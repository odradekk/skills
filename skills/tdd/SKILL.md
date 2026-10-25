---
name: tdd
description: Build behavior test-first against a settled interface, with a test list derived from the contract, one test at a time seen to fail because the behavior is missing and then made to pass, and completion only when every contract item has a test, the changed code is covered, and errors injected into its boundaries and fixed numbers make a test fail. Use when implementing a feature or a change of behavior, when the user asks for TDD or test-first work, and when another skill needs tests written; its rules for a test apply to every test the other skills write.
---

# TDD

The red-green loop is the easy part. The quality of test-driven work is decided around it: by the interface, and by which cases get a test. This skill derives the cases from the contract, so the tests cover what the interface promises, its boundaries and fixed numbers included, and nothing it rules out. It runs the loop one case at a time, and it finishes only when checks show that the tests would catch a wrong implementation.

Cleanup after green, such as removing duplication or extras, belongs to the `simplify-change` skill, which runs these tests as its proof. A bug fix starts from the `diagnose-bug` skill instead, and a change of structure only from the `refactor` skill.

The skill runs without stopping for anyone, so that it can be one step of a longer workflow: what it cannot do or decide itself goes into its report.

## 1. Start from the contract

Read the repository's `## Agent workflow` section: Decision notes, and the check table with its test commands. If the section is missing, find the test commands in the manifests for this run only, and say so in the report.

- **The contract:** the one the `design-interface` skill wrote, when the work adds or changes an interface. Otherwise the existing interface: its types, its documentation, and its tests, together with the intent, such as the ticket, the acceptance criteria of a decision note, or the request. When the work needs an interface that does not exist yet or must change, run `design-interface` first.
- **The project's testing rules:** the accepted decision notes of class `testing` that touch the area, and the testing documents the repository's `AGENTS.md` files point to. They are constraints on the test tier, the seam, the stand-ins, and the tools: a case they require, such as a snapshot or a browser test, goes on the test list, and a conflict between them and the work goes to the report.
- **The existing tests** at the seams the work touches: where they live, how they are named, which fixtures and data builders they use, and which behavior they already cover. Follow the conventions of a test that meets the rules in step 3, not merely of the nearest one.
- **The checks:** run the narrowest automated checks for the area now. They must pass, so that each failing test afterwards fails because of the new test. A check that the table describes as a manual procedure, such as opening a page, runs for the manual cases in step 4.

Done when you have the contract, the testing rules that apply, the seams where the tests go, and passing automated checks.

## 2. Write the test list

Turn the contract into a list of cases. Each case is one behavior a caller can observe, with the contract item it comes from and the seam it is tested at. Derive the cases from the contract, not from the implementation you have in mind:

- **Each input's data definition:** one case for each variant of a union or an enumeration; both ends of each interval, and the value just past each end when an input can reach it; empty, one, and many for a collection; for a recursive structure, the base case and a case at least two levels deep.
- **Each result** the purpose statement promises: a worked example whose expected value is computed by hand from the intent.
- **Each number the rule itself fixes,** such as a cap, a rate, or a formula the intent states: a case at the number, and a case on each side of a threshold, with literal expected values worked out by hand.
- **Each piece of tunable data the code reads,** such as thresholds in a content or configuration file: the rule applied to the data, with cases built from the data itself, such as each entry's threshold and the value just below it, which the test reads as input. The data's invariants, such as ascending order, get a case in the project's check of its content. Data moved from one place to another gets one comparison of the old values with the new.
- **Each promised error, each required order of calls, and each effect:** a case that triggers it, checking the effect through the interface.
- **Each state transition:** the transition, and each transition the interface refuses.
- **Each requirement or acceptance criterion** of the intent: at least one case. A requirement without a case is a gap in the list.

A requirement the project cannot test automatically is still a case, marked as one of two kinds: a **manual check**, such as text on a page in a project without interface tests, or a **structural check**, such as a search showing that something no longer exists in a directory.

Leave out:

- inputs that the types or the validation at the system boundary already rule out. That validation gets its cases once, at the boundary, with the outside data it receives;
- the behavior of the language, the framework, and the dependencies;
- the current values of tunable data, and literal tables and mappings in general, unless the mapping is itself the contract: a test that copies a value from a table only repeats it, and fails at every adjustment;
- incidental details, such as log text, the calls made to collaborators, and internal state, unless the contract names them;
- a case that another test already covers at the same seam.

Order the list so that each case builds on the one before: the simplest typical case first, then the other variants, then the boundaries and errors.

Done when every contract item has at least one case, and every case names its contract item, its seam, and its kind when it is not automated.

## 3. The rules for a test

These rules apply to every test written in this skill, and to every test the other skills write, such as the regression test of `diagnose-bug`. A test that breaks one is fixed or removed, even when it passes.

