<!-- Instructions for GitHub Copilot (Coding Agent & Code Review) -->

## For All Copilot Agents (Coding Agent & Code Review)

- Always read and follow `AGENTS.md` in the repository root before starting any work. It contains essential rules on SHA pinning, naming conventions, directory structure, and CI quality gates.

## For Copilot Coding Agent

- When creating an issue, always read the issue templates first:
  - `.github/ISSUE_TEMPLATE/bug-report.yml`
  - `.github/ISSUE_TEMPLATE/feature-request.yml`
- When creating a pull request, always read the PR template first:
  - `.github/PULL_REQUEST_TEMPLATE.md`
- Follow the templates exactly and fill in all required fields.
- When making architectural or design decisions, record them as an Architecture Decision Record (ADR):
  1. Run `npm run adr:new -- "ADR title"` to generate a new ADR file in `docs/adr/`.
  2. Fill in the Context, Decision, and Consequences sections. Refer to existing ADRs in `docs/adr/` for the expected format and level of detail.
  3. Include the ADR in the same pull request as the implementation.
