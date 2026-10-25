# odradekk skills

Development-workflow skills for coding agents, adapted from the agent workflow of [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) (MIT), whose `.agents/notes` and `.agents/skills` are tied to that one project. These skills keep the method and move every project fact into an `## Agent workflow` section of each repository's `AGENTS.md`.

| Skill | Purpose |
|---|---|
| [`setup-agent-workflow`](skills/setup-agent-workflow/SKILL.md) | Detects a repository's base branch, hooks, CI, and narrowest checks, proves each check by running it, and writes the Agent workflow section. Sets up and refreshes the issue labels: one `kind/*` per issue, from the decision note classes, and the `area/*` labels for the parts of the system it touches. Installs git hooks: commit-msg and pre-push hooks that remove AI attribution from commit messages, and a pre-commit check that keeps files under a token budget, with a baseline for older large files. |
| [`setup-code-review`](skills/setup-code-review/SKILL.md) | Builds a repository's own `<repo>-code-review` skill from its documents, its existing checks, the failures in its history, adopted review comments, and the user's priorities settled through `grill`. Every check names its source, and a refresh adds, updates, or removes checks as the project changes. The generated review runs in a fresh sub-agent, away from the author's context. |
| [`deep-code-review`](skills/deep-code-review/SKILL.md) | Started only by the user: a strict review of a change or an area for restructurings that remove concepts while keeping behavior, run by fresh sub-agents and grounded in the decision notes, with a sketch and a behavior argument for every finding. Its standards draw on ideas from the `thermo-nuclear-code-quality-review` skill in [cursor/plugins](https://github.com/cursor/plugins). |
| [`verify-bug`](skills/verify-bug/SKILL.md) | Decides whether a claimed bug is real before anyone fixes it, whether the claim comes from a review, a user, or a ticket. Each claim ends as holds, does not hold, or unconfirmed: a claim holds only with a reproduction that goes red on the current code, and is ruled out only with positive evidence, never because a reproduction failed to fail. Review findings go to fresh sub-agents. |
| [`diagnose-bug`](skills/diagnose-bug/SKILL.md) | Starts from the red reproduction of `verify-bug`, tightens it, then tests ranked, falsifiable hypotheses one probe at a time, and fixes the bug behind a regression test at a seam that exercises the real call path. Adapted from the `diagnosing-bugs` skill in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT), whose reproduction methods and human-in-the-loop script now live in `verify-bug`. |
| [`setup-performance`](skills/setup-performance/SKILL.md) | Builds and refreshes a repository's performance system: it finds the user operations whose speed or memory matters, settles targets and workloads with the user through `grill`, records them in a `testing` decision note, builds scenarios that are proven to catch the cost they guard against, and writes a `<repo>-performance` skill with the scenarios, profiling commands, and an optimization loop of one change at a time. Measurement code is kept as project infrastructure under rules in its directory's `AGENTS.md`, and a refresh audits it for duplicate, dead, or stale scenarios. Draws on `dsh-speed-up-perf` and `benchmarks/AGENTS.md` in deepseek-harness, and on the perf playbooks of `poteto-mode` in [backnotprop/pstack](https://github.com/backnotprop/pstack) (MIT). |
| [`measure-performance`](skills/measure-performance/SKILL.md) | The standard for every performance number: a measurement plan before running, seven checks (the limiter, production settings, physical limits, errors, repeatability, end-to-end share, and whether the work ran), and a report that leads with faster, slower, no measurable difference, or inconclusive. Adapted from the `benchmark-checklist` skill in [backnotprop/pstack](https://github.com/backnotprop/pstack) (MIT). |
| [`decision-notes`](skills/decision-notes/SKILL.md) | Agent-written RFCs in `<lifecycle>/<class>/YYYY-MM-DD-slug.md`, moving through proposed, implemented, rejected, and frozen archived states, with a supersession check on every new note and a verifier script. |
| [`grill`](skills/grill/SKILL.md) | Interviews the user in rounds of numbered questions with recommended answers until every decision that matters is settled or deferred, and returns a record of what was settled, what was rejected and why, and what was deferred. Other skills call it with their own settled ground and required answers. The interview method is adapted from the `grilling` skill in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). |
| [`grill-decision`](skills/grill-decision/SKILL.md) | Grounds a decision in the repository's existing notes, settles it with the user through `grill`, and turns the record into decision notes. |
| [`note-to-tickets`](skills/note-to-tickets/SKILL.md) | Splits a proposed decision note into tickets on the repository's tracker, one pull request each, and traces a note or ticket to its tickets, pull requests, and commits. Tickets point to the note by ID, blocking edges use the tracker's own relation when it has one, and pull requests point to tickets, so each link is stored once and the reverse direction is a query. |
| [`plain-language`](skills/plain-language/SKILL.md) | Revises documents, notes, tickets, pull request descriptions, and reports so they read the way an experienced colleague talks: a clear main point and line of reasoning, nothing redundant or off the point, established terms instead of coined ones, and no unexplained abbreviations, working labels, literal translations, or verbal tics. Includes Chinese and English pattern references and a new-reader check. |
| [`visualize`](skills/visualize/SKILL.md) | Shows structure, flow, state, change, or data as a figure: a small text diagram in the reply, or a self-contained, offline HTML page that is always written to a temporary directory, never the workspace. Other skills call it for their figures. Its catalog of forms is adapted from the `show-me` skill in [humanlayer/skills](https://github.com/humanlayer/skills) (MIT). |
| [`explain`](skills/explain/SKILL.md) | Started only by the user: explains a change, a part of the codebase, a concept, a decision, or a failure against stated learning goals, with figures from `visualize` and a quiz whose answers the reader can paste back. Exploration runs in fresh sub-agents, adapted from the `how` skill in [backnotprop/pstack](https://github.com/backnotprop/pstack) (MIT). |
| [`pre-push-checks`](skills/pre-push-checks/SKILL.md) | Maps each outgoing change to its narrowest check and runs it once, leaving exhaustive coverage to CI. |
| [`commit`](skills/commit/SKILL.md) | Commits the current changes as Conventional Commits grouped by intent, in the repository's own style, without asking for confirmation. Leaves out files that look like secrets or accidents, and stops only for conflicts or hook failures it did not cause. |
| [`pr`](skills/pr/SKILL.md) | Runs the pre-push checks, pushes, and opens or updates a pull or merge request with a description written for reviewers (why, what changed, testing) and the kind and area labels, without asking for confirmation. |

The skills read the section that `setup-agent-workflow` writes and call one another: `grill-decision` and `setup-code-review` run `grill`, `grill-decision` hands its drafts to `decision-notes`, `note-to-tickets` turns proposals into tickets, review findings are checked through `verify-bug` before anyone acts on them and `diagnose-bug` starts from its reproduction, every performance number goes through `measure-performance`, every step that writes for people revises with `plain-language`, `pre-push-checks` runs the `decision-notes` verifier, and every skill that commits or opens a pull request does it through `commit` and `pr`. Install them together.

## In a repository

The skills keep everything they install in a repository under `.agents/`: decision notes, project skills, git hooks, the hook scripts, and their settings, so one set of files serves every agent. The root holds only `AGENTS.md`, a one-line `CLAUDE.md` that imports it, and a `.claude/skills` link to `.agents/skills` for Claude Code. [layout.md](skills/setup-agent-workflow/references/layout.md) shows the layout, the link on Windows, and how to move an older layout.

## Always-loaded principles

A skill loads only when something triggers it, but agents write to people on almost every turn. [`skills/plain-language/core.md`](skills/plain-language/core.md) holds the few principles that need to be in context all the time; at deployment, copy them into each agent's global instructions.

## Layout

```
skills/<name>/SKILL.md      one directory per skill
skills/<name>/scripts/      scripts a skill runs
```

## Requirements

- git
- Python 3.10 or later, standard library only, for the scripts in `skills/*/scripts/`
- The command-line tool or MCP tools of the tracker and of the platform that hosts the repository, for `note-to-tickets` and `pr`. The skills give `gh` examples; the Tracker line of each repository's Agent workflow section names its tools.

## Development

```sh
python -m unittest discover -s skills/decision-notes/scripts
python -m unittest discover -s skills/setup-agent-workflow/scripts
```
