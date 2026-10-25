---
name: setup-code-review
description: Create or refresh a repository's own code review skill, built from its documents, its existing checks, the failures in its history, adopted review comments, and the user's priorities, with a source for every check. Use when the user asks for a project-specific code review skill, or to update one after new fixes, decisions, or review feedback.
---

# Set up a project code review

A project's review skill is worth what the project has learned and written down. This skill gathers that material, settles the priorities with the user, and writes a review skill in which every check names its source: a document, a commit, a decision note, a review comment, or the user's answer. A check without a source is a generic best practice and stays out.

The generated skill is named `<repo>-code-review`, after the repository's directory, such as `rpgx-code-review`, so it never shadows a general `code-review` skill. It lives at `.agents/skills/<repo>-code-review/SKILL.md`, which Claude Code reaches through the `.claude/skills` link that `setup-agent-workflow` creates, and is committed with the code so it changes with the code.

## 1. Read the settings

Read the repository's `## Agent workflow` section: base branch, hooks, CI, the table of narrowest checks, Tracker, Decision notes, and Prose. If the section is missing, run the `setup-agent-workflow` skill first.

When the generated skill already exists, this run is a refresh. Its last line records the commit its sources were checked up to; steps 2 to 4 cover what changed since that commit, and also look for checks whose source no longer exists or that a tool now enforces.

## 2. Collect the rule sources

Find the written rules: every `AGENTS.md`, `CONTRIBUTING.md`, architecture and design documents, style guides, accepted decision notes (especially the `architecture` and `process` classes), postmortems, and open issues that state rules. For each source, record:

- **Paths:** which parts of the repository it governs.
- **Committed or not:** the generated skill is committed, so it can link only to committed files. List uncommitted sources separately; the user decides in step 5 whether to commit them first.
- **State:** compare the document with the code. A document is *current* when the code matches it, *target* when it describes a design the code has partly reached (say which parts are done), and *stale* when it names paths, symbols, or behavior the code no longer has (note the lines).

Done when every top-level area of the repository is mapped to the sources that govern it, or marked as having no written rules, and every source has its state.

## 3. Collect the checks

From the check table, the Hooks and CI lines, and the linter and test configuration, list every mechanical check, and sort each one:

- **Automatic:** runs on every change without anyone starting it, such as a CI job on every pull request, or a hook that every clone gets. A review leaves out what these catch.
- **Started by hand:** exists, but runs only when someone runs it, such as tests without CI, or a hook that each clone must connect itself. The generated skill has the reviewer run these.

Then list the rules that a source states and no check enforces. Each one is a candidate check whose source is that document.

Done when every check is sorted, and every unenforced written rule is a candidate.

## 4. Mine the history

Look back over the last 12 months, or the whole history if it is shorter; on a refresh, since the recorded commit.

- **Commits:** when the range has fewer than 200 commits, read every commit message, body included. Otherwise search the messages in every language the repository's commits use, for words such as fix, revert, bug, and regression, and their equivalents, such as 修复, 修正, and 回滚. Failures also hide in the bodies of feature commits. Read each relevant diff far enough to say what went wrong and where.
- **Bug-fix decision notes and postmortems** in the range.
- **Adopted review comments**, when the platform that hosts `origin` has merged pull requests: list those merged in the range and read their inline review comments through its tool, for example `gh pr list --state merged --search "merged:>=<date>"` and `gh api repos/{owner}/{repo}/pulls/<N>/comments`. Keep a comment only when someone other than the author wrote it, a later commit in the same pull request changed the lines it points at, and it states a rule that applies beyond that one change.

Group the findings by kind of failure. A kind of failure that touched code which still exists becomes a candidate check, with its sources.

Done when every candidate check, from step 3 or this step, has a description of the failure it prevents and at least one source.

## 5. Settle the priorities with the user

These defaults need no question; the generated skill states them, and the user can edit them later:

- A review covers pull requests, branches, and work committed straight to the base branch.
- The reviewer runs the checks that are started by hand, choosing them through the `pre-push-checks` skill, and reports the results.
- Current documents are rules. For a target document, the finished parts are rules; the unfinished parts apply only to code a change newly writes there, and known gaps between them and the code are not findings. Stale documents are not rules for the stale lines; the report in step 7 lists them so someone can fix them.

Run the `grill` skill with:

- **Topic:** what a review of this repository must catch.
- **Settled ground:** the defaults above, the sources from step 2 with their states, the checks from step 3, and the candidate checks with their sources.
- **Required answers:** for each candidate, whether it blocks a merge, is a suggestion, or is dropped; whether to commit the uncommitted sources so the skill can link to them, when there are any; concerns of the user's that no source records yet, each of which becomes a check whose source is the user's answer and its date; and anything a review report must contain beyond the default.
- **Reader:** the people and agents who review changes to this repository.

Done when the user has confirmed the grill record.

## 6. Write the skill

Fill in [references/review-skill-template.md](references/review-skill-template.md) from the grill record:

- **Sources of truth:** paths mapped to the committed documents that govern them, as links, with a note on how to apply each target document. The rules stay in those documents.
- **Blocking requirements** and **Suggestions:** the confirmed checks, each with its source.
- **Checked automatically** and **Run by the reviewer:** the two lists from step 3.
- The last line records the current commit.

Write the skill in the language the `Decision notes` line names, translating the template's headings and text; keep the front matter keys, commands, paths, and code as they are. Keep it to a table of sources and a short list of checks, so it routes the reviewer to the project's documents instead of repeating them. Revise it with the `plain-language` skill, then show it, or on a refresh show the changes, and write it only after the user approves. Leave the changes uncommitted unless the user asked for a commit; then commit them with the `commit` skill.

## 7. Report

State the file written; the number of checks with each kind of source; the candidates the user dropped; the stale documents and lines from step 2, so someone can fix them; and the areas of the repository with no written rules, where a document would make reviews better.
