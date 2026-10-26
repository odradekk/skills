---
name: measure-performance
description: 'Make a performance number trustworthy: plan the measurement, find what limits it, confirm the work ran, and report the runs and their spread. Use when running a benchmark, measuring a speedup, a regression, latency, throughput, or memory, or citing such a number.'
---

# Measure performance

A performance number means something only when you know what it measured, what limits it, and how much it varies between runs. This skill holds every number to that standard. When the repository has its own performance skill, a skill in its skill directory whose name ends in `-performance` other than `measure-performance` and `setup-performance`, take the scenarios and commands from it; the checks below apply to every number they produce.

## 1. Plan the measurement

Before running anything, write down the claim you expect to make, in the words you would ship, such as "opening a 5,000-turn save takes 40% less time at the median", and the plan that tests it:

| Field | What to decide |
|---|---|
| User operation | The action a user waits on, and the observable point at which it is complete |
| Workload | Its dimensions and values, for typical and for heavy use, and its data, by the data rule below |
| Entry path | The production code and the build that ships, and which external boundaries are stubbed |
| Clock | Where timing starts and stops, cold or warm, and what is excluded, such as network latency |
| Memory | The counter and the process, such as the language heap, the process's private memory, or GPU memory; retained, with the intended objects still reachable, or peak, measured apart |
| Verdict | The number of runs, the aggregate, and the difference that counts as real |
| Behavior | The functional tests that must still pass |

The measurement code follows these rules:

- It calls production code through its real entry points. It adds no production export for measurement and no copy of the algorithm it measures. A standard instrumentation hook that changes no behavior, such as a performance mark or an `elementtiming` attribute, may go into product code when the project's measurement rules list it.
- User and production data never appear in fixtures, logs, or reports; take only aggregate characteristics from them, such as sizes and distributions. Shipped content, such as the project's own assets and text, may be used as it is, and a measurement that uses it records its version, since every content change moves the numbers: the commit when the content is committed, and otherwise a hash of each content file the workload reads. Other fixtures come from fixed constants or a seed.
- Both sides get the same input, the same validation, and the same output the user receives. A side that skips work is not comparable.
- A cold run is the cold start users have: a fresh process and a private temporary directory for each sample, and no setup step that warms a cache. Name what still differs from a user's cold start: caches that stay warm anyway, such as the operating system's file cache, and first-run costs that the fresh directory adds and users do not pay, such as creating a profile or initializing storage. Exclude those costs, or say that they are included. Warm runs warm the cache on purpose and say so.
- Measurements run one at a time, on a quiet machine. Check the system load first, and on a laptop the power mode, and record both; when other work cannot stop, alternate the sides so both see the same noise, and say so in the report.

Done when the claim and every field of the plan are written down.

## 2. Check the number

Answer each question with evidence from a run, not from reading the code.

1. **What limits it?** Name the bound: a core, a lock, the disk, the network, the load generator, or a code path. Find it with a profiler or system counters in a run you do not report, since profiling slows the work down, and map the hot spot to source. A large profile or trace goes to a sub-agent when your tools can start one: it loads the artifact into a form it can query, such as one row per sample, and returns the hot path with its source locations. If you cannot say why the number is not twice as good, you do not yet know what you measured.
2. **Did both sides run as users run them?** Release builds, production settings, the same versions and data, and caches as warm or as cold as users see them. A side on default or debug settings compares configurations, not code.
3. **Is it within physical limits?** Compare bytes per second with the disk and network bandwidth, and work per second with the cores. Speeding up a piece that takes 10% of the time can make the whole at most about 11% faster. A result past a limit measured something else: a cache, a no-op, or a bug.
4. **Did anything fail?** Count errors and unsuccessful results, and check that the output is correct, not just present. Rejections are fast; timeouts and retries are slow.
5. **Does it repeat?** Run each side at least five times, alternating A, B, A, B, so warmup and drift favor neither, and report the median and the range. A gap smaller than the spread between runs is no measurable difference. When the call is close, use a rank-sum test or the harness's own statistics. A stored baseline from an earlier run is not one of the sides: it shows drift over time, while a comparison runs both sides now.
6. **Does it matter end to end?** Next to a result for one component, measure the whole operation the user waits on, and give the component's share of it.
7. **Did the work happen?** Confirm that the work ran inside the timed region: the request arrived, the rows were written, the result was used. Lazy evaluation, tasks nobody awaits, results the compiler can discard, and timeouts all produce numbers for work that never ran.

For a quick estimate the user asked for, one run is enough. Still answer questions 4 and 7, and say that it was one run.

Done when every question has an answer from a run, or is named as a gap.

## 3. Report

Lead with the verdict: **faster**, **slower**, **no measurable difference**, or **inconclusive**. The verdict is inconclusive when the limiter is unknown, a side ran with settings users do not have, or question 4 or 7 has no answer; name the gap.

Then give the number with its unit, the runs, the range, and the limiter, such as "p50 41 ms → 33 ms, median of 7 runs per side, range 32–35 ms after, bound by JSON parsing on one core". Keep the raw samples, the command, the commit and whether the working tree had uncommitted changes, and the platform where the report can link to them: the measurement's own report output, or a file in a temporary directory. Keep earlier or author-reported numbers apart from fresh ones; an old number is a lead, not evidence.

A pull request description gives one primary number and links the rest.
