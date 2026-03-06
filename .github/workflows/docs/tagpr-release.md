**English** | [日本語](tagpr-release.ja.md)

# tagpr Release

Release management and major tag update workflow using tagpr

> Source: [`.github/workflows/tagpr-release.yml`](../tagpr-release.yml)

## Usage

```yaml
jobs:
  release:
    permissions:
      contents: write
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/tagpr-release.yml@v0
    secrets:
      # app-token - Personal Access Token for tagpr (requires 'repo' and 'workflow' scopes)
      # Required
      app-token: ${{ secrets.APP_TOKEN }}
```

## Inputs

None

## Secrets

| Name | Description | Required |
|------|-------------|----------|
| `app-token` | Personal Access Token for tagpr (requires `repo` and `workflow` scopes) | Yes |

## Outputs

| Name | Description |
|------|-------------|
| `tag` | Version tag created by tagpr (empty if no release) |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `contents` | `write` | Tag creation/push by tagpr and force-updating major tags |
| `pull-requests` | `write` | Creating/updating release PRs by tagpr |

## Examples

### Basic Usage

```yaml
jobs:
  release:
    permissions:
      contents: write
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/tagpr-release.yml@v0
    secrets:
      app-token: ${{ secrets.APP_TOKEN }}
```

### Running follow-up jobs after release

```yaml
jobs:
  release:
    permissions:
      contents: write
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/tagpr-release.yml@v0
    secrets:
      app-token: ${{ secrets.APP_TOKEN }}

  post-release:
    needs: release
    if: needs.release.outputs.tag != ''
    runs-on: ubuntu-latest
    steps:
      - run: echo "Released ${{ needs.release.outputs.tag }}"
```

## Behavior

This workflow consists of two jobs: `tagpr` and `bump_major_tag`.

**Concurrency**: `group: {workflow}-release` / `cancel-in-progress: false`

### tagpr Job

1. Check out the repository with `actions/checkout@v6` (token: `app-token`, `persist-credentials: false`)
2. Run `Songmu/tagpr@v1.17.1` to create/merge release PRs and tag releases (`GITHUB_TOKEN: app-token`)
3. If a release is made, output the version tag as the `tag` output (empty if no release)

### bump_major_tag Job

Runs only after the `tagpr` job completes and a tag was created (`tag != ''`).

1. Check out the repository with `actions/checkout@v6` (token: `app-token`, `persist-credentials: false`)
2. Extract the major version from the tag (e.g., `v1.2.3` → `v1`)
3. Update the major tag with `git tag -f` and push to remote with `git push --force`

## Prerequisites

- GitHub App Token or Personal Access Token (requires `repo` + `workflow` scopes)
- `.tagpr` configuration file must exist in the repository
