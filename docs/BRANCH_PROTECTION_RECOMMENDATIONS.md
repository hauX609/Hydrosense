# Branch Protection Recommendations

Apply these settings to the `main` branch in GitHub:

## Required status checks

Enable these required checks before merging:

- `frontend-build`
- `backend-smoke`
- `Validate PR title`

## Recommended protections

- Require a pull request before merging.
- Require at least 1 approval.
- Dismiss stale approvals when new commits are pushed.
- Require conversation resolution before merge.
- Require branches to be up to date before merge.
- Restrict force pushes.
- Restrict branch deletion.
- Include administrators.

## Merge strategy

- Allow squash merge.
- Optionally disable merge commits for a cleaner history.

## Suggested branch naming

- `feature/<short-description>`
- `fix/<short-description>`
- `docs/<short-description>`
- `chore/<short-description>`

## Optional tag protection

Protect release tags:

- `v*`

This reduces accidental modification of published release versions.
