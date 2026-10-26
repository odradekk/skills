---
name: implement
description: 'Carry one ticket, accepted decision note, or request to reviewed code without stopping: design-interface, design-ui, and tdd, diagnose-bug, or refactor, then simplify-change and the repository''s own review. Use when the user asks to implement a ticket, a decision note, a feature, or a fix.'
---

# Implement

This skill runs the development workflow for one piece of work: one ticket, one accepted decision note small enough for one pull request, or one request. Each stage is its own skill. This skill gives each stage its input, acts on its report, and carries forward what it cannot settle. It runs without stopping for anyone: the user's request starts it, and its report, with the decisions it leaves to the user, ends it.

The stages run in this context, and the rules each stage's skill sets for sub-agents apply, such as fresh reviewers and verifiers.

## 1. Take in the work

Read the repository's `## Agent workflow` section: base branch, Tracker, Decision notes, CI, and the check table. If the section is missing, find the checks in the manifests for this run only, and say so in the report.

- **The intent:**
  - **A ticket:** read it through the tool the Tracker line names, with its acceptance criteria, and the decision note it cites by ID.
  - **A decision note:** only an accepted note is carried out; for a proposal, the report says that the user must accept it first, through the `decision-notes` skill. When an accepted note has open tickets, found as the `note-to-tickets` skill finds them, work on the ticket the user named, or else on the first open ticket that nothing blocks, and say which. An accepted note without tickets that needs more than one pull request is not started: the report says it needs splitting with the `note-to-tickets` skill.
  - **A request** in the conversation.
- **The kind:** a defect, such as a ticket labeled `kind/bug-fix` or a report that something is broken; a change of structure only, such as a ticket labeled `kind/simplification` or `kind/architecture`, or a request to refactor; or new or changed behavior.
- **The starting state:** record `git status`. Changes already in the working tree are not part of this work: leave them as they are, and keep a list of the files this run changes.
- **The branch:** when the user wants a pull request and the current branch is the base branch, create a branch for this work before changing anything, named after the ticket or the change in the repository's usual style.

Done when you have the intent with its acceptance criteria, its kind, the starting state, and the branch.

## 2. Build it

For new or changed behavior:

1. When the work adds or changes an interface, run the `design-interface` skill with the intent. When it reports that the design cannot go on, stop: the report says what blocks it.
2. When the work adds or changes a user interface, run steps 1 to 6 of the `design-ui` skill with the intent.
3. Run the `tdd` skill with the contract, from `design-interface` or from the existing interface, the cases the UI contract hands to tests, and the intent.
4. When `design-ui` ran, run its step 7 on the built interface.

For a defect, run the `diagnose-bug` skill on the report. It verifies the defect through `verify-bug`, finds the cause, and fixes it behind a regression test. When the verdict is anything but "holds", stop and report the verdict with its evidence.

For a change of structure only, run the `refactor` skill with the intent. When it reports that the target makes nothing disappear, or reverts the restructuring, stop: its report says why.

Done when the build reports that every case passed after failing first, and `design-ui`, when it ran, that every check of the built interface passed or is listed as not checked; that the defect's red command passes with its regression test; or that the refactor passes its pin with something gone.

## 3. Simplify it

Run the `simplify-change` skill with the files this run changed as its scope, and the intent. From its report:

- a suspected defect inside this work is checked with the `verify-bug` skill, and fixed as step 5 fixes a defect when it holds;
- the tests that skipped candidates need, the proposals beyond the change, and the behavior changes go to the final report.

Done when `simplify-change` has reported, and each defect it raised is fixed or in the report.

## 4. Check the trace

This work carries out decisions; it writes and changes no decision note, since a proposal belongs to planning and the other notes are frozen.

- Code this work wrote whose shape the accepted note explains cites that note, as the `decision-notes` skill describes for citing notes from code.
- A conflict between this work and an accepted note, and a choice that is hard to reverse and that no note settles, go to the report as open decisions for planning. The work keeps to the accepted notes meanwhile.

Done when every citation is in place, every open decision is in the report, and the `decision-notes` verifier passes with `--base`.

## 5. Review it

The review belongs to the repository: the skill in its skill directory whose name ends in `-code-review`, which the `setup-code-review` skill builds from the project's rules and the failures it has had. `setup-code-review` itself does not count, and neither does `deep-code-review`, which only the user starts. Run the review on this work: the files this run changed, or the commits it made, with the IDs of the ticket and the decision note, and the pull request description when one exists. When the repository has no such skill, the work stays unreviewed: say so in the report, and recommend `setup-code-review`, which needs the user's priorities.

Verify the findings with the `verify-bug` skill, which hands review findings to fresh verifiers, then act on each verdict:

- **A defect that holds:** write a test that fails on it, by the rules for a test in the `tdd` skill, then fix the code, and watch the test pass.
- **A rule violation that holds:** fix it, and run the narrowest checks for the files it touches.
- **A design judgment whose facts hold:** apply it when the fix stays inside this work and keeps its behavior, judged as `simplify-change` judges a candidate; otherwise it goes to the report.
- **Does not hold:** the report, with the evidence and the check that produced the finding.
- **Unconfirmed:** the report, with what would settle it.

When fixes changed code, review again, until a round finds nothing that holds, and at most three rounds in all. What remains goes to the report.

Done when every finding of the last round has a verdict and an outcome.

## 6. Finish

Run the checks for the whole of this work: the narrowest checks of the check table for every file this run changed, selected as step 3 of the `pre-push-checks` skill selects them, which includes the `decision-notes` verifier when a citation changed. When the CI line says that nothing runs the full suite, run the full suite once as well. Fix a failure this work caused by the rules of step 5; a failure that also happens at the merge base, found as step 4 of `pre-push-checks` finds it, goes to the report.

When the user asked for a commit, commit the files this run changed through the `commit` skill, naming them so that the changes that were there before stay out. When the user asked for a pull request, open it through the `pr` skill after the commit. Both skills apply the ticket references of the Tracker line. Otherwise leave the work uncommitted.

Done when the checks pass or each failure is shown to exist at the merge base, and the work is committed where the user asked.

## 7. Report

Report:

- the intent, the ticket or note, and the branch;
- the design: the chosen shape, its assumptions, and its follow-ups, or that the work used an existing interface; and for a user interface, the main tasks with their step counts, each view's focus, the device matrix, and what was not checked;
- the tests: the test list in brief, the injected errors no test caught, the manual checks not made with what to look at, and the coverage of the change or that the project has no coverage tool;
- the simplifications applied, and those skipped, with the reasons;
- the review: each finding with its verdict and outcome, and the number of rounds, or that the repository has no review skill;
- the checks run and their results;
- the decisions left to the user: the open decisions and the conflicts with accepted notes, behavior changes, proposals beyond the change, a coverage tool, missing boundary checks, unconfirmed findings, and the choices `design-interface` made as assumptions;
- the commits and the pull request, or that the work is uncommitted, with its files.

Write it in the conversation's language, by the principles of the `plain-language` skill.

Done when every stage appears in the report with its outcome.
