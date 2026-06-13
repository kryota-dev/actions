#!/usr/bin/env python3
"""Embed shared PR-review sources into the workflow YAML heredocs.

Embedded content (engine, JSON schema, prompt blocks) is kept as standalone,
properly-formatted source files under scripts/pr-review/. Each workflow writes a
runtime copy via a quoted heredoc whose body is owned by this tool:

    cat > "$WORK/engine.py" <<'ENGINE_PY'
    ENGINE_PY

`embed.py` fills the body between each `<<'DELIM'` opening line and its closing
`DELIM` line with the mapped source file, re-indented to the opening line's
column. No markers are left in the generated files (the heredoc delimiter is the
boundary), so embedded JSON/Markdown stays valid. Idempotent. Run after editing
any source:

    python3 scripts/pr-review/embed.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "scripts" / "pr-review"

# heredoc delimiter -> source file
DELIMS = {
    "ENGINE_PY": SRC / "engine.py",
    "SCHEMA_JSON": SRC / "blocks" / "findings.schema.json",
    "RULES_MD": SRC / "blocks" / "review-rules.md",
    "CATALOG_MD": SRC / "blocks" / "role-catalog.md",
}
TARGETS = [
    ROOT / ".github" / "workflows" / "claude-pr-review.yml",
    ROOT / ".github" / "workflows" / "codex-pr-review.yml",
]


def fill(text: str, delim: str, content: str) -> str:
    open_token = f"<<'{delim}'"
    body = content.rstrip("\n").split("\n")
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    replaced = False
    while i < len(lines):
        line = lines[i]
        out.append(line)
        if open_token in line:
            indent = line[: len(line) - len(line.lstrip())]
            j = i + 1
            while j < len(lines) and lines[j].strip() != delim:
                j += 1
            if j >= len(lines):
                raise SystemExit(f"{delim}: closing delimiter not found")
            for el in body:
                out.append((indent + el) if el.strip() else "")
            out.append(lines[j])  # closing delimiter line, preserved
            i = j + 1
            replaced = True
            continue
        i += 1
    return "\n".join(out) if replaced else text


def main() -> int:
    contents = {d: p.read_text(encoding="utf-8") for d, p in DELIMS.items()}
    for target in TARGETS:
        text = target.read_text(encoding="utf-8")
        for delim, content in contents.items():
            text = fill(text, delim, content)
        target.write_text(text, encoding="utf-8")
        print(f"embedded into {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
