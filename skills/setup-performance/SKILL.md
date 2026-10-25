---
name: setup-performance
description: Create or refresh a repository's performance system, made of scenarios that guard the user operations whose speed or memory matters, measurement code kept as maintained infrastructure under written rules, and a project skill for measuring and optimizing them. Use when the user asks to set up performance testing or a project performance skill, or to update them after the project changes.
---

# Set up project performance

What to measure, on which workloads, with which tools, and how much noise is normal are facts of one project. This skill settles them once with the user, builds the measurement code for them, and writes them into a project skill, so that each later optimization starts from a measurement instead of a plan. It produces three things:

- **A decision note** of class `testing`, cited by its ID: the operations guarded and why, their workloads and targets, the options weighed, and where budgets are enforced. It records the choices and the reasons.
- **The measurement infrastructure:** the scenarios, the code they share, and an `AGENTS.md` in the measurement directory that owns the layout and the rules for changing it. Measurement code is project infrastructure, held to the same standards as product code: one place, one way to run it, no copies, and no change without a reason.
- **The project skill `<repo>-performance`**, named after the repository's directory in lowercase, such as `rpgx-performance`. It lives at `.agents/skills/<repo>-performance/SKILL.md` and is committed with the code. It points to the scenarios, the rules, and the note, and carries the optimization loop.

## 1. Read the settings

Read the repository's `## Agent workflow` section: base branch, CI, the table of narrowest checks, Tracker, Labels, File size, Decision notes, and Prose. If the section is missing, run the `setup-agent-workflow` skill first.

When the repository already has its own performance skill, found by the rule in the `measure-performance` skill, this run is a refresh. The skill's last line records the commit its sources were checked up to, and the uncommitted paths that were part of them; steps 2 and 3 cover what changed since that commit, recheck those paths as they stand now, and step 3 audits the infrastructure.

The grill and the report use the conversation's language. The files this skill writes use the language the `Decision notes` line names.

## 2. Find the operations that matter

Find the operations whose speed or memory users notice, such as startup, loading and saving, a frame, a request, a search, or a batch job. Gather the evidence for each from:

- the code's entry points and its heaviest paths;
- the size of what users load or process, and its growth over the history and into the working tree: bundles, assets, data files, saved state;
- configuration that raises or silences a limit, such as a bundle size warning, a timeout, or a memory cap, and comments that describe a workaround for slowness;
- plans in documents, decision notes, and issues that multiply a cost driver, such as more content, records, or users; these also set the heavy workload;
- commits and pull requests that fixed slowness or a regression, found by searching in every language the repository uses, for words such as slow, perf, lag, timeout, and memory, and their equivalents, such as 慢, 卡, 性能, and 内存.

A quick measurement outside the repository, such as a few timed runs against an existing build from a temporary directory, is allowed here. Its numbers, like those in the history, are leads, not evidence.

Judge each operation on its own evidence. **Evidence of slowness** is a report of slowness from a user or a commit, code that works around slowness, or a limit raised or silenced without a stated reason that it is harmless. **Structural evidence** is everything else: sizes, growth, plans that multiply a cost driver, and limits raised for a stated harmless reason. When no operation has evidence of either kind and the user names none, say so and stop: a project without a performance-sensitive path needs no performance system. Whether to guard an operation that has only structural evidence is the user's call, asked in step 4.

Done when every candidate operation has its evidence and its kind of evidence, or you have stopped.

## 3. Take stock of the measurement code

List every piece of measurement code already in the repository: benchmark suites, profiling scripts, timing inside tests, CI jobs that measure, fixture generators, and reports. For each one, record what it measures, how it runs, what runs it, and whether it still works, by running it. List the tools that work here too: the profilers for the language and runtime, the test runner's benchmark support, the CI runners, and, for code that runs in a browser or on a device, the browsers or devices available and how to drive them.

What exists comes first. When one suite exists, new scenarios extend it. When several overlap, the plan merges them before anything is added.

On a refresh, audit the infrastructure against its `AGENTS.md`, and record each finding with a proposed fix:

- a scenario whose user operation or code path no longer exists;
- two scenarios that measure the same operation on the same workload;
- support code copied between scenarios;
- fixtures that nothing uses;
- a budget far above the measured values, so it can never fail, or so close to them that noise fails it;
- a baseline older than the latest change to the code path or the content it measures;
- measurement code outside the measurement directory, other than the module diagnostics its rules allow, and code that breaks its rules.

Done when every piece of measurement code is listed with its state, and, on a refresh, every audit finding has a proposed fix.

## 4. Settle the plan with the user

These defaults need no question; the decision note states them, and the user can change them later:

- The measurement code follows the rules of [references/measurement-agents-template.md](references/measurement-agents-template.md).
- Every number follows the `measure-performance` skill.
- A first setup guards at most three operations; a refresh can add more.
- A target can start as "no slower than the unchanged code beyond the noise". An absolute target follows the first baseline, taken from an established threshold where one exists, such as the web performance thresholds for pages.
- A budget is enforced only when the user says so, and only after it is calibrated on the machine that enforces it: the CI runner, or a named reference machine for local runs.

Run the `grill` skill with:

