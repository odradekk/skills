---
name: grill-decision
description: Settle a design decision with the user through the grill skill, then record the outcome as decision notes. Use when the user asks to grill a decision that should become a decision note, or when a decision note is due but its choice or alternatives were never weighed with the user.
---

# Grill a decision

A decision note and a grill record have the same parts. The note's Proposal or Decision is the path the user chose; its Alternatives considered are the options the user turned down, each with the reason that settled it. This skill grounds the interview in the repository's notes, runs it through the `grill` skill, and turns the record into notes without inventing anything.

## 1. Ground the topic

Read the `Decision notes` line of the repository's `## Agent workflow` section; if the section is missing, run the `setup-agent-workflow` skill first. Search the active notes (everything outside `archived/`) and the relevant code for the topic, and sort the notes you find:

- **An active note that already owns this decision:** the session updates that note instead of starting a new one.
- **Implemented notes:** settled constraints.
- **Rejected notes:** options already turned down, with their reasons.
- **Proposed notes on the same topic:** candidates to update, merge, or reject.

Done when you can name every active note that touches the topic, or have confirmed that none does.

## 2. Grill

Run the `grill` skill with:

- **Topic:** the decision.
- **Settled ground:** the constraints from implemented notes, and the options rejected notes turned down, with their reasons.
- **Required answers:** for work not yet built, what observable state means done and what the change knowingly gives up; for work that already shipped, what it cost.
- **Reader:** whoever reads the repository's decision notes.

Done when the user has confirmed the grill record.

## 3. Draft the notes

Map the record onto the sections of the `decision-notes` format:

| From the record | Into |
|---|---|
| Topic as confirmed | Problem |
| Settled decisions on the chosen path | Proposal; Decision for work that already shipped |
| Settled technical sub-decisions, such as a data format or an interface | Free-form sections between the required ones |
| Rejected options with their reasons | Alternatives considered |
| Costs the user accepted, and the risks raised | Risks; Consequences for work that already shipped |
| The answer to what counts as done | Acceptance criteria |
| Deferred questions | Open questions in the Proposal; a `## Deferred` section for work that already shipped |

A record that settled several independent decisions, each with its own trade-off, produces one note per decision; a sub-decision that depends on one choice stays in that choice's note. Write each note as current-state prose about the decision and its reasons. Round numbers, attributions such as "the user said", and the course of the interview stay out of the note.

Revise the drafts with the `plain-language` skill, then show them, with the lifecycle and class folder you chose for each, and wait for the user to confirm them.

## 4. Record them

Write the confirmed notes by following the `decision-notes` skill, starting with its supersession check; the notes found in step 1 are its first candidates.

Done when the `decision-notes` verifier passes and the user has confirmed every note's content.
