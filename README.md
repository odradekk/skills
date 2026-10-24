# odradekk skills

Development-workflow skills for coding agents, adapted from the agent workflow of [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) (MIT), whose `.agents/notes` and `.agents/skills` are tied to that one project. These skills keep the method and move every project fact into an `## Agent workflow` section of each repository's `AGENTS.md`.

| Skill | Purpose |
|---|---|
| [`setup-agent-workflow`](skills/setup-agent-workflow/SKILL.md) | Detects a repository's base branch, hooks, CI, and narrowest checks, proves each check by running it, and writes the Agent workflow section. |
| [`decision-notes`](skills/decision-notes/SKILL.md) | Agent-written RFCs in `<lifecycle>/<class>/YYYY-MM-DD-slug.md`, moving through proposed, implemented, rejected, and frozen archived states, with a supersession check on every new note and a verifier script. |
| [`grill-decision`](skills/grill-decision/SKILL.md) | Interviews the user in rounds of questions with recommended answers until a decision and its alternatives are settled, then drafts the decision notes from the session. The interview method is adapted from the `grilling` skill in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). |
| [`note-to-tickets`](skills/note-to-tickets/SKILL.md) | Splits a proposed decision note into tickets on GitHub or GitLab, one pull request each, and traces a note or ticket to its issues, pull requests, and commits. Tickets point to the note by ID and commits point to tickets, so each link is stored once and the reverse direction is a query. |
| [`pre-push-checks`](skills/pre-push-checks/SKILL.md) | Maps each outgoing change to its narrowest check and runs it once, leaving exhaustive coverage to CI. |

The skills read the section that `setup-agent-workflow` writes and call one another: `grill-decision` hands its drafts to `decision-notes`, `note-to-tickets` turns proposals into tickets, and `pre-push-checks` runs the `decision-notes` verifier. Install them together.

## Layout

```
skills/<name>/SKILL.md      one directory per skill
skills/<name>/scripts/      scripts a skill runs
```

## Requirements

- git
- Python 3.10 or later, standard library only, for `skills/decision-notes/scripts/verify_notes.py`
- `gh` or `glab`, for `note-to-tickets`

## Development

```sh
python -m unittest discover -s skills/decision-notes/scripts
```
