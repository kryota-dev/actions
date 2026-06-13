# PR review engine

Shared implementation behind the public review workflows
[`claude-pr-review.yml`](../../.github/workflows/claude-pr-review.yml) and
[`codex-pr-review.yml`](../../.github/workflows/codex-pr-review.yml).

The agent only **generates** findings; everything in this directory is the
**deterministic** half that annotates the diff, validates inline line mapping,
de-duplicates mechanically, and builds the review/summary payloads.

## Files

| Path | Role |
|------|------|
| `engine.py` | Source of truth for the engine. Subcommands `annotate` and `post`. Pure stdlib. |
| `embed.py` | Re-embeds `engine.py` + `blocks/*` into the workflow YAML heredocs. Idempotent. |
| `blocks/findings.schema.json` | Output contract (used as Claude `--json-schema` reference and Codex `--output-schema`). |
| `blocks/review-rules.md` | SSOT for severity / validity / what-to-flag / dedup / source-tag rules. |
| `blocks/role-catalog.md` | SSOT for Claude's reviewer-role catalog (role × trigger × responsibility). |
| `blocks/review-rules.ja.md`, `blocks/role-catalog.ja.md` | Japanese reference translations. **Not embedded**; documentation only. |

## How the embed works

Each workflow writes a runtime copy of a source via a quoted heredoc whose body
is owned by `embed.py`:

```bash
cat > "$WORK/engine.py" <<'ENGINE_PY'
ENGINE_PY
```

`embed.py` fills the body between each `<<'DELIM'` opening line and its closing
`DELIM` line, re-indented to the opening line's column. No markers are left in
the generated files, so embedded JSON/Markdown stays valid.

| Delimiter | Source |
|-----------|--------|
| `ENGINE_PY` | `engine.py` |
| `SCHEMA_JSON` | `blocks/findings.schema.json` |
| `RULES_MD` | `blocks/review-rules.md` |
| `CATALOG_MD` | `blocks/role-catalog.md` (Claude only; absent in the Codex workflow) |

This embedding (rather than a self-checkout or a local composite action) is
required because a Reusable Workflow cannot version-consistently load its own
repository's files — the `github` context and `./` paths resolve to the caller
(see `docs/adr/006-add-claude-and-codex-pr-review-reusable-workflows.md`).

## Maintenance flow

Always edit the **source** here, never the embedded copy inside the workflow YAML.

```bash
# 1. Edit the source
#    scripts/pr-review/engine.py  or  scripts/pr-review/blocks/*

# 2. Re-embed into both workflows (idempotent)
python3 scripts/pr-review/embed.py

# 3. Lint (the same gates CI runs)
aqua exec -- actionlint .github/workflows/claude-pr-review.yml .github/workflows/codex-pr-review.yml
aqua exec -- ghalint run
aqua exec -- zizmor --format github .

# 4. Compile-check the engine
python3 -m py_compile scripts/pr-review/engine.py
```

When editing a `*.md` / `*.json` prompt block, also keep the Japanese reference
translation (`*.ja.md`) in sync if the change is substantive.

## Engine subcommands

```bash
# annotate: unified diff -> annotated diff (absolute line numbers) + valid inline positions
#   Honors PATHS / EXCLUDE_PATHS env globs.
python3 engine.py annotate raw.diff annotated_diff.txt positions.json

# post: findings JSON -> review_payload.json + summary_body.md + meta.json
#   Env: FINDINGS_JSON, POSITIONS_JSON, PRIOR_REVIEWS_JSON, OUT_DIR,
#        MARKER, SIGNATURE, SUBMIT, REVIEW_EVENT
#   Defensive: never crashes on malformed findings (soft-fail -> meta.status="parse-error").
python3 engine.py post
```

## Local smoke test

`engine.py` is pure stdlib, so its logic can be exercised offline with fixtures:

```bash
tmp=$(mktemp -d)
printf 'diff --git a/x.ts b/x.ts\n--- a/x.ts\n+++ b/x.ts\n@@ -1,1 +1,2 @@\n a\n+b\n' > "$tmp/raw.diff"
python3 engine.py annotate "$tmp/raw.diff" "$tmp/annotated.txt" "$tmp/positions.json"
printf '{"summary":{"overview":"","type":"","scope":"","impact":"","size":"","key_changes":[],"agent_failures":[]},"findings":[{"severity":"warning","path":"x.ts","line":2,"side":"RIGHT","start_line":null,"source":["test"],"category":"","rule":"","problem":"p","suggestion":"s"}],"rejected":[]}' > "$tmp/findings.json"
OUT_DIR="$tmp" POSITIONS_JSON="$tmp/positions.json" PRIOR_REVIEWS_JSON=/dev/null \
  FINDINGS_JSON="$tmp/findings.json" MARKER="<!-- test -->" SIGNATURE="test" \
  SUBMIT=true REVIEW_EVENT=COMMENT python3 engine.py post
cat "$tmp/meta.json"   # -> {"status":"ok","post_review":true,"inline":1,...}
```
