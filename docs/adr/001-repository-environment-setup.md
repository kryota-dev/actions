# 1. Repository environment setup

Date: 2026-02-21

## Status

2026-02-21 accepted

## Context

This repository (`kryota-dev/actions`) manages reusable GitHub Actions workflows.
To ensure quality, security, and maintainability, a CI/CD pipeline and supporting toolchain are required.

The following tools and configurations have been evaluated:

- **ls-lint**: File naming convention enforcement for workflow files (snake_case)
- **actionlint**: GitHub Actions workflow syntax checking
- **ghalint**: Security policy compliance checking (SHA pinning, permissions)
- **zizmor**: Static security analysis (template injection, supply chain risks)
- **tagpr**: Automated semantic versioning and release management
- **Renovate Bot**: Automated dependency updates with SHA pinning
- **CodeQL**: Continuous security scanning
- **adr (npm)**: Architecture Decision Records management

## Decision

Adopt the following baseline environment:

1. **Workflow linting**: ls-lint + actionlint + ghalint + zizmor via `my_test.yml`
2. **Release management**: tagpr with PAT (`APP_TOKEN`) via `my_release.yml`
3. **Dependency management**: Renovate Bot with `helpers:pinGitHubActionDigests` preset
4. **Security scanning**: CodeQL via `my_codeql.yml`
5. **ADR management**: adr npm package with `docs/adr/` as the storage path
6. **SHA pinning policy**: All `uses:` references must use full 40-character commit SHA

## Consequences

- All workflow files must follow snake_case naming convention
- All external Actions must be pinned to full commit SHA (enforced by ghalint and zizmor)
- Releases are fully automated via tagpr; manual tagging is not required
- Design decisions will be documented as ADRs in `docs/adr/`
- Renovate Bot must be installed as a GitHub App (manual setup required)
- `APP_TOKEN` (PAT) must be configured as a repository secret (manual setup required)
