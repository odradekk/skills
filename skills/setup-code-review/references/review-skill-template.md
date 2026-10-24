# Template for a generated review skill

Replace every `<placeholder>`, and translate the headings and text into the language of the repository's decision notes. Leave out what does not apply: the ticket checks need a tracker, the note checks need decision notes, and an empty list of checks run by the reviewer drops that section.

````markdown
---
name: <repo>-code-review
description: Review a change to <repo> against this repository's rules and the failures it has had before. Use when reviewing a pull request, a branch, commits made straight to <base branch>, or uncommitted changes in <repo>.
---

# Reviewing a <repo> change

Built with the `setup-code-review` skill, which refreshes it. Edit it freely, and keep a source on every check.

## Process

1. Find the change. For a pull request, compare its head with the merge base of its base branch. For a branch, compare it with its merge base with `<base branch>`. For commits made straight to `<base branch>`, review the commits the user names, or the commits not yet on `origin/<base branch>`, together with any uncommitted changes. List the changed paths.
2. For each changed path, read the documents that Sources of truth lists for it, before reading the diff.
3. Read the diff, and enough of the surrounding code to understand the design.
4. Run the checks listed under Run by the reviewer for the changed paths.
5. Apply the blocking requirements, then the suggestions for the changed paths, then the workflow checks.
6. Report.

## Sources of truth

| Paths | Rules in |
|---|---|
| `<glob>` | [<document>](<relative link>) |

<For each target document: which parts are finished and apply as rules, and that unfinished parts apply only to code a change newly writes there.>

## Checked automatically

<What runs on every change without anyone starting it. Findings these checks catch stay out of the report.>

## Run by the reviewer

<The checks that exist but run only when someone starts them. Choose the ones for the changed paths through the `pre-push-checks` skill, run them, and put the commands and results in the report.>

## Blocking requirements

1. **<name>.** <What must hold, and what goes wrong when it does not.> Source: <link, commit, note, review comment, or "the user, YYYY-MM-DD">.

## Suggestions

Report these as suggestions; they do not block a merge.

- **<name>** (`<paths>`): <what to look for, and the failure it prevents>. Source: <...>.

## Workflow checks

- The change meets the acceptance criteria of its ticket; commits for the ticket say `Refs #N`, and the pull request that completes it says `Fixes #N`. Source: the Tracker line in `AGENTS.md`.
- A pull request that closes the last open ticket of a decision note moves the note to `implemented/`. Source: the Tracker line in `AGENTS.md`.
- A change to something an implemented decision note describes updates that note in the same change. Source: the Decision notes line in `AGENTS.md`.
- New or changed prose follows the `plain-language` skill. Source: the Prose line in `AGENTS.md`.

## Reporting

For each finding, state the defect, its location, its impact, and the evidence. List blocking findings before suggestions, then the checks you ran with their results. On a pull request, put a finding about one spot on that line of the diff, and a finding about the whole change on the pull request; without a pull request, give the file and line in the report. When you receive a review, check each claim before acting on it, then fix it or explain why not.

Sources checked up to commit `<sha>` (<YYYY-MM-DD>).
````
