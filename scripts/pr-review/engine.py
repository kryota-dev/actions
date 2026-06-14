#!/usr/bin/env python3
"""PR review engine (shared by claude-pr-review.yml and codex-pr-review.yml).

Subcommands:
  annotate <raw.diff> <annotated.txt> <positions.json>
      Annotate a unified diff with absolute line numbers (so agents cite real
      lines) and emit the valid inline-comment position set. Honors PATHS /
      EXCLUDE_PATHS env globs.
  post
      Turn the agent findings JSON into a review payload + summary, applying
      diff-line validation (demote non-mappable to body-only) and the mechanical
      dedup guard (semantic dedup is the agent's job). Also computes the hybrid
      auto-resolve set (mechanically-stale prior threads the reviewer judged
      addressed). Env-driven; never crashes on malformed findings (soft-fail).
      Writes review_payload.json, summary_body.md, resolve_thread_ids.json,
      meta.json into OUT_DIR.

Pure stdlib (python3).
"""
import fnmatch
import json
import os
import re
import sys

# ---------------------------------------------------------------- annotate ----
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def _globs(name):
    raw = os.environ.get(name, "")
    return [g.strip() for g in re.split(r"[,\n]", raw) if g.strip()]


def _included(path, includes, excludes):
    if path is None:
        return False
    if includes and not any(fnmatch.fnmatch(path, g) for g in includes):
        return False
    if any(fnmatch.fnmatch(path, g) for g in excludes):
        return False
    return True


def _strip_prefix(p):
    return p[2:] if p.startswith(("a/", "b/")) else p


def parse_diff(diff_text, includes=None, excludes=None):
    includes = includes or []
    excludes = excludes or []
    positions = {}
    lines_out = []
    path = None
    old_no = new_no = 0
    in_hunk = False
    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            in_hunk = False
            path = None
            continue
        if line.startswith("--- "):
            continue
        if line.startswith("+++ "):
            raw = line[4:].strip()
            path = None if raw == "/dev/null" else _strip_prefix(raw)
            if path is not None and not _included(path, includes, excludes):
                path = None
            if path is not None:
                positions.setdefault(path, {"RIGHT": [], "LEFT": []})
                lines_out.append(f"### {path}")
            continue
        m = HUNK_RE.match(line)
        if m:
            old_no = int(m.group(1))
            new_no = int(m.group(2))
            in_hunk = True
            lines_out.append(line)
            continue
        if not in_hunk or path is None:
            continue
        if line.startswith("+"):
            positions[path]["RIGHT"].append(new_no)
            lines_out.append(f"R{new_no}: +{line[1:]}")
            new_no += 1
        elif line.startswith("-"):
            positions[path]["LEFT"].append(old_no)
            lines_out.append(f"L{old_no}: -{line[1:]}")
            old_no += 1
        elif line.startswith(" "):
            positions[path]["RIGHT"].append(new_no)
            positions[path]["LEFT"].append(old_no)
            lines_out.append(f"R{new_no}:  {line[1:]}")
            old_no += 1
            new_no += 1
        elif line.startswith("\\"):
            continue
    return positions, "\n".join(lines_out) + "\n"


def cmd_annotate(argv):
    raw_path, out_path, pos_path = argv[0], argv[1], argv[2]
    with open(raw_path, encoding="utf-8") as f:
        diff_text = f.read()
    positions, annotated = parse_diff(diff_text, _globs("PATHS"), _globs("EXCLUDE_PATHS"))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(annotated)
    with open(pos_path, "w", encoding="utf-8") as f:
        json.dump(positions, f, ensure_ascii=False, indent=2)


# -------------------------------------------------------------------- post ----
SOURCE_RE = re.compile(r"<!--\s*review-source:\s*(.*?)\s*-->")
EMOJI = {"critical": "\U0001F534", "warning": "\U0001F7E1", "suggestion": "\U0001F7E2"}
INLINE_SEVERITIES = {"critical", "warning"}
DEDUP_LINE_TOLERANCE = 3


def _env(name, default=""):
    return os.environ.get(name, default)


def _load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _extract_sources(body):
    out = set()
    for m in SOURCE_RE.findall(body or ""):
        out.update(t.strip() for t in m.split(",") if t.strip())
    return out


def _is_mappable(positions, path, side, line):
    if line is None:
        return False
    return line in set(positions.get(path, {}).get(side, []))


def _dedup_hit(finding, sources, existing):
    if finding.get("line") is None:
        return False
    for c in existing:
        if c.get("path") != finding["path"]:
            continue
        if (c.get("side") or "RIGHT") != finding["side"]:
            continue
        cl = c.get("line")
        if cl is None:
            continue
        if abs(cl - finding["line"]) > DEDUP_LINE_TOLERANCE:
            continue
        if sources & _extract_sources(c.get("body", "")):
            return True
    return False


