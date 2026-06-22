# 7. Apply repository-managed htaccess on production deploys via opt-in

Date: 2026-06-22

## Status

2026-06-22 accepted

## Context

On production deploys (`is-production=true`), both `deploy-web-hosting-rsync` and
`deploy-web-hosting-ftp` excluded `.htaccess` (and `_feature/`) from the mirror.
The exclusion was implemented with rsync `--exclude-from` and lftp `-x`, which
suppress **both** the deletion **and** the transfer of the matching files.

The original intent (per the action comment "Excluding .htaccess ... from
deletion") was only to protect the server's existing `.htaccess` from `--delete`.
But because the exclude also suppresses the transfer, a repository-managed
`.htaccess` contained in the build artifact (`public/.htaccess` → `out/.htaccess`)
can never reach production through CI. Redirect rules and the custom 404 page
(`ErrorDocument 404`) therefore had to be edited manually on the server, so the
repository could not act as the source of truth (real-world impact:
`kryota-devs/meitobari-homepage` #490 redirect and #496 custom 404).

Backward compatibility is mandatory: consumers that manage `.htaccess` manually
on the server must not have their server-side file overwritten or deleted by an
upgrade of these actions.

Alternatives considered and rejected as defaults:

- **Always transfer `.htaccess`** — breaks existing consumers who manage it
  manually. Not acceptable.
- **Switch to a deletion-protect-only filter as the default** — would still
  overwrite the server's `.htaccess` for existing consumers whose artifact
  happens to contain one. Not backward compatible on its own.

## Decision

Add an opt-in string input `apply-htaccess` (default `'false'`) to both actions
and thread it through the `deploy-web-hosting.yml` Reusable Workflow so both
direct-action and workflow consumers can reach it. It is only effective when
`is-production` is `'true'` (no-op on preview deploys). `_feature/` deletion
protection remains unconditional.

Semantics when `apply-htaccess='true'` on production: **transfer the artifact's
`.htaccess`, but never delete the server's copy** (a "protect" semantics rather
than "treat as a normal file"). If a given artifact has no `.htaccess`, the
server's copy is preserved instead of being deleted.

Implementation per transport (symmetric two-pass on both):

- **rsync**: pass 1 mirrors with `--delete` while excluding `.htaccess` and
  `_feature/` via `--exclude-from`, so the server copies are never transferred or
  deleted. Pass 2 runs only when `apply-htaccess='true'` and the artifact
  actually contains a `.htaccess`, applying it via a separate `rsync` without
  `--delete`. An explicit second transfer is used rather than rsync's `protect`
  (`P`) filter rule because whether a protected file is also *transferred* is
  implementation-dependent (e.g. openrsync suppresses the transfer), which would
  make the opt-in silently no-op on some rsync builds. `RSYNC_OPTS` is refactored
  from an unquoted string into a bash array for safe argument passing.
- **lftp**: `mirror` has no protect-only filter (its `-x` excludes from both
  transfer and deletion), so the same two-pass shape is used. Pass 1 mirrors with
  `.htaccess` and `_feature/` excluded (server copies never deleted). Pass 2 runs
  only when `apply-htaccess='true'` and the artifact actually contains a
  `.htaccess`, uploading it explicitly via `put`. `set cmd:fail-exit yes` makes a
  failed `put` surface as a non-zero exit instead of a silent success. This also
  fixes a prior bug where the two exclude patterns shared a single `-x` flag,
  leaving `_feature/` misinterpreted as a mirror positional argument.

A single boolean opt-in was chosen over a more general "protect/transfer pattern
list" input to minimize consumer cognitive load and keep the backward-compatible
default unambiguous.

## Consequences

- Existing consumers are unaffected: the default (`apply-htaccess` omitted or
  `'false'`) keeps the current exclude behavior, and the server's `.htaccess` is
  never touched.
- Opt-in consumers can manage `.htaccess` (redirects, `ErrorDocument 404`, etc.)
  in the repository as the source of truth and deliver it to production through
  CI.
- rsync and lftp now share an equivalent, symmetric two-pass shape ("mirror with
  the file excluded, then explicitly transfer it when opted in"), giving the same
  "transfer + delete-protect" semantics on both transports. The trade-off is one
  extra connection pass on opt-in production deploys.
- The rsync `RSYNC_OPTS` array refactor, the lftp `_feature/` exclude fix, and
  `cmd:fail-exit` are incidental robustness improvements that ship with this
  change.
- Because the Reusable Workflow pins the actions to the previous release SHA,
  `apply-htaccess` passed via `deploy-web-hosting.yml` is a no-op until Renovate
  bumps the pin to the release that defines the input; direct action consumers on
  `@v0` get it immediately via the major-tag update.
- A future generalization (arbitrary protect/transfer pattern lists) is left open
  but intentionally out of scope.

