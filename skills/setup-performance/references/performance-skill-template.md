# Template for a generated performance skill

Replace every `<placeholder>`, and translate the headings and text into the language of the repository's decision notes. An operation still waiting on its ticket keeps its row: the ticket goes in the Scenario cell, and Run and Baseline hold "—". A cell for a tool or a test may hold a procedure instead of a command, or "none: check by hand" with what to check, which names the gap.

````markdown
---
name: <repo>-performance
description: Measure and optimize <repo> against its guarded scenarios for <operations, briefly>. Use when making <repo> faster or lighter, when checking a performance claim or regression in <repo>, and before changing its measurement code.
---

# <repo> performance

Built with the `setup-performance` skill, which refreshes it. The targets and the reasons behind them are in decision note `<note ID>`, and the rules for measurement code are in [<measurement directory>/AGENTS.md](<relative link>). Every number follows the `measure-performance` skill.

## Scenarios

| User operation | Scenario | Guards | Run | Metric | Baseline | Runs on |
|---|---|---|---|---|---|---|
| <operation> | `<path>`, or <ticket> | `<code paths and content>` | `<command>` | <metric> | `<baseline location>` | <CI, enforcing the budget or reporting only, or locally on the reference machine> |

## Finding the limiter

| Runtime | How | What it shows |
|---|---|---|
| <runtime> | `<command>`, or <procedure> | <what the output shows, and known quirks> |

## Behavior that must hold

| User operation | Functional tests, or what to check by hand |
|---|---|
| <operation> | `<command>`, or none: <what to check by hand> |

## Optimizing

1. **Set the target:** a scenario above and its target in the note, or a number the user gives. An operation without a scenario goes through the measurement rules first: extend a scenario, or ask the user for a new target and refresh with `setup-performance`.
2. **Check the starting point:** run the scenario and its functional tests on the unchanged code, and compare the result with the stored baseline. A large gap means the baseline is stale or the machine differs; settle that before going on.
3. **Find the limiter** with the tools above. Read the decision notes for the area, the rejected ones included, before repeating an attempt.
4. **Write the hypotheses.** Each names a mechanism, such as "the save file is parsed again on every frame". Try them cheapest first: stop work whose result nothing uses; do it once; do less of it; do it later; do it while the user is not waiting; do it concurrently; do it faster.
5. **Change one thing at a time.** After each change, run the functional tests, and compare the code with and without the change by alternating runs, by the `measure-performance` skill. Keep the change only when the difference is past the noise and the tests pass; otherwise revert it completely. Log every attempt, kept or reverted, with its numbers, in a file in a temporary directory. Attempts may be prepared in parallel in separate worktrees, but their measurements run one at a time.
6. **Reject** a change whose gain disappears end to end, that slows a typical workload, whose complexity outweighs its gain, or that changes behavior beyond <the acceptable differences in the note>.
7. **Stop** at the target, or when the remaining ideas are too small to be worth their cost, and list those ideas, ranked.
8. **Deliver.** Each kept change is its own commit, through the `commit` skill; a change to a scenario is a separate commit, with a new baseline, by the measurement rules. The pull request, through the `pr` skill, gives the primary number and the rejected attempts. A rejected idea that others would try again becomes a rejected decision note.

## Regressions

A claim that something in <repo> became slower or uses more memory goes through `verify-bug`, then `diagnose-bug`, with the scenarios above as the reproduction.

Sources checked up to commit `<sha>` (<YYYY-MM-DD>)<, together with uncommitted changes to <paths>>.
````