def _to_int(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value == int(value) else None
    if isinstance(value, str):
        return int(value) if value.strip().isdigit() else None
    return None


def _thread_is_ours(thread, marker):
    nodes = thread.get("comments") or []
    first = nodes[0] if nodes and isinstance(nodes[0], dict) else {}
    author = first.get("author") or ""
    # Require BOTH the marker and a bot author on the FIRST comment. A human login
    # can never end with "[bot]", so a user who quotes our (HTML-comment) marker
    # cannot get their own thread classified as ours and silently auto-resolved.
    return marker in (first.get("body") or "") and author.endswith("[bot]")


def _resolve_targets(prior_threads, agent_resolved, marker):
    """Hybrid resolve set: threads that pass BOTH the mechanical gate (ours, open,
    outdated, resolvable, line-anchored) AND the reviewer's "addressed" judgment.

    The agent references a thread by the integer ``comment_id`` (its first comment's
    databaseId). We validate that handle against the mechanical map, so a garbled or
    hallucinated handle is a safe no-op (under-resolve, never wrong-resolve).
    """
    if not marker:
        return []
    mechanical = {}
    for t in prior_threads:
        if not isinstance(t, dict):
            continue
        if t.get("isResolved"):
            continue
        if not t.get("isOutdated"):
            continue
        if not t.get("viewerCanResolve"):
            continue
        if t.get("subjectType") not in (None, "LINE"):
            continue
        if not _thread_is_ours(t, marker):
            continue
        cid = _to_int(t.get("comment_id"))
        tid = t.get("id")
        if cid is not None and tid:
            mechanical[cid] = tid
    ids = []
    for r in agent_resolved:
        if not isinstance(r, dict):
            continue
        cid = _to_int(r.get("comment_id"))
        if cid is not None and cid in mechanical and mechanical[cid] not in ids:
            ids.append(mechanical[cid])
    return ids


def _sign(text, signature):
    return f"{text}\n\n---\n*{signature}*" if signature else text


def _short(text, n=140):
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    text = text.replace("\n", " ").strip()
    return text if len(text) <= n else text[: n - 1] + "…"


def _cell(text):
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    return text.replace("\n", " ").replace("|", "\\|").strip()


def _build_body_table(findings, rejected, agent_failures):
    counts = {k: 0 for k in EMOJI}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    header = (f"## \U0001F916 PR Review — Findings "
              f"({EMOJI['critical']}{counts['critical']} "
              f"{EMOJI['warning']}{counts['warning']} "
              f"{EMOJI['suggestion']}{counts['suggestion']})")
    lines = [header, ""]
    if findings:
        lines += ["| # | severity | source | location | problem | suggestion |",
                  "|---|---|---|---|---|---|"]
        for i, f in enumerate(findings, 1):
            loc = f["path"] + (f":{f['line']}" if f.get("line") else "")
            lines.append(
                f"| {i} | {EMOJI.get(f['severity'], '')} {f['severity']} | "
                f"{_cell(','.join(f.get('source', [])))} | {_cell(loc)} | "
                f"{_cell(_short(f.get('problem')))} | {_cell(_short(f.get('suggestion')))} |")
    else:
        lines.append("> No findings.")
    if rejected:
        lines += ["", f"<details><summary>Rejected findings ({len(rejected)})</summary>", ""]
        for r in rejected:
            loc = r.get("path", "") + (f":{r['line']}" if r.get("line") else "")
            lines.append(f"- {_cell(loc)} — {_cell(r.get('reason'))}")
        lines += ["", "</details>"]
    for af in agent_failures:
        lines.append(f"\n\U0001F6A8 Agent failure report: {_cell(af)}")
    return "\n".join(lines)


def _build_summary(summary, marker, counts):
    s = summary or {}
    lines = [marker, "", "## \U0001F916 PR Review Summary"]
    if s.get("overview"):
        lines += ["", f"> {_cell(s['overview'])}"]
    meta_rows = [(k, s[k]) for k in ("type", "scope", "impact", "size") if s.get(k)]
    if meta_rows:
        lines += ["", "| | |", "|---|---|"]
        for k, v in meta_rows:
            lines.append(f"| **{k}** | {_cell(v)} |")
    if s.get("key_changes"):
        lines += ["", "### Key changes", ""]
        for kc in s["key_changes"]:
            lines.append(f"- `{_cell(kc.get('path'))}` ({kc.get('status', '')}) {_cell(kc.get('note'))}")
    lines += ["", "---",
              (f"Findings: {EMOJI['critical']}{counts['critical']} "
               f"{EMOJI['warning']}{counts['warning']} "
               f"{EMOJI['suggestion']}{counts['suggestion']} "
               "— see the review for details.")]
    for af in s.get("agent_failures", []):
        lines.append(f"\U0001F6A8 Agent failure report: {_cell(af)}")
    return "\n".join(lines)


def cmd_post():
    out_dir = _env("OUT_DIR", ".")
    marker = _env("MARKER", "<!-- pr-review -->")
    signature = _env("SIGNATURE")
    submit = _env("SUBMIT", "true").lower() == "true"
    review_event = _env("REVIEW_EVENT", "COMMENT")
    resolve_addressed = _env("RESOLVE_ADDRESSED", "true").lower() == "true"

    positions = _load_json(_env("POSITIONS_JSON"), {})
    prior = _load_json(_env("PRIOR_REVIEWS_JSON"), {})
    prior_inline = prior.get("inline", []) if isinstance(prior, dict) else []
    prior_threads = prior.get("threads", []) if isinstance(prior, dict) else []

    raw = _load_json(_env("FINDINGS_JSON"), None)
    status = "ok"
    if not isinstance(raw, dict):
        status = "parse-error"
        raw = {}

    summary = raw.get("summary", {}) if isinstance(raw.get("summary"), dict) else {}
    findings = [f for f in raw.get("findings", []) if isinstance(f, dict)]
    rejected = [r for r in raw.get("rejected", []) if isinstance(r, dict)]
    agent_resolved = [r for r in raw.get("resolved", []) if isinstance(r, dict)]

    norm = []
    demoted = 0
    for f in findings:
        sev = f.get("severity")
        if sev not in EMOJI:
            sev = "suggestion"
        side = f.get("side") or "RIGHT"
        side = side if side in ("RIGHT", "LEFT") else "RIGHT"
        line = f.get("line")
        if isinstance(line, bool):
            line = None  # bool is an int subclass; never a valid line
        elif isinstance(line, float):
            line = int(line) if line == int(line) else None
        elif isinstance(line, str):
            line = int(line) if line.strip().isdigit() else None
        elif not isinstance(line, int):
            line = None
        if line is not None and not _is_mappable(positions, f.get("path", ""), side, line):
            demoted += 1
            line = None
        norm.append({"severity": sev, "path": f.get("path", ""), "line": line,
                     "side": side, "start_line": f.get("start_line"),
                     "source": f.get("source", []) if isinstance(f.get("source"), list) else [],
                     "category": f.get("category", ""), "problem": f.get("problem", ""),
                     "suggestion": f.get("suggestion", "")})

    counts = {k: 0 for k in EMOJI}
    for f in norm:
        counts[f["severity"]] += 1

    comments = []
    self_posted = []
    deduped = 0
    for f in norm:
        if f["severity"] not in INLINE_SEVERITIES or f["line"] is None:
            continue
        sources = set(f["source"])
        if _dedup_hit(f, sources, prior_inline) or _dedup_hit(f, sources, self_posted):
            deduped += 1
            continue
        tag = ("<!-- review-source: " + ",".join(f["source"]) + " -->") if f["source"] else ""
        body = f"{EMOJI[f['severity']]} **{f['severity']}**: {f['problem']}\n\n{f['suggestion']}"
        if tag:
            body += f"\n\n{tag}"
        if marker:
            body += f"\n\n{marker}"  # self-identify the thread for later auto-resolve
        comment = {"path": f["path"], "line": f["line"], "side": f["side"],
                   "body": _sign(body, signature)}
        if f.get("start_line") and f["start_line"] != f["line"]:
            comment["start_line"] = f["start_line"]
            comment["start_side"] = f["side"]
        comments.append(comment)
        self_posted.append({"path": f["path"], "side": f["side"], "line": f["line"],
                            "body": comment["body"]})

    post_review = bool(norm) or status == "parse-error"
    body_md = _build_body_table(norm, rejected, summary.get("agent_failures", []))
    if status == "parse-error":
        body_md = ("## \U0001F916 PR Review — Findings\n\n"
                   "\U0001F6A8 Agent failure report: the reviewer did not return valid "
                   "findings JSON; nothing could be posted inline.")
        comments = []
    payload = {"body": _sign(body_md, signature), "comments": comments}
    if submit:
        payload["event"] = review_event

    resolve_ids = (_resolve_targets(prior_threads, agent_resolved, marker)
                   if status == "ok" and resolve_addressed else [])

    with open(os.path.join(out_dir, "review_payload.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    with open(os.path.join(out_dir, "summary_body.md"), "w", encoding="utf-8") as fh:
        fh.write(_build_summary(summary, marker, counts) + "\n")
    with open(os.path.join(out_dir, "resolve_thread_ids.json"), "w", encoding="utf-8") as fh:
        json.dump(resolve_ids, fh, ensure_ascii=False)
    meta = {"status": status, "post_review": post_review, "counts": counts,
            "inline": len(comments), "deduped": deduped, "demoted": demoted,
            "rejected": len(rejected), "resolve": len(resolve_ids)}
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False)
    print(json.dumps(meta, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: engine.py <annotate|post> [args]")
    cmd = sys.argv[1]
    if cmd == "annotate":
        cmd_annotate(sys.argv[2:])
    elif cmd == "post":
        cmd_post()
    else:
        sys.exit(f"unknown subcommand: {cmd}")


if __name__ == "__main__":
    main()
