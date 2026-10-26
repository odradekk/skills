---
name: grill-decision
description: Settle a decision with the user through the grill skill and record it as decision-note proposals. Use when the user asks to grill a decision that should become a note, or when a note is due but its alternatives were never weighed with the user.
---

# Grill a decision

A decision note and a grill record have the same parts. The note's Proposal is the path the user chose; its Alternatives considered are the options the user turned down, each with the reason that settled it. This skill grounds the interview in the repository's notes, runs it through the `grill` skill, and turns the record into notes without inventing anything.

## 1. Ground the topic

Read the `Decision notes` line of the repository's `## Agent workflow` section; if the section is missing, run the `setup-agent-workflow` skill first. Search the active notes (everything outside `archived/`) and the relevant code for the topic, and sort the notes you find:

- **A proposal that already owns this decision:** the session revises it instead of starting a new one.
- **An accepted note that owns it:** frozen; a change to the decision becomes a new proposal that supersedes it.
- **Accepted notes:** settled constraints.
- **Rejected notes:** options already turned down, with their reasons.
- **Proposed notes on the same topic:** candidates to update, merge, or reject.

Done when you can name every active note that touches the topic, or have confirmed that none does.

## 2. Grill

Run the `grill` skill with:

- **Topic:** the decision.
- **Settled ground:** the constraints from accepted notes, and the options rejected notes turned down, with their reasons.
- **Required answers:** for work not yet built, what observable state means done and what the change knowingly gives up; for work that already shipped, what it cost.
- **Reader:** whoever reads the repository's decision notes.

Done when the user has confirmed the grill record.

## 3. Draft the notes

Map the record onto the sections of the `decision-notes` format:

| From the record | Into |
|---|---|
| Topic as confirmed | Problem |
| Settled decisions on the chosen path | Proposal |
| Settled technical sub-decisions, such as a data format or an interface | Free-form sections between the required ones |
| Rejected options with their reasons | Alternatives considered |
| Costs the user accepted, and the risks raised | Risks |
| The answer to what counts as done | Acceptance criteria |
| Deferred questions | Open questions in the Proposal |

A record that settled several independent decisions, each with its own trade-off, produces one note per decision; a sub-decision that depends on one choice stays in that choice's note. Write each note as current-state prose about the decision and its reasons. Round numbers, attributions such as "the user said", and the course of the interview stay out of the note.

Revise the drafts with the `plain-language` skill, then show them, with the class folder you chose for each, and wait for the user to confirm them.

## 4. Record them

Write the confirmed notes as proposals by following the `decision-notes` skill, starting with its check of the notes a proposal touches; the notes found in step 1 are its first candidates. They stay proposals until the user accepts them, through the `decision-notes` skill.

Done when the `decision-notes` verifier passes and the user has confirmed every note's content.
