# 5. Replace adr npm package with bash script

Date: 2026-03-05

## Status

2026-03-05 accepted

## Context

Multiple Dependabot security alerts have been reported for the `adr@1.5.2` npm package and its transitive dependencies:

1. **sharp@0.30.7** (high severity, CVSS 7.8): libwebp CVE-2023-4863
2. **lodash.template@4.5.0** (high severity, CVSS 7.2): Command Injection vulnerability
3. **tmp@0.0.33** (low severity, CVSS 2.5): Arbitrary file write via symlink

The `adr` package (version 1.5.2) is the final release and maintenance has been discontinued. Upstream fixes are not expected, and vulnerabilities will continue to accumulate.

### Risk Assessment

- All vulnerabilities are in `devDependencies` used only for local ADR creation
- No runtime or CI/CD impact (the package is not used in workflows)
- Attack vector is limited to local development environments with trusted input
- However, maintaining known vulnerabilities contradicts security best practices

### Alternatives Evaluated

1. **Continue using `adr@1.5.2`**: Not acceptable due to accumulating vulnerabilities
2. **Migrate to log4brains**: Full-featured ADR tool with GUI, but overly complex for our needs
3. **Migrate to adr-tools (Bash)**: Mature Bash-based tool, but requires external installation
4. **Custom Bash script**: Minimal, maintainable, zero external dependencies

## Decision

Replace the `adr` npm package with a custom Bash script (`scripts/adr-new.sh`) that:

1. Generates ADR files with the same format as the existing `adr` tool
2. Automatically assigns sequential ADR numbers
3. Updates `docs/adr/README.md` with new entries
4. Has zero external dependencies
5. Is maintained within this repository

The script provides only the essential functionality needed (creating new ADRs), eliminating:
- Unused features (compress, export, search, etc.)
- 196 transitive npm dependencies
- All associated security vulnerabilities

## Consequences

### Positive

- All 9 npm audit vulnerabilities are eliminated
- No external dependencies to maintain or monitor for vulnerabilities
- Simpler, more transparent implementation (60 lines of Bash vs. complex npm dependency tree)
- Faster execution (no npm package loading overhead)
- Easy to customize for repository-specific needs

### Negative

- Loss of advanced features (export to HTML/CSV/JSON, image compression, keyword search)
  - Mitigation: These features were never used in this repository
- Manual maintenance required for script updates
  - Mitigation: The script is simple and unlikely to require changes

### Migration Impact

- Update `package.json`: Change `adr:new` script to call `bash scripts/adr-new.sh`
- Update documentation: AGENTS.md, README.md
- All existing ADR files remain compatible (no format changes)
- Developers use `npm run adr:new -- "Title"` as before (same interface)
