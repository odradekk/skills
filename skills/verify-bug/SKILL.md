---
name: verify-bug
description: Decide whether a claimed bug is real before anyone fixes it, by reproducing it with a command that goes red on the current code or by showing the evidence that it cannot happen. Use on code review findings, bug reports, and tickets that claim a defect, and when another skill must check such claims before acting on them.
---

# Verify bug

A claim is not a bug until evidence shows it, and a claim nobody could reproduce is not refuted until evidence shows that too. Each claim ends with one of three verdicts, holds, does not hold, or unconfirmed, backed by the evidence that verdict requires. Weigh only evidence: a command and its output, a code path, the text of a rule. How sure the reviewer sounded and what the author meant to write count for nothing.

This skill changes no product code; it writes reproductions. Scripts go to a temporary directory: the scratchpad directory your harness provides, if any, or else a `verify-bug/` folder in the system temp directory. A test goes into the project's test tree when the test runner needs it there.

Redact everything you show: write `<REDACTED>` in place of every secret, keep credentials in environment variables instead of in commands, and quote only the lines of a captured request or log that carry the signal.

## 1. List the claims

Split the input into claims of one defect each; a finding that names two defects becomes two claims. For each claim, write down:

- **Location:** the file and lines, or the endpoint, command, or screen.
- **Trigger:** the input, state, or sequence of events that causes the defect.
- **Symptom:** what goes wrong: the error, the wrong output, the lost data, the slow step.
- **Kind:** one of the kinds in step 3.

When a claim leaves out the trigger or the symptom, write the most specific version that the claim and the code support. A claim too vague for that is unconfirmed; say what it would need to state.

Done when every claim has a location, a trigger, a symptom, and a kind.

## 2. Hand the claims to fresh verifiers

Claims from a code review, and any batch of several claims, go to fresh sub-agents when your tools can start them, on the most capable model available: a wrong verdict costs a wrong fix or a missed bug. Give each verifier this skill's path, its claim from step 1, and the constraints, such as uncommitted changes that are not part of the claim; the conversation that produced the code and the review's reasoning stay out. Each verifier carries out steps 3 and 4 for its claim and returns the verdict in the form of step 5.

Start one verifier per claim that needs a reproduction. Run them in parallel when their reproductions share no files and no running services, such as a port or a database, and one after another otherwise. Check yourself the claims that reading settles, facts about the code and rule violations, and a single bug that the user reports. Without sub-agents, verify every claim yourself and say in the report that verification ran in the same context as the code or the review.

## 3. Gather the evidence

| Kind | Evidence |
|---|---|
| Behavior: a crash, wrong output, lost or corrupted data | A reproduction that drives the real code path with the trigger and asserts the symptom |
| Concurrency or timing | The same, under controlled scheduling or repeated until the failure rate is high and stable |
| Performance | A measurement of the baseline and the trigger by the `measure-performance` skill, with the project's own scenarios when it has them; it is red when the verdict is slower |
| A fact about the code, such as "never called", "unreachable", or "not validated" | The search, and the code path with its paths and lines |
| A rule violation | The rule's text and source, and the code that breaks it |
| A design judgment, such as a finding from `deep-code-review` | Not reproducible. Check the facts it rests on, such as that the duplication exists or that the cited tests pin the behavior, and leave the judgment to the user |

For a reproduction, take the first of these that reaches the code path:

1. A failing test at the seam that reaches the location: unit, integration, or end to end.
2. A request or script against a running development build.
3. A command-line run with a fixture input, compared with known-good output.
4. A headless browser script that drives the UI and asserts on the page, the console, or the network.
5. A captured request, payload, or event log, replayed through the code path.
6. A throwaway harness: the smallest part of the system that runs the code path, with its dependencies stubbed.
7. A property or fuzz loop, for output that is wrong only sometimes.
8. A differential run: the same input through the old and the new version, or through two configurations, with the outputs compared.
9. A human-in-the-loop script, when a person must act: copy [scripts/hitl-loop.template.sh](scripts/hitl-loop.template.sh) to the temporary directory and edit its steps, so the instructions and the answers stay structured.

A reproduction is **red** when it:

- drives the real code path with the trigger and fails with the claimed symptom, not with a different failure nearby;
- has been run, and you have its command and redacted output;
- gives the same result on every run, or, for a flaky failure, fails at a stated rate high enough to work against;
- runs without a person, or through the human-in-the-loop script.

Once it is red, shrink it: cut inputs, callers, configuration, and steps one at a time, rerunning after each cut, until removing any remaining element turns it green. When the claim is about a change, also run the reproduction on the base commit, in a separate worktree, to tell whether the change introduced the defect or exposed an older one.

Done when every claim has the evidence its kind requires, or a record of what you tried and what stopped you.

## 4. Reach a verdict

- **Holds:** the reproduction is red, or, for a fact or a rule, the code shows it. When the real impact differs from the claimed one, such as a narrower trigger or a worse consequence, state the real one.
- **Does not hold:** the evidence rules the defect out. That evidence is the code path that keeps the trigger from reaching the location, such as a type, a validation, or the only callers; a source stating that the behavior is intended; or a reproduction that sets up the claimed trigger exactly and passes. A passing reproduction counts only once you have shown that it reached the location with the trigger, for example with a temporary assertion there.
- **Unconfirmed:** the evidence settles neither way. State what is missing, such as access to an environment where it happens, a captured log or request, permission for temporary instrumentation there, or a decision on what the intended behavior is.

Done when every claim has one verdict and the evidence that verdict requires.

## 5. Report

For each claim, give the claim in one line, the verdict, the evidence, and the impact as found. Add:

- **For a claim that holds:** the red command, where the reproduction lives, and whether the base commit has the defect too.
- **For a claim that does not hold** and came from a review skill generated by `setup-code-review`: the check that produced it, so the next refresh can tighten or drop that check.
- **For an unconfirmed claim:** what the user could provide to settle it.

List the claims that hold first, by impact, then the unconfirmed ones, then the ones that do not hold. Write the report in the conversation's language, by the principles of the `plain-language` skill.

Then remove the temporary assertions, the worktrees you added, and the reproductions you added to the test tree for claims that did not hold or stayed unconfirmed. Leave each red reproduction in place, uncommitted: it is where the fix starts, through the `diagnose-bug` skill when the reproduction does not make the cause plain.

Done when the report is given and the working tree holds no leftovers from verification except the red reproductions.
