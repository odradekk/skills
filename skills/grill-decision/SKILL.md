---
name: grill-decision
description: Grill the user about a design decision in rounds of questions with recommended answers until every branch that matters is settled, then record the outcome as decision notes. Use when the user asks to grill a plan or design, or when a decision note is due but its choice or alternatives were never weighed with the user.
---

# Grill a decision

A grilling session and a decision note have the same structure. The note's Proposal or Decision is the path the user chose through the **design tree**; its Alternatives considered are the branches the user turned down, each with the reason that settled it. Run the interview so the note can be written from it without inventing anything.

Facts are your job: find them in the code, the notes, the configuration, and the history. Decisions are the user's: put each one to the user and wait for the answer.

## 1. Ground the topic

Read the `Decision notes` line of the repository's `## Agent workflow` section; if the section is missing, run the `setup-agent-workflow` skill first. Search the active notes (everything outside `archived/`) and the relevant code for the topic, and sort the notes you find:

- **An active note that already owns this decision:** the session updates that note instead of starting a new one.
- **Implemented notes:** settled constraints. They become prerequisites in the tree, not questions.
- **Rejected notes:** guardrails. When the user leans toward a rejected option, show the note's reasons and ask whether they still hold.
- **Proposed notes on the same topic:** candidates to update, merge, or reject.

Done when you can name every active note that touches the topic, or have confirmed that none does.

## 2. Map the design tree

The root is the problem. Every decision branches into the decisions that depend on it, and the options at each branch are the candidate alternatives. A question belongs in the tree only when its answer changes the decision, its cost, or what counts as done; easily reversed details are left to implementation.

The tree also holds the questions the note needs answered. For work not yet built, ask what observable state means done and what the change knowingly gives up. For work that already shipped, ask what it cost.

The **frontier** is every open question whose prerequisites are settled.

## 3. Ask in rounds

Open the first round with the problem: state it in two or three sentences, without the solution, as the first question, so the user can correct the framing. Add the frontier questions whose answers do not depend on that framing.

Each round asks the whole frontier, numbered. Each question names its options with what each costs and buys, and gives your recommendation with its reason:

```markdown
**Settled since the last round:** <one line per decision>

**Q1. <title>**
<the question, and each option with what it costs and buys>
Recommended: <option>, because <reason>.

**Q2. <title>**
...
```

Then wait for the answers. Each answer reshapes the tree, so recompute the frontier before the next round. A question that depends on another question still open in the same round belongs to a later round.

- **A question needs a fact:** find it yourself, with a sub-agent where your tools allow. Meanwhile, ask the questions that do not depend on that fact.
- **The user turns an option down:** keep the reason that settled it, either the user's own or the trade-off from your question that the user accepted. When the round shows no reason, ask for one: an alternative goes into the note only with the reason it lost.
- **The user defers a question:** mark it deferred and move on.

Done when the frontier is empty: every branch is settled or deferred by the user, and nothing is silently assumed.

## 4. Draft the notes

Map the session onto the sections of the `decision-notes` format:

| From the session | Into |
|---|---|
| The problem statement the user confirmed | Problem |
| The chosen path through the tree | Proposal; Decision for work that already shipped |
| Technical sub-decisions on that path, such as a data format or an interface | Free-form sections between the required ones |
| Each turned-down option, with the reason that settled it | Alternatives considered |
| Costs the user accepted, and the risks raised | Risks; Consequences for work that already shipped |
| What the user said counts as done | Acceptance criteria |
| Deferred questions | Open questions in the Proposal; a `## Deferred` section for work that already shipped |

A session that settled several independent decisions, each with its own trade-off, produces one note per decision; a sub-decision that depends on one choice stays in that choice's note. Write each note as current-state prose about the decision and its reasons. Round numbers, attributions such as "the user said", and the course of the interview stay out of the note.

Revise the drafts with the `plain-language` skill, then show them, with the lifecycle and class folder you chose for each, and wait for the user to confirm them.

## 5. Record them

Write the confirmed notes by following the `decision-notes` skill, starting with its supersession check; the notes found in step 1 are its first candidates.

Done when the `decision-notes` verifier passes and the user has confirmed every note's content.
