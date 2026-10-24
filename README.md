# odradekk skills

Development-workflow skills for coding agents, adapted from the agent workflow of [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) (MIT), whose `.agents/notes` and `.agents/skills` are tied to that one project. These skills keep the method and move every project fact into an `## Agent workflow` section of each repository's `AGENTS.md`.

| Skill | Purpose |
|---|---|
| [`setup-agent-workflow`](skills/setup-agent-workflow/SKILL.md) | Detects a repository's base branch, hooks, CI, and narrowest checks, proves each check by running it, and writes the Agent workflow section. Can also install a pre-commit check that keeps files under a token budget, with a baseline for older large files. |
| [`setup-code-review`](skills/setup-code-review/SKILL.md) | Builds a repository's own `<repo>-code-review` skill from its documents, its existing checks, the failures in its history, adopted review comments, and the user's priorities settled through `grill`. Every check names its source, and a refresh adds, updates, or removes checks as the project changes. |
| [`decision-notes`](skills/decision-notes/SKILL.md) | Agent-written RFCs in `<lifecycle>/<class>/YYYY-MM-DD-slug.md`, moving through proposed, implemented, rejected, and frozen archived states, with a supersession check on every new note and a verifier script. |
| [`grill`](skills/grill/SKILL.md) | Interviews the user in rounds of numbered questions with recommended answers until every decision that matters is settled or deferred, and returns a record of what was settled, what was rejected and why, and what was deferred. Other skills call it with their own settled ground and required answers. The interview method is adapted from the `grilling` skill in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). |
| [`grill-decision`](skills/grill-decision/SKILL.md) | Grounds a decision in the repository's existing notes, settles it with the user through `grill`, and turns the record into decision notes. |
| [`note-to-tickets`](skills/note-to-tickets/SKILL.md) | Splits a proposed decision note into tickets on GitHub or GitLab, one pull request each, and traces a note or ticket to its issues, pull requests, and commits. Tickets point to the note by ID and commits point to tickets, so each link is stored once and the reverse direction is a query. |
| [`plain-language`](skills/plain-language/SKILL.md) | Revises documents, notes, tickets, pull request descriptions, and reports so they read the way an experienced colleague talks: a clear main point and line of reasoning, nothing redundant or off the point, established terms instead of coined ones, and no unexplained abbreviations, working labels, literal translations, or verbal tics. Includes Chinese and English pattern references and a new-reader check. |
| [`pre-push-checks`](skills/pre-push-checks/SKILL.md) | Maps each outgoing change to its narrowest check and runs it once, leaving exhaustive coverage to CI. |

The skills read the section that `setup-agent-workflow` writes and call one another: `grill-decision` and `setup-code-review` run `grill`, `grill-decision` hands its drafts to `decision-notes`, `note-to-tickets` turns proposals into tickets, every step that writes for people revises with `plain-language`, and `pre-push-checks` runs the `decision-notes` verifier. Install them together.

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
- `gh` or `glab`, for `note-to-tickets`

## Development

```sh
python -m unittest discover -s skills/decision-notes/scripts
python -m unittest discover -s skills/setup-agent-workflow/scripts
```
