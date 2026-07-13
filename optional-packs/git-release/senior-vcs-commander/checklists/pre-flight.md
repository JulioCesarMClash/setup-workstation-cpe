# Pre-Flight Checklist

Use this checklist before push, PR creation, or release handoff.

## SDD Readiness
- [ ] `change_name` is confirmed and matches the branch intent.
- [ ] `sdd-design` exists and is the current design source of truth.
- [ ] Relevant items in `sdd-tasks` are complete for this scope.
- [ ] `sdd-verify` has been executed for the change.

## Git Hygiene
- [ ] Current branch follows `{type}/{change-name}` or repo policy.
- [ ] The diff contains only related work.
- [ ] Commits are atomic and reversible.
- [ ] Commit messages follow Conventional Commits.

## Jira Traceability
- [ ] `issue_key` is known or explicitly waived.
- [ ] Jira comment draft reflects current task and verification state.
- [ ] PR linkage strategy for `issue_key` is prepared.

## CI/CD Guard
- [ ] CI configuration was checked (`Jenkinsfile` or `.github/workflows/`).
- [ ] For deployable repos, deploy authority is explicit: Jenkins executor, GitHub Actions CI/trigger only.
- [ ] Local tests were run, or a human explicitly waived them.
- [ ] Build/lint/test evidence is available for the PR.

## PR Readiness
- [ ] PR body references `change_name`.
- [ ] PR body links the design artifact or design file path.
- [ ] PR summary explains what changed and why.
- [ ] Risks, follow-ups, or waivers are documented.

## Human Approval Gate
- [ ] No destructive Git action is pending without approval.
- [ ] Shared-history operations are explicitly approved if needed.
