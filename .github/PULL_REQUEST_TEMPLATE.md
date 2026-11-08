## Summary (written by a person, in your own words)

<!-- What changes for the users of the plugin or for the engineers, and why. -->

Closes #

## How it was built

- [ ] Spec and plan: `docs/plans/...` (or: small change agreed in the issue)
- [ ] Tests written first; new behaviour covered (unit, self-test, DOM, browser)
- [ ] Agent involvement disclosed: <!-- none / Copilot agent mode / Copilot CLI / Copilot cloud agent; Superpowers skills used -->

## Gates

- [ ] `python tools/dev.py check` ends with ALL GATES PASSED (paste the summary below)
- [ ] Renderer changes: `python tools/dev.py site e2e` and screenshots attached
- [ ] Generated files regenerated, not hand-edited (template, `plugin-install.json`)

```
<gate summary>
```

## Rules

- [ ] Customer-neutral (Caldova only); no secrets
- [ ] Plugin changed after a release: version bumped (`python tools/dev.py bump X.Y.Z`) and CHANGELOG updated
- [ ] SKILL.md, references, PRD or ADR updated where behaviour or design changed
- [ ] Microsoft product icons used within their terms; notices updated

## Release pull requests only

- [ ] Cowork skill validators run in Copilot Cowork (structure, score, conflicts, security, package)
- [ ] Behavioural prompts of PRD B.9 route to the expected skills
- [ ] Install from the built package tested in a Cowork chat
