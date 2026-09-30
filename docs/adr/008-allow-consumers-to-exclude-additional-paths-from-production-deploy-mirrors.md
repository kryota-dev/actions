# 8. Allow consumers to exclude additional paths from production deploy mirrors

Date: 2026-09-28

## Status

2026-09-28 accepted

## Context

On production deploys, `deploy-web-hosting-rsync` and `deploy-web-hosting-ftp`
mirror the build artifact into the target root with deletion enabled
(`rsync --delete` / `lftp mirror --reverse --delete`). Anything on the server
that is not in the artifact is deleted, except for the two hard-coded
exclusions `.htaccess` and `_feature/`.

Shared web hosting plans often force another site (for example an additional
domain running a CMS) to live in a subdirectory of the same document root. With
the current actions, the next production deploy of the primary site deletes that
subdirectory. Production deploys may also be triggered automatically (e.g. by a
CMS webhook), so the deletion can happen without any code change.

ADR 7 explicitly left "arbitrary protect/transfer pattern lists" out of scope to
keep the `.htaccess` opt-in simple. The problem here is different: the paths are
consumer-specific and cannot be hard-coded in a shared action.

Alternatives considered:

- **Hard-code more paths in the actions** — does not scale, and leaks consumer
  specifics into a public shared action.
- **Accept raw rsync filter rules / lftp regexes** — exposes two different
  pattern languages through one input, makes the rsync and FTP behavior diverge,
  and opens an injection surface into the lftp command string.
- **Use rsync's protect (`P`) rule** — only covers rsync, and ADR 7 already
  found its transfer semantics implementation-dependent.

## Decision

Add an optional string input `exclude-paths` (default `''`) to both actions and
thread it through the `deploy-web-hosting.yml` Reusable Workflow.

- The value is a newline-separated list of **plain paths relative to the target
  root**, not patterns. Blank lines are ignored; surrounding whitespace and a
  leading `/` are stripped.
- Each entry must consist of `[A-Za-z0-9._-]` segments separated by `/`, with an
  optional trailing `/` meaning "directory only". `.` and `..` segments are
  rejected. Invalid entries fail the step before any transfer, in every mode.
  The conservative character set lets both transports embed the entries without
  a general escaping layer and closes the lftp command-injection surface.
- Like the built-in exclusions, the entries are only applied on production
  deploys (`is-production: 'true'`). Preview deploys target a per-branch
  subdirectory where consumer content does not live.
- Both transports anchor the entries at the target root and exclude them from
  **both transfer and deletion**, matching the existing `.htaccess` /
  `_feature/` semantics:
  - **rsync**: each entry is appended to the existing `--exclude-from` file with
    a leading `/`, because an unanchored rsync pattern matches at any depth.
  - **lftp**: each entry becomes an extra `-x` regex `^<entry>` with `.`
    escaped. Entries without a trailing `/` get `(/|$)` so they match the file
    or directory of that name but not a longer sibling name.

## Consequences

- Consumers can keep other content under the production target root safe from
  deletion without forking the actions. The default (`''`) keeps the current
  behavior, so existing consumers are unaffected.
- Paths containing characters outside the allowed set (spaces, wildcards, etc.)
  cannot be excluded. This is intentional; the set can be widened later if a
  real need appears, together with proper escaping per transport.
- Artifact content under an excluded path is never uploaded on production, so
  the consumer must not ship files there.
- As with ADR 7, the Reusable Workflow pins the actions to a release SHA, so
  `exclude-paths` passed via `deploy-web-hosting.yml` only takes effect once the
  internal pins are bumped to a release that defines the input.
