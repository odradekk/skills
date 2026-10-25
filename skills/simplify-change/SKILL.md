---
name: simplify-change
description: Remove what a change makes the project maintain without needing it, such as parameters nothing passes, fallbacks for cases that cannot occur, copies of code the project already has, and code the change left unused, while its tests show that behavior stays the same. Use after implementing a change and before its review, when the user asks to clean up or simplify a change, and when another skill needs a change simplified.
---

# Simplify change

Code that was just written carries extras: a parameter no caller passes, a fallback for a case that cannot occur, a helper the codebase already has, an old function that nothing calls any more. Each one is something the project must now maintain for no reason. This skill finds them in one change and removes them while keeping its behavior, and the change's own tests are the proof.

It works inside the change. Restructurings that reach beyond it belong to the `deep-code-review` skill, and removals in code the change did not touch to the `find-simplifications` skill. It does not hunt for defects, and it does not chase speed: a candidate whose only gain is speed goes through the `measure-performance` skill before anyone keeps it.

## 1. Set the scope

Read the repository's `## Agent workflow` section: base branch, Decision notes, Labels, and the check table. If the section is missing, find the checks in the manifests for this run only, and say so in the report.

- **The change:** the current branch against its merge base with the base branch, plus uncommitted changes; or the commits or files that the user or the calling skill names. A named scope limits every edit, even when the change is larger.
- **The intent:** the ticket, decision note, or request that the change carries out, and the design documents they cite. It decides what the change must provide: something the change adds that the intent does not call for and nothing uses is a candidate.
- **The checks:** the narrowest checks for the changed files, from the check table. Run the automated ones now. A simplification is proven by checks that stay green, so when they fail, stop and report: the change is not finished. A check that the table describes as a manual procedure, such as opening a page, runs in step 4, for what the applied candidates touch.

Done when you have the changed files, the intent, and passing automated checks.

## 2. Find the candidates

When your tools can start sub-agents, give the search to fresh ones in two cases: the change was written in this conversation, since the context that wrote the code is the one least likely to see what it added without need; or the change is large, such as a thousand changed lines or more, whoever wrote it. A change of a few lines in one file you check yourself. Split a large change by the `area/*` labels from the Labels line, one sub-agent per area, running in parallel. Give each one this skill's path, its part of the diff, and the intent; it returns the candidates and changes nothing. You decide and apply them, since you hold the intent.

Check everything the change adds or edits, its tests included, against these questions:

- **Does anything use it?** A parameter, option, field, or return value that no caller sets or reads; a branch, fallback, retry, or validation for a case that the types, the callers, or an earlier check already rule out; a layer that only forwards calls; a computation whose result nothing uses. Validation where outside data enters the system stays.
- **Did the change leave something unused?** The function, type, file, test helper, configuration key, dependency, or asset, such as an image or a data file, that the change replaced or stopped referencing; and debug output, commented-out code, and temporary files.
- **Does the project already have it?** A helper, type, or constant with the same behavior: search the shared modules and the files beside the change. The same steps written twice in the change, and a stored value that could be derived from another.
- **Is it at the right depth?** A special case added to shared code for one caller, or a check patched in where the cause lies elsewhere. The fix goes to the cause when the cause is inside the change.
- **Is there a simpler form?** A construct that a simpler one with the same behavior replaces, such as nested conditions that an early return flattens.

When the test runner already reports coverage, run the change's tests with coverage, installing nothing for it: a changed line that no test runs is either code nothing needs or a missing test.

For each candidate, record its location as file and lines, what it is, the evidence (the search, the callers, the type that rules a case out), the simpler form, and what disappears. Note also the documents and comments that still name what the change removed or renamed: they are not candidates, but the change left them out.

Done when every file in the change has been checked against every question.

## 3. Decide each candidate

Apply a candidate when all of these hold:

- **The behavior stays the same** for every input the code can receive: the output, the errors, and the side effects.
- **It has proof.**
  - A removal deletes a declaration that nothing uses, such as a parameter, an export, a field, a function, a file, an asset, or a dependency. The search that finds no consumer and checks that still pass prove it.
  - Every other candidate changes which statements run, such as deleting a branch or a check, or replacing code with a simpler form or an existing helper. The tests that run the replaced code prove it. Two kinds need no test: a change to types only, which the type check proves, and a literal replaced by a named constant of the same value, which the constant's definition proves.
  - When no test runs the replaced code, skip the candidate, and report the test it needs and the seam where that test belongs. Writing the test belongs to the work that wrote the code, through the `tdd` skill.
- **It stays inside the scope:** it edits the files of the change, or deletes what the change left unused; with a named scope, only the files in it. A candidate that needs more goes back to whoever named the scope.
- **Nothing outside requires it.** Search the active decision notes and the design documents of the intent for its name, and keep it when an implemented note or the current design requires it. Keep anything others may use without the repository showing it: an export of a package others install, a documented API, a plugin or extension point, a configuration key users set, or a stored or wire format.

Otherwise the candidate goes to the report:

- a restructuring beyond the change, with an offer to record it as a proposed `simplification` note with the `decision-notes` skill;
- a change of behavior, for the user to decide;
- a defect you noticed, as a claim in the form of step 1 of the `verify-bug` skill: location, trigger, symptom, and kind.

Decide candidates that affect each other together. When applying one would block another, such as removing a parameter that a skipped candidate would pass, judge them by the result of both, and report them together.

Drop a candidate that only renames or moves code, or that merges two things meaning different things into one: the reader holds as many concepts as before. List the dropped candidates from a sub-agent with the reason.

## 4. Apply

Apply the accepted candidates, and update what names the removed code: comments, docs, tests, and the implemented decision notes that name it, by the `decision-notes` skill.

Then run the automated checks from step 1 again, adding the narrowest checks for every file you touched, and the manual checks that the table names for what the applied candidates touch: open the pages they reach directly and watch the console. List as not checked a page that needs a particular state to reach, or that writes data the user keeps, such as a save. When a check fails, find the candidate that broke it, reapplying them one at a time if it is not obvious, revert that candidate completely, and move it to the report.

Commit nothing. When the change is still uncommitted, whoever commits it commits the simplifications with it; when it is already committed, the simplifications stay uncommitted for whoever asked, to commit on their own.

Done when every accepted candidate is applied with passing checks, or reverted and reported.

## 5. Report

List:

- the candidates applied, each with its location and what disappeared;
- the candidates skipped or reverted, each with the reason, and the tests that skipped candidates need;
- the proposals beyond the change, the behavior changes for the user to decide, the suspected defects, and the documents the change left out;
- the checks run, their results, and what was not checked;
- whether fresh sub-agents searched, or the search ran in the context that wrote the code.

When another skill called this one, return the report to it. Otherwise write it in the conversation's language, by the principles of the `plain-language` skill.

Done when every candidate appears in the report as applied, skipped, reverted, or passed on.
