**English** | [日本語](README.ja.md)

# Reusable Workflows

## Quality Gates

| Workflow | Description |
|----------|-------------|
| [actions-lint](docs/actions-lint.md) | GitHub Actions quality gate (actionlint / ls-lint / ghalint / zizmor) |
| [codeql-analysis](docs/codeql-analysis.md) | CodeQL security scanning |

## PR Management

| Workflow | Description |
|----------|-------------|
| [auto-assign-pr](docs/auto-assign-pr.md) | Auto-assign PR creator as assignee |

## Release

| Workflow | Description |
|----------|-------------|
| [tagpr-release](docs/tagpr-release.md) | tagpr release management and major tag update |

## Deploy

| Workflow | Description |
|----------|-------------|
| [deploy-web-hosting](docs/deploy-web-hosting.md) | Deploy to web hosting server via FTP / rsync |
| [undeploy-web-hosting](docs/undeploy-web-hosting.md) | Remove feature environment from web hosting server via FTP / rsync |

## Usage

To call a Reusable Workflow from another repository:

```yaml
jobs:
  example:
    uses: kryota-dev/actions/.github/workflows/{workflow}.yml@v0
    with:
      # inputs
    secrets:
      # secrets
```

See the linked documentation above for details on each workflow's inputs / secrets / permissions.

## Internal CI Workflows

Internal CI workflows (with `my-` prefix) used for quality management of this repository itself. They are implemented as thin wrappers that call the Reusable Workflows via `uses:`.

| Workflow | Trigger | Calls | Description |
|----------|---------|-------|-------------|
| my-test.yml | PR, merge_group | actions-lint.yml | Quality gate |
| my-setup-pr.yml | PR opened | auto-assign-pr.yml | Auto assignee |
| my-release.yml | push (main) | tagpr-release.yml | Release management |
| my-codeql.yml | PR, push (main), merge_group | codeql-analysis.yml | Security scanning |
