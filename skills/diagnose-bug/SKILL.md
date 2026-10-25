---
name: diagnose-bug
description: Find the cause of a bug or performance regression and fix it with a regression test, starting from a reproduction that goes red. Use when the user asks to debug or diagnose something, or reports something broken, failing, or slow.
---

# Diagnose bug

Every step here consumes one thing: a red command, a reproduction that fails on this bug and will pass once it is fixed. With it, each hypothesis can be tested and the fix proven; without it, reading code yields theories that nobody can check. The redaction rule of the `verify-bug` skill applies to everything you show.

## 1. Get a red command

Take it from `verify-bug` when that skill has already run on this bug; otherwise run `verify-bug` on the report first. When the verdict is anything but "holds", stop and report the verdict with its evidence: there is nothing to diagnose yet.

Then make the command **tight**:

- **Faster:** cache the setup, skip unrelated initialization, narrow the test scope.
- **Sharper:** assert the specific symptom, not "did not crash".
- **More deterministic:** pin the time, seed random numbers, isolate the filesystem and the network.

Done when the command runs in seconds and still meets every condition of red in `verify-bug`.

## 2. Hypothesize

Read the decision notes that touch the code in question. An accepted note may explain why the code works the way it does, and a fix that goes against one must say so.

When the bug appeared between two known states, such as two commits, two dependency versions, or two data sets, bisect with the red command first, for example with `git bisect run`. The first bad state narrows every hypothesis.

Write three to five hypotheses and rank them before testing any; a single hypothesis anchors on the first plausible idea. Each one states its prediction: "If X is the cause, then changing Y turns the command green, and changing Z makes it worse." Sharpen or discard a hypothesis that predicts nothing. Show the ranked list to the user before testing, since the user may already have ruled one out, and continue with your ranking unless the user answers first.

Done when the ranked hypotheses, each with its prediction, are shown.

## 3. Instrument

Each probe tests one prediction and changes one variable. Use a debugger or a REPL when the environment has one; otherwise add logs at the boundaries that tell the hypotheses apart, and only there. Tag every temporary log with one unique prefix, such as `[DEBUG-a4f2]`, so a single search finds them all at cleanup.

For a performance regression, measure instead of logging, by the `measure-performance` skill and with the project's own scenarios when it has them: find the limiter with a profiler or a query plan, then bisect.

Done when one hypothesis's prediction held and the others' failed. When every prediction fails, return to step 2 with what the probes showed.

## 4. Fix with a regression test

The regression test needs a correct seam: a place where the test exercises the bug the way it happens at the real call site. A seam that is too shallow, such as a unit test of one caller when the bug needs two, gives false confidence. When no correct seam exists, that is a finding in itself: report it as an open decision for planning, a candidate for a `testing` or `architecture` proposal.

With a correct seam:

1. Turn the shrunk reproduction into a test at that seam, by the rules for a test in the `tdd` skill.
2. Watch it fail.
3. Fix the code.
4. Watch it pass.
5. Run the original red command and watch it pass too.

When the fix goes against an accepted decision note, say so in the report: the note stays as it is, and whether to change the decision is for planning to take up.

## 5. Clean up

Done when:

- the original red command passes;
- the regression test passes, or the missing seam is reported;
- a search for the log prefix finds nothing;
- the throwaway harnesses, and every reproduction that did not become the regression test, are gone from the working tree;
- your report names the cause that turned out to be right, and the commit message or pull request description for the fix names it too, through the `commit` and `pr` skills, so the next person who debugs this code learns it.
