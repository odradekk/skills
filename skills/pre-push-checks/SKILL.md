---
name: pre-push-checks
description: Run the narrowest checks that cover a branch's outgoing changes instead of the full suite. Use before pushing, before opening a pull request or marking it ready, before claiming that checks pass, and after a rebase or merge.
---

# Pre-push checks

Run each piece of evidence once, matched to what the change can break. Hooks run their own narrow checks and CI owns the exhaustive matrix; this skill covers the gap between them: the focused tests and checks that fail if this diff introduced a regression.

## 1. Read the settings

Read the `## Agent workflow` section of the repository's `AGENTS.md`: base branch, hooks, CI, and the table of narrowest checks. If the section is missing, run the `setup-agent-workflow` skill first. If the user declines, find commands in the manifests for this run only, and say so in the report.

## 2. Establish the scope

```sh
git status --short --branch
```

The base is the open pull request's base branch when one exists (read it from the platform that hosts `origin`, for example `gh pr view --json baseRefName --jq .baseRefName`); otherwise it is the configured base branch. Fetch it and take the merge base:

```sh
git fetch origin <base>
git merge-base HEAD origin/<base>
git diff --name-status <merge-base> HEAD
```

Checks run on the working tree, but a push carries only commits, so a passing check proves nothing about the push until the two match. When `git status` shows uncommitted changes, commit the ones that belong to this work with the `commit` skill, and ask the user about the rest.

Done when you have the complete list of paths the push will carry, with their change status.

## 3. Select the checks

Map every changed path to a row of the table, and fill in concrete targets: the test files that exercise the changed code (found through test naming, imports, or the test layout), the changed files for linters, the affected package for builds.

- **Decision notes changed, or a citation of one did:** run the verifier of the `decision-notes` skill, which sits beside this skill (`../decision-notes/` from this skill's directory): `python <decision-notes directory>/scripts/verify_notes.py <notes-dir> --base <merge-base>`. A citation changed when `git diff --name-only -G "Decision note: " <merge-base> HEAD` lists any file: those are the files whose diff adds or removes a `Decision note: <ID>` line.
- **Behavior change that no row covers:** run the narrowest existing test that exercises it. When none does, report the gap; write a test only when the task includes one.
- **Manifests, lockfiles, toolchain, or CI configuration changed:** add the broader rows those files affect, such as the build.
- **Already covered:** leave out a check that a hook runs at commit or push (the Hooks line), and a check that already passed in this session on the same content.
- **Full suite:** run it only when the user asks, when diagnosing a CI failure, or when the change reaches the whole repository, such as a toolchain upgrade or shared configuration. Otherwise CI covers it.

Done when every changed path maps to a selected check, to a check a hook already runs, or to a stated reason that no check applies.

## 4. Run them

Run each selected check once. After a filtered run, read the reported test or file count to confirm the filter selected what you meant; a filter that silently matched everything, or nothing, proves nothing.

When a check fails:

- **Caused by this change:** fix it, commit the fix with the `commit` skill, and rerun that check.
- **Possibly pre-existing:** run the same check at the merge base in a temporary worktree (`git worktree add <dir> <merge-base>`, then `git worktree remove <dir>`). A failure there is pre-existing: report it rather than working around it.

Hooks run as configured; a hook failure is a check failure. If a command from the table no longer exists or its syntax changed, finish with a working command and tell the user that the section needs a refresh through `setup-agent-workflow`.

Done when every selected check passed, or each failure is shown to be pre-existing by the run at the merge base.

## 5. Push

When the work goes into a pull request, the `pr` skill pushes it, after running steps 1 to 4 of this skill. Otherwise push only when the user asked for a push. When the user asked to rewrite a branch's history, push with `git push --force-with-lease`. After a rebase onto, or a merge of, a newer base, repeat steps 2 to 4 for what the new base changed, and rerun only the checks it invalidates.

## 6. Report

List the commands you ran with their results, the changed areas that no check covers and why, test gaps, pre-existing failures, and whether anything was pushed. Report only checks you actually ran.
