---
name: refactor
description: Change the structure of code without changing its behavior, by pinning the behavior first, naming the structure the code is missing, deleting what nothing uses, moving in small steps that keep the pin passing, and keeping the result only when something disappears. Use when the user asks to refactor, restructure, extract, inline, rename, move, or merge code, for a ticket or decision note of class simplification or architecture, and when another skill needs a change of structure made.
---

# Refactor

A refactor changes the structure and keeps the behavior: callers observe the same results, errors, and effects before and after. It is worth doing only when the new structure makes something disappear, such as branches, invalid states, flags, layers, or copies, so that the next reader has fewer concepts to hold. So the behavior is pinned before anything moves, and the result stays only when the pin still passes and something is gone.

New behavior belongs to the `tdd` skill, and a defect to the `diagnose-bug` skill. When the work mixes them, this skill does the structure first, against the pinned behavior, and reports the rest.

The skill runs without stopping for anyone, so that it can be one step of a longer workflow: what it cannot do or decide itself goes into its report.

## 1. Take the target

Read the repository's `## Agent workflow` section: Decision notes, and the check table. If the section is missing, find the checks in the manifests for this run only, and say so in the report.

- **The intent:** a ticket or decision note of class `simplification` or `architecture`; a finding of the `deep-code-review`, `find-simplifications`, or `improve-architecture` skill; or a request. Read the decision notes and design documents that touch the area: implemented notes and the parts of designs that describe the code as it is are constraints, and rejected notes are guardrails.
- **The area:** the files whose structure changes, and the **surviving seams**: the interfaces that callers use both before and after. The behavior is pinned there.
- **Interfaces with consumers outside the repository,** such as an export of a package others install, a documented API, a plugin or extension point, a configuration key users set, or a stored or wire format, keep their shape: the refactor changes what is behind them. Whether to change such an interface goes to the report, for the user to decide.
- **The checks:** run the narrowest automated checks for the area now. When they fail, stop and report: a refactor starts from passing checks.

Done when you have the intent, the area with its surviving seams, the outside interfaces that keep their shape, and passing checks.

## 2. Pin the behavior

The pin is what shows that the behavior did not change. Type checks and lint are not a pin.

- **Existing tests:** find the tests that run the area through the surviving seams, and keep those that meet the rules for a test in the `tdd` skill.
- **Characterization tests:** where those tests leave a behavior unchecked, add tests at a surviving seam that record what the code does now. In a refactor, the code before the change is the independent source the `tdd` rules ask for, so an expected value may come from running it. Choose the cases the way the `tdd` skill's test list derives them from the data, and cover every path the restructuring will touch.
- **An equivalence check,** when the outputs are too large or too many to assert: run the same inputs through the code at the starting commit, in a separate worktree, and through the changed code, and compare the outputs.
- **A manual check,** for an interface without tests: look at the behavior before the change, and again at the end.

Prove the pin as step 5 of the `tdd` skill proves tests: inject an error into each part of the area that will change, and watch the pin fail; then undo it.

Done when every path the restructuring touches is pinned, and an error injected into each part that will change makes the pin fail.

## 3. Name the target structure

Name the structure the code is missing, such as:

- a state machine in place of scattered flags, phases, and lifecycle checks;
- a typed model in place of loose parameters or the same assumption about a shape repeated across files;
- a table, a registry, or a union of variants in place of branches spread across files;
- one module that owns a body of knowledge, in place of modules split by execution order, such as load, validate, transform, and save;
- one owner for each piece of state, in place of copies kept in step.

Leave code as it is when its shape is already clear, local, and unlikely to grow. Check both the current and the target structure against the flaws in step 5 of the `design-interface` skill. When the target changes an interface between modules, run `design-interface` for it, with the pinned behavior as its contract.

List what the target makes disappear: branches, invalid states, flags, parameters, layers, copies, files, and the concepts a caller must learn. A target that only moves code makes nothing disappear: stop, and report that the refactor is not worth doing.

Done when the target is named and its list of what disappears is not empty.

## 4. Delete first

Before building the new structure, delete in the area what nothing uses, proven as step 4 of the `find-simplifications` skill proves that nothing reaches it; collapse wrappers that have one caller; and remove checks for cases that the types or the callers already rule out. Run the pin after the deletions. They are a step of their own, so that the restructuring starts from the smaller code.

Done when the deletions are made and the pin passes.

## 5. Move in small steps

- Make one move at a time, such as an extraction, an inlining, a rename, a move, or a merge, and run the pin and the type check after each. A step that breaks the pin is undone and taken again in smaller pieces.
- Migrate every caller in the repository in the same change, then delete the old interface. Leave no compatibility layer and no old and new paths side by side, except for the interfaces with outside consumers from step 1, which keep their shape.
- Search a renamed or moved name in every form a consumer could use, as step 4 of `find-simplifications` lists them: string forms, configuration, documentation, decision notes, and `Decision note:` citations.
- Mechanical edits across many files may go to a sub-agent, with a precise scope: the files, the names being moved, and the behavior to keep. Review its diff yourself.
- Keep the tests that check the behavior at the surviving seams. Delete a test of internals that the restructuring removed, once a test at a surviving seam covers the same behavior.

Done when the target structure is reached and the pin passes.

## 6. Prove it and judge it

Run the pin, the equivalence check, the narrowest checks of the check table for every file this run changed, and the manual checks a second time. Then compare the result with the list from step 3: when nothing on it disappeared, revert the restructuring and report why. The deletions of step 4 stand on their own.

A defect found along the way is not fixed here, since fixing it changes behavior: it goes into the report as a claim in the form of step 1 of the `verify-bug` skill.

Done when every check passes and something on the list is gone, or the restructuring is reverted.

## 7. Bring the tests and notes up to date

- **Characterization tests:** keep those that check a behavior callers rely on at a surviving seam, named for that behavior, as regression tests. Delete those that only pin incidental details, by the `tdd` rules.
- **Decision notes:** record a lasting structural decision as an `architecture` note and cite it from the code, as `design-interface` does in its step 7. Update the implemented notes that name what moved or was renamed, as the `decision-notes` skill keeps them current. When this work completes a proposal, carry out the "Implement a proposal" procedure of the `decision-notes` skill.

Done when every characterization test is kept or removed by those rules, and the `decision-notes` verifier passes.

## 8. Report

Report:

- the target, and what disappeared;
- the pin: the tests it used, the characterization tests kept and removed, the equivalence check, and the injected errors with the tests that caught them;
- the steps taken, and any that were undone;
- the outside interfaces that kept their shape, and the defects found, as decisions for the user;
- the checks run and their results, or that the restructuring was reverted, and why;
- the commits, or that the changes are uncommitted.

Leave the changes uncommitted unless the user asked for a commit. When the user did, commit through the `commit` skill as the work goes, so that each commit passes the pin and can be reviewed or reverted on its own: the deletions after step 4, the restructuring after step 6, and the updates to tests and notes after step 7.

When another skill called this one, return the report to it. Otherwise write it in the conversation's language, by the principles of the `plain-language` skill.

Done when the report covers every step.