- **Through the interface.** The test calls the module the way callers do and checks what callers observe. When a behavior can be checked only by reaching inside, the interface has the wrong shape: return to the `design-interface` skill.
- **Expected values from an independent source:** a value worked out by hand from the intent, a known-good literal, or the specification. A value obtained by running the code, or computed in the test the same way the code computes it, checks nothing. Reading tunable data into the test as input is allowed; repeating the rule in the test to compute the expected value is not. In a refactor, the code before the change is the independent source, so a characterization test may record what it returns, as the `refactor` skill describes.
- **Stand-ins by dependency category,** as the `design-interface` skill sorts them: in-process dependencies run for real; a dependency with a local substitute runs that substitute; a service the project owns across a process or the network is replaced by an in-memory adapter at its port; only a third-party service gets a fake. The project's own modules are never mocked.
- **One behavior per test,** named for what a caller observes, such as "a located captive can be rescued", not for how the code works.
- **Deterministic:** time, random numbers, the filesystem, and the network are pinned or isolated.
- **Survives a refactor:** the test fails only when observable behavior changes. When a test at a deeper interface covers the same behavior as an older test at a shallower one, delete the older test instead of keeping both.

## 4. Run the loop

For each automated case on the list, in order:

1. Write its test.
2. Run it, and watch it fail because the behavior is missing: an assertion on the expected value, the stub's not-implemented error, or the crash this case is meant to fix. A missing import, a typo, or a failure in the setup is not that failure: fix the test and run it again. A test that passes at once has three possible explanations: an earlier case already covers it; the test does not reach the behavior; or the code written for an earlier case is more general than that case needed. Fix the list or the test for the first two. For the third, keep the test only when the error injected at its boundary in step 5 makes it fail.
3. Write the least code behind the interface that makes it pass. Code for a case that is not on the list waits until the case is added to the list.
4. Run it together with the tests before it; all of them pass.

For a manual check, look at the behavior before the change, where the old behavior plays the part of the failure, and again after it. A manual check you cannot make yourself, such as one that needs a device or a browser you do not have, is listed as not checked, with what to look at, and the loop goes on. For a structural check, run the search before the change, when it finds what is to go, and after, when it finds nothing. A check of shipped content passes at once, since the content starts out right; step 5 proves it by injecting a violation into the content.

Once a test has failed because the behavior was missing, the code changes to meet it, never the other way round. Change an expected value only when working the case out by hand again gives the new value, and record why. Weaken no assertion, and skip or delete no test, to reach green.

When the implementation keeps meeting the same kind of friction, stop and return to the `design-interface` skill, as its last step describes.

Done when every automated case has passed after failing because the behavior was missing, and every manual and structural check has been made before and after, or listed as not checked.

## 5. Check the tests

Passing tests do not yet show that they would catch a wrong implementation. Make these checks:

1. **Trace both ways.** Every contract item has a case, and every test belongs to a case on the list. A test without a contract item is removed, or the contract item it reveals is added to the list, with the reason.
2. **Cover the change.** When the check table or the test runner provides coverage, run the tests with it: every changed production line and branch is run by a test. A line that no test runs is code nothing asked for, which you remove; a missing case, which you add; or an exception, such as code that connects to the UI and is checked by hand, which the report names with its reason. Without a coverage tool, say so in the report, and propose adding one as a coverage command in the check table. Install nothing: choosing a test dependency is a `testing` decision, so it goes to the report as an open decision for planning, where the user may make it a proposal.
3. **Inject errors.** For each boundary and each number the rule fixes in the changed code, make it wrong for a moment: move a comparison by one, such as `>=` to `>`; change the constant; invert the condition; delete the branch. Run the tests: at least one must fail. An injected error that no test catches is a missing case, which you add, or code that nothing needs, which you remove. When the project has a mutation testing tool, such as Stryker, mutmut, or cargo-mutants, run it on the changed files instead, and treat each surviving mutant the same way.
   - Tunable data is the exception: the tests read it as input, so changing a value keeps them passing, and the report says so. The data's invariants are proven instead by injecting a violation into the data, such as swapping two rows, and watching the content check fail.
   - Make each injection with an edit that keeps the file's line endings, and check that it applied: an edit that matched nothing proves nothing. Save the diff of the working tree before the first injection, and compare it with the diff after the last, so that no injected error remains even when the tree had other changes.

Done when every check passes, or each gap is in the report with its reason.

## 6. Report

Report:

- the test list, with each case's contract item, seam, kind, and test;
- for each automated case, the failure it produced before its code existed, and for each manual or structural check, what it showed before and after, or what to look at when it was not checked;
- each expected value that changed, and why;
- the coverage of the change and its exceptions, or that the project has no coverage tool;
- each injected error and the test that caught it, each one no test caught, with what was done, and the tunable data the tests read as input;
- the checks run, and the deviations from the design found during the loop.

Leave the changes uncommitted unless the user asked for a commit. The usual next steps, which the `implement` skill runs, are the `simplify-change` skill on this change, then the repository's review.

When another skill called this one, return the report to it. Otherwise write it in the conversation's language, by the principles of the `plain-language` skill.

Done when the report covers every case on the list and every check.
