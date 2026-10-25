# Template for a generated review skill

Replace every `<placeholder>`, and translate the headings and text into the language of the repository's decision notes. Leave out what does not apply: the ticket checks need a tracker, the note checks need decision notes, and an empty list of checks run by the reviewer drops that section.

````markdown
---
name: <repo>-code-review
description: Review a change to <repo> against this repository's rules and the failures it has had before. Use when reviewing a pull request, a branch, commits made straight to <base branch>, or uncommitted changes in <repo>.
---

# Reviewing a <repo> change

Built with the `setup-code-review` skill, which refreshes it. Edit it freely, and keep a source on every check.

## Who reviews

When your tools can start a sub-agent, the review runs in a fresh one, on the most capable model available, and you coordinate. An agent that wrote the change, or watched it being written, shares the assumptions behind it and misses what they hide.

1. Find the change. For a pull request, compare its head with the merge base of its base branch. For a branch, compare it with its merge base with `<base branch>`. For commits made straight to `<base branch>`, take the commits the user names, or the commits not yet on `origin/<base branch>`, together with any uncommitted changes.
2. Start the reviewer with only: the change, as a base and head or a list of commits and uncommitted paths; this skill's path; the IDs of the tickets and decision notes the change serves; and the pull request description, when there is one, as claims to check. The conversation and reasoning that produced the change stay out. For a change across several areas, start one reviewer per group of areas, and one more that checks only the change against its tickets' acceptance criteria.
3. Pass the findings on as reported. Check factual claims, such as whether a line exists; where you disagree with a judgment, add your reasons beside the finding instead of removing it.

Without sub-agents, review the change yourself and say in the report that the review ran in the author's context.

## Process

The reviewer:

1. Lists the changed paths, and for each one reads the documents that Sources of truth lists for it, before reading the diff.
2. Reads the diff, and enough of the surrounding code to understand the design.
3. Runs the checks listed under Run by the reviewer for the changed paths.
4. Applies the blocking requirements, then the suggestions for the changed paths, then the workflow checks.
5. Reports.

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

- The change meets the acceptance criteria of its ticket. A pull request that completes the ticket carries the tracker's closing reference, such as `Fixes #N`, in its description; work committed straight to `<base branch>` carries the ticket reference, or the closing reference in the completing commit, in its commit messages instead. Source: the Tracker line in `AGENTS.md`.
- The change edits no decision note outside `proposed/`, and the `decision-notes` verifier with `--base` passes. A conflict with an accepted note is reported for planning, not resolved by changing the note. Source: the Decision notes line in `AGENTS.md`.
- A change to code that cites a decision note (`Decision note: <ID>`) follows the decision of that note when it is accepted, or of the note that supersedes it; new code whose shape an accepted note explains cites that note. Source: the `decision-notes` skill.
- New or changed prose follows the `plain-language` skill. Source: the Prose line in `AGENTS.md`.

## Reporting

For each finding, state the check it comes from, if any, the defect, its location, its impact, and the evidence. List blocking findings before suggestions, then the checks you ran with their results. On a pull request, put a finding about one spot on that line of the diff, and a finding about the whole change on the pull request; without a pull request, give the file and line in the report. When you receive a review, verify its findings with the `verify-bug` skill before acting on them; fix the ones that hold, and give the evidence for the rest.

Sources checked up to commit `<sha>` (<YYYY-MM-DD>).
````
