---
name: improve-architecture
description: A survey of an area or the whole repository for structure worth changing, such as shallow modules, details that leak across seams, state with several owners, and files that always change together, starting where changes concentrate, with a before-and-after figure for each candidate and a decision note for the one the user picks; started only by the user.
disable-model-invocation: true
---

# Improve architecture

Structure is worth changing where it makes future changes expensive: where understanding one concept means reading many modules, where callers must know a module's insides, or where two files change together every time. This skill finds those places, proposes a deeper structure for each with its evidence and a figure, and turns the one the user picks into a decision.

It changes no code. Once the user accepts the decision, it goes on to the `note-to-tickets` and `implement` skills, and `implement` carries it out through the `refactor` skill. What the project could remove instead of restructuring belongs to the `find-simplifications` skill, and the review of a change to the `deep-code-review` skill. The vocabulary of module, interface, depth, and seam is the one the `design-interface` skill defines.

## 1. Set the scope and read the ground

Read the repository's `## Agent workflow` section: Decision notes, Labels, and the check table. If the section is missing, run the `setup-agent-workflow` skill first.

The scope is the area the user names. Otherwise it is where changes concentrate, since a better structure pays off in the changes that come after it. Over the last year of history, or the whole of a shorter one, find:

- **the files changed most often,** for example with `git log --since=1.year --name-only --format= | sort | uniq -c | sort -rn`;
- **the pairs of files that change together** in many commits, counted for each pair as the commits that change both, especially pairs in different modules: two files that keep changing together usually share a detail that one of them should own.

Weight the scope toward those files. When the changes are scattered with no clear center, widen it.

Read the ground as step 1 of the `find-simplifications` skill reads it: accepted notes, especially of class `architecture`, are constraints; rejected notes are proposals already declined, and a candidate that repeats one answers its reason with new evidence; proposed notes are planned work; and in design documents, the parts that describe the code as it is are constraints, and the parts that describe plans are planned work.

Done when you have the scope, with its most-changed files and the pairs that change together, and every active note and design document that touches it is listed with its role.

## 2. Survey

When your tools can start sub-agents, the scope goes to fresh ones, on the most capable model available, running in parallel: one per `area/*` label from the Labels line, or per top-level package or directory where the repository has no area labels. A scope of up to a few thousand lines is surveyed in the current context, and so is any scope when you cannot start sub-agents; say so in the report. Give each surveyor this skill's path, its paths, the most-changed files and pairs within them, the notes and documents from step 1, and the constraints. Each returns its candidates in the form of step 3, and changes nothing.

Look in the existing code for the flaws listed in step 5 of the `design-interface` skill, and for these signs of friction:

- understanding one concept takes reading many small modules;
- a function was extracted to be testable, while the defects come from how it is called;
- code is hard to test through its current interface, or has no tests where the most-changed files are;
- a pair of files from step 1 keeps changing together.

Apply the deletion test from step 3 of `design-interface` to every module that looks shallow.

Done when every part of the scope has been searched.

## 3. Record each candidate

- the modules and files, by the names the code and the project's documents use;
- the evidence: the code paths, and the commits from step 1 that show the friction;
- the deeper structure: a short sketch of the new interface and what moves behind it. The full design waits until a candidate is chosen;
- what disappears: interfaces, layers, copies, branches, files, and the concepts a caller must learn;
- the tests: which would move to the deeper interface, and which would no longer be needed;
- the dependency category of what sits behind the new seam, as step 1 of `design-interface` sorts dependencies;
- any conflict with a decision note: a candidate that goes against an accepted note says why the friction justifies reopening it;
- its strength: **strong** when the friction shows in the history and in the code, **worth exploring** when it shows in the code only, and **speculative** when it is a likely problem not yet seen.

Reject a candidate that only moves code, or whose list of what disappears is short enough that the next reader would not notice.

Done when every candidate has its record.

## 4. Report

When surveyors ran as sub-agents, check the facts each candidate rests on the way the `verify-bug` skill checks a fact about the code: rerun the searches, and read the code paths. Where you disagree, add your reasons beside the candidate instead of removing it.

Then show the candidates as one page with the `visualize` skill: for each, a before-and-after figure of its modules and seams, its record, and its strength, the strongest first, ending with the candidate you would take first and why. In the conversation, list the candidates in a line each, with the page's path, and ask which one to explore.

Write the report in the conversation's language, by the principles of the `plain-language` skill.

Done when the page is written and the user has the list.

## 5. Settle the chosen candidate

Run the `grill-decision` skill on the candidate the user picks: its constraints and dependencies, the shape of the deeper module, what sits behind its seam, and which tests survive. When the shape needs alternatives, the comparison of shapes in step 3 of `design-interface` supplies them. The result is a proposed `architecture` note, written by the `decision-notes` skill in the language the `Decision notes` line names. A proposal that needs more than one pull request goes on to the `note-to-tickets` skill.

When the user rejects a candidate for a reason that a later survey would need, offer to record it as a rejected `architecture` note, written as a proposal and rejected through the `decision-notes` skill, so the next survey reads the reason instead of proposing it again; write it only when the user agrees.

Done when the chosen candidate has its note, and each rejection with a lasting reason is recorded or declined.