- **Topic:** what this repository's performance system must protect.
- **Settled ground:** the defaults above, the candidate operations with their evidence and its kind, the inventory and audit from step 3, and the tools.
- **Required answers:**
  - which operations to guard, including whether to guard each one that has only structural evidence; the observable point at which each one is complete; and which one to build first;
  - the workloads for each, typical and heavy, with the dimensions that drive the cost, such as size, count, or cache state, and their data: the shipped content as it is, a frozen copy, synthetic data, or a mix;
  - the metric for each, such as latency, throughput, or memory, and its target;
  - for code that runs in a browser or on a device, which ones the scenarios run on;
  - the behavior differences that are acceptable in an optimization;
  - the instrumentation hooks that product code may carry for measurement, such as performance marks, or none;
  - where the measurement code lives, how it runs, and where its dependencies go, or which existing suite to extend or merge;
  - where the baselines live, and whether they are committed;
  - with CI, whether CI runs the scenarios, and whether it enforces budgets or only reports; without CI, whether the scenarios run locally only and on which reference machine, or whether to add CI, which is a `process` decision of its own;
  - the options weighed for the layout and the tools, and why each one lost;
  - the fix for each audit finding.
- **Reader:** the people and agents who measure and optimize this repository.

Done when the user has confirmed the grill record.

## 5. Record the decision and plan the build

Write the note with the `decision-notes` skill in `proposed/testing/`, from the grill record: the operations and why, the workloads, metrics and targets, the CI or reference-machine decision, what the measurements exclude, how budgets are calibrated, and the alternatives. The details of the layout are left to the measurement rules from step 6. On a refresh, update the existing note instead.

This run builds the shared parts, the rules, and the scenario for the operation the grill record puts first. The shared parts are the run command, the reporting function, and any support code that two or more planned scenarios need, such as the driver for a browser. Each further scenario is built in this run too when it needs nothing beyond its own scenario directory and the shared parts; the row, target, baseline, and check that every scenario adds elsewhere do not count. A scenario that needs more, such as a new tool or dependency, or a change to product code, becomes a ticket.

Draft those tickets with the `note-to-tickets` skill and get them approved, but publish them only after step 6, once the setup change is committed, so they point at rules and code that others can read. The note's acceptance criteria that this run meets need no ticket, and the tickets cite the measurement `AGENTS.md` for the layout.

Done when the note is written, and every guarded operation is either planned for this run or has an approved ticket draft.

## 6. Build the infrastructure

1. **Write the rules first.** Fill in [references/measurement-agents-template.md](references/measurement-agents-template.md) as the measurement directory's `AGENTS.md`, so the code that follows obeys it. When the repository's `CLAUDE.md` is a symlink to `AGENTS.md` or only imports it, put a `CLAUDE.md` of the same kind beside the new `AGENTS.md`, so that Claude Code reads these rules too.
2. **Bring the directory under the project's checks:** add it to the lint and type check configuration and to the test command, and keep its files within the file size limit. When no `area/*` label covers it, add one to the Labels line and to the tracker, as the labels reference of the `setup-agent-workflow` skill describes for a refresh.
3. **Build the shared parts once,** or reuse the existing ones: the run command, which takes a scenario name and a number of samples; the reporting function that every scenario goes through; and the shared support code from step 5.
4. **Write each scenario,** with its plan by the fields of the `measure-performance` skill in the place the rules name.
5. **Prove each scenario:**
   - it tells the heavy workload from the typical one, along a cost dimension the evidence names, such as size or cache state;
   - with the cost it guards against injected temporarily, such as a delay in the measured path for a time metric, or extra retained memory for a memory metric, its result moves past the noise, or its budget fails. Record in the scenario's plan where the cost was injected, then remove it;
   - its noise is known: the spread between runs, measured by the `measure-performance` skill;
   - it runs through the run command.
6. **Record the baselines** in the baseline location from the rules, with everything the rules require a baseline to record. Take again, or mark as such, a baseline taken while the machine was busy. A budget is set from repeated runs on the machine that enforces it, above the measured noise.
7. **Add rows to the check table** in the Agent workflow section, and run each once to prove it:
   - for changes under the measurement directory: the type check, the tests of the support code, and one sample of each affected scenario;
   - for changes to the code paths and the content that a scenario guards: one sample of that scenario, compared with its baseline and reported, not enforced.

When no ticket remains, finish the note with the "Implement a proposal" procedure of the `decision-notes` skill; otherwise the change that completes the last ticket does it. Leave the changes uncommitted unless the user asked for a commit. Then commit them with the `commit` skill, apart from any optimization, and publish the ticket drafts from step 5.

Done when every scenario built in this run runs through the run command, has passed its proofs, and has a recorded baseline and noise.

## 7. Write the skill

Fill in [references/performance-skill-template.md](references/performance-skill-template.md):

- **Scenarios:** each guarded operation with its scenario, the paths and content it guards, its command, metric, baseline location, and where it runs; an operation still waiting on a ticket keeps its row with that ticket.
- **Finding the limiter:** the profiling commands, or procedures such as a browser's performance panel, that work in this repository, each one tried once.
- **Behavior that must hold:** the functional tests for each guarded operation, or "none: check by hand" with what to check, which names the gap.
- The last line records the current commit, and the uncommitted paths that were part of what you checked, if any.

Numbers stay in the measurement code and its baselines, where they change with the code; the skill points to them. Write the skill in the language the `Decision notes` line names, translating the template's headings and text, and keep the front matter keys, commands, paths, and code as they are. Revise it with the `plain-language` skill, then show it, or on a refresh show the changes, and write it only after the user approves.

## 8. Report

State the files written; each scenario with its baseline and noise; the tickets, published or still waiting on the commit; the changes to labels and checks; the audit findings and what was done about each; and the operations considered and left out, and why.
