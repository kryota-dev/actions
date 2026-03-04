**English** | [日本語](compute-web-hosting-deploy-path.ja.md)

# compute-web-hosting-deploy-path

A Composite Action that computes the deploy path and production flag from GitHub context and inputs.

> Source: [`.github/actions/compute-web-hosting-deploy-path/action.yml`](../compute-web-hosting-deploy-path/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/compute-web-hosting-deploy-path@v1
  with:
    # base-path-prefix - Project-specific path prefix (e.g., /<your-project>)
    # Optional (default: '')
    base-path-prefix: ''

    # production-branch - Production branch name
    # Optional (default: 'main')
    production-branch: 'main'

    # ref-name - Branch name override (auto-derived from github context if empty)
    # Optional (default: '')
    ref-name: ''
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `base-path-prefix` | Project-specific path prefix (e.g., /&lt;your-project&gt;) | No | `''` |
| `production-branch` | Production branch name | No | `'main'` |
| `ref-name` | Branch name override (auto-derived from github context if empty) | No | `''` |

## Outputs

| Name | Description | Example |
|------|-------------|---------|
| `deploy-path` | Full deploy path | `/my-project` (main branch), `/my-project/_feature/feat-awesome` (feature branch `feat/awesome`) |
| `is-production` | Whether this is a production deploy | `true` or `false` |
| `ref-name` | Resolved ref name (derived or overridden) | `main`, `feat/awesome` |

## Examples

### Basic Usage

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/compute-web-hosting-deploy-path@v1
    id: compute-path
    with:
      base-path-prefix: '/my-project'
```

### Customize Production Branch Name

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/compute-web-hosting-deploy-path@v1
    id: compute-path
    with:
      base-path-prefix: '/my-project'
      production-branch: 'master'
```

### Explicitly Specify ref-name

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/compute-web-hosting-deploy-path@v1
    id: compute-path
    with:
      base-path-prefix: '/my-project'
      ref-name: 'feat/awesome'
```

## Behavior

1. Determine the ref-name: Use the `ref-name` input if specified. If not specified, auto-derive based on `github.event_name`:
   - For `pull_request`: `github.head_ref`
   - For `repository_dispatch`: The value of `production-branch`
   - For others: `github.ref_name`
2. Exit with error if ref-name is empty
3. Sanitize the branch name: Replace `/` with `-`
4. Determine production status: If ref-name matches `production-branch`, set `is-production=true` and no feature suffix. Otherwise, set `is-production=false` and use `/_feature/{sanitized-ref}` as the feature suffix
5. Compute the deploy path: `{base-path-prefix}{feature-suffix}`
6. Set the results as outputs

<!-- ## Migration Guide -->

<!-- Uncomment and fill in when there are Breaking Changes -->
