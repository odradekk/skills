---
name: grill
description: Grill the user in rounds of numbered questions with recommended answers until every branch of a plan, design, or decision is settled or deferred, and return the record. Use when the user asks to be grilled or to stress-test a plan.
---

# Grill

An interview that settles decisions with the user. Facts are your job: find them in the code, the documents, the configuration, and the history. Decisions are the user's: put each one to the user and wait for the answer.

## Inputs

A skill that calls grill passes four things:

- **Topic:** the question to settle.
- **Settled ground:** facts and decisions already fixed, such as constraints from accepted decision notes, and options rejected earlier together with their reasons. They become prerequisites in the tree, not questions.
- **Required answers:** the questions the caller's output cannot be written without, such as what counts as done.
- **Reader:** who reads the caller's output.

When the user starts grill directly, the topic is what the user named, you find the settled ground in the repository yourself, and the required answers are whatever the plan needs before someone can act on it.

## 1. Map the design tree

The root is the topic. Every decision branches into the decisions that depend on it, and the options at each branch are the candidate alternatives. Each required answer is a branch too. A question belongs in the tree only when its answer changes the decision, its cost, or what counts as done; easily reversed details are left to the work itself.

The **frontier** is every open question whose prerequisites are settled.

## 2. Ask in rounds

Open the first round by restating the topic in two or three sentences, without a solution, as the first question, so the user can correct the framing. Add the frontier questions that stay the same however the user corrects the framing.

Each round asks the whole frontier, numbered; a question that depends on another question still open in the same round belongs to a later round. A question with options names each option with what it costs and buys, and gives your recommendation with its reason. An open question, such as what else worries the user, has no options and no recommendation. When one question asks the user to rate several items the same way, such as blocking or suggestion for each candidate check, put the items in a table with your recommendation for each.

```markdown
**Settled since the last round:** <one line per decision; from the second round on>

**Q1. <title>**
<the question, and each option with what it costs and buys>
Recommended: <option>, because <reason>.

**Q2. <title>**
<what the items are rated on>

| Item | Recommended | Why |
|---|---|---|
| <item> | <option> | <reason> |
```

Then wait for the answers. Each answer reshapes the tree, so recompute the frontier before the next round.

- **A question needs a fact:** look it up, with a sub-agent where your tools allow, and meanwhile ask the questions that do not depend on it.
- **The user turns an option down:** keep the reason that settled it, either the user's own or the trade-off from your question that the user accepted. When the round shows no reason, ask for one: a rejected option is recorded only with the reason it lost.
- **The user leans toward an option the settled ground rejected:** show the earlier reasons and ask whether they still hold.
- **The user defers a question:** mark it deferred and move on.

Done when the frontier is empty: every branch is settled or deferred by the user, and nothing is silently assumed.

## 3. Return the record

Write the outcome in this form, as current-state statements without round numbers:

```markdown
## Grill record: <topic>

**Topic as confirmed:** <the framing the user accepted>

**Settled**
- <decision>: <chosen option>, because <reason>.

**Rejected**
- <option>, for <decision>: <the reason it lost>.

**Deferred**
- <question>

**Facts found**
- <fact> (<file, command, or commit it came from>)
```

Show the record and wait for the user to confirm that it matches what was decided. A calling skill continues from the confirmed record; when the user started grill directly, the record is the result.
