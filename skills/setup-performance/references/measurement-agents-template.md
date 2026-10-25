# Template for the measurement directory's AGENTS.md

Replace every `<placeholder>` and translate the headings and text into the language of the repository's decision notes. The grill record settles the operations, the dependency home, the data, the instrumentation hooks, the baselines, and the budgets. The rest you choose while building, following the project's own naming conventions, and record here and nowhere else: the name patterns, how measurement code loads product code, the reporting function and its output, where each scenario's plan lives, the support, fixture, and test locations, and the check commands. Where the template offers `<one form | another>`, keep the form the grill record chose. Keep every rule unless the grill record says otherwise; a rule the project cannot follow yet stays, marked with the ticket that will make it true.

````markdown
# Performance measurements

This directory holds the scenarios that guard <repo>'s <operations>. It was set up with the `setup-performance` skill; the reasons for its workloads, targets, and budgets are in decision note `<note ID>`. Treat it as project infrastructure: changes here are reviewed, tested, and kept as clean as product code.

## Layout

- One directory per user operation, named after the operation, not after the source tree, such as `<example directory>`.
- Scenario files are named `<scenario pattern>`. Support, fixture, and worker files carry no scenario suffix.
- A diagnostic for one module lives beside that module as `<diagnostic pattern>` and is not part of the scenario run.
- Measurement-only dependencies belong to `<package or dependency group>`, or, where the package manager has no such groups, to this list: <dependencies>. A new measurement framework or dependency needs a decision note first.

## Running

- `<command>` runs every scenario, `<command for one scenario>` runs one, and `<samples option>` sets the number of samples. The runner finds scenarios by their name pattern in this directory only.
- Measurement code loads product code <how, such as through the shipped build or the bundler's module loader>.
- Every scenario reports through `<reporting function>`. It takes what the scenario measures and the user operation it affects, and writes `<report output>`.
- Measurements run one at a time; nothing else that is CPU-heavy runs beside them.

## Adding and changing

- **Look before adding.** Before adding a scenario, find the one that measures the same user operation, and add a workload to it instead. A new scenario needs a target in decision note `<note ID>`; a new target needs the user's approval and an update to the note.
- **State the plan.** Each scenario states its plan, by the fields of the `measure-performance` skill, in <where the plan lives>, including where its reverse validation injected the cost.
- **Share only what is shared.** Support code stays beside its scenario until a second scenario needs the same behavior. Then it moves to `<support directory>`, and both use it.
- **Measure the real thing.** Call production code through its real entry points, in the build that ships. Add no production export for measurement, copy no product algorithm, and leave functional assertions to the functional tests. Product code may carry only these instrumentation hooks, which change no behavior: <hooks, or "none">.
- **Data.** User and production data never appear in fixtures, logs, or reports. <Shipped content, such as `<content paths>`, is used as it is.> <Other fixtures come from fixed constants or a seed in `<fixture location>`.> Nothing comes from the network or from files outside the repository.
- **Baselines** live in `<baseline location>`, <committed | not committed>. Each one records the commit; whether the working tree had uncommitted changes; the content version where shipped content is used, which is the commit when the content is committed and otherwise a hash of each content file the workload reads; the machine, its power mode, and its load during the run; the runtime or browser version; and the number of runs, the median, and the range. A baseline taken while the machine was busy is taken again, or marked as such. A stored baseline shows drift over time; a change is judged by alternating runs of the code with and without it.
- **Keep numbers comparable.** A change to what a scenario measures, such as its workload, its timing boundary, or its completion point, makes old and new numbers incomparable. Commit it apart from any optimization, record the new baseline in the same change, and give the reason in the commit message.
- **Budgets.** <Budgets are reviewed constants in `<budget location>`, calibrated on `<CI runner or reference machine>` and set above the measured noise. Environment variables cannot override them. Change a budget only with the reason and the new measurements, never to let a regression through. | There are no budgets yet; decision note `<note ID>` says what adding one takes.>
- **Remove what is gone.** A scenario whose user operation or code path is removed goes in the same change.
- **Explore outside.** Exploratory scripts and profiles stay outside the repository, in a temporary directory, until the rules above admit them.

## Checks

Code here passes `<lint, type, and test commands>` like product code, and support code with logic, such as statistics or fixture generation, has tests in `<test location>`. The check table in the root `AGENTS.md` names the light check for changes here, and the one-sample runs for changes to the paths each scenario guards.
````
