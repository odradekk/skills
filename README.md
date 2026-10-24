# odradekk skills

Development-workflow skills for coding agents, adapted from the agent workflow of [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) (MIT), whose `.agents/notes` and `.agents/skills` are tied to that one project. These skills keep the method and move every project fact into an `## Agent workflow` section of each repository's `AGENTS.md`.

| Skill | Purpose |
|---|---|
| [`setup-agent-workflow`](skills/setup-agent-workflow/SKILL.md) | Detects a repository's base branch, hooks, CI, and narrowest checks, proves each check by running it, and writes the Agent workflow section. |
| [`decision-notes`](skills/decision-notes/SKILL.md) | Agent-written RFCs in `<lifecycle>/<class>/YYYY-MM-DD-slug.md`, moving through proposed, implemented, rejected, and frozen archived states, with a supersession check on every new note and a verifier script. |
| [`pre-push-checks`](skills/pre-push-checks/SKILL.md) | Maps each outgoing change to its narrowest check and runs it once, leaving exhaustive coverage to CI. |

`decision-notes` and `pre-push-checks` read the section that `setup-agent-workflow` writes, and `pre-push-checks` calls the `decision-notes` verifier, so install the three together.

## Layout

```
skills/<name>/SKILL.md      one directory per skill
skills/<name>/scripts/      scripts a skill runs
```

## Requirements

- git
- Python 3.10 or later, standard library only, for `skills/decision-notes/scripts/verify_notes.py`

## Development

```sh
python -m unittest discover -s skills/decision-notes/scripts
```
