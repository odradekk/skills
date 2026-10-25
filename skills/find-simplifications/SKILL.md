---
name: find-simplifications
description: A survey of an area or the whole repository for what the project maintains without needing it, such as features nothing can reach, distinctions no consumer acts on, copies of values it could read, and hand-rolled code a dependency covers, with evidence for every candidate and proposals for the supported ones; started only by the user.
disable-model-invocation: true
---

# Find simplifications

Every API, field, state, configuration option, dependency, test, and document is something the project keeps maintaining: callers must consider it, changes must keep it working, and readers must learn it. This skill surveys an area or the whole repository for what the project could stop maintaining, proves each candidate, and turns the supported ones into proposals. A few well-supported candidates are worth more than a count of deletions; the measure is what the project no longer maintains, not how many lines go.

Every candidate makes something disappear: a feature, a field, a state, a copy, a path, a dependency. A rearrangement that leaves the reader holding the same concepts belongs to the `deep-code-review` skill, and the change at hand to the `simplify-change` skill. This skill reports and proposes, and changes code only when the user asks to implement a candidate.

## 1. Set the scope and read the ground

The scope is the area the user names, or the whole repository. Read the repository's `## Agent workflow` section: Decision notes, Labels, and the check table. If the section is missing, run the `setup-agent-workflow` skill first.

The decision notes are the project's memory of what it keeps on purpose and what it already tried. Read the active notes that touch the scope:

- **Implemented notes,** especially of class `architecture`, are constraints. A candidate that goes against one says so and why, since removing it is a new decision that supersedes the note.
- **Rejected notes,** especially `rejected/simplification/`, are proposals already declined. A candidate that repeats one answers the reason it was rejected with new evidence. A rejection settles only what it rejected: the rejected half of a mixed proposal does not settle an independent candidate.
- **Implemented `simplification` notes** show what this project has counted as worth removing.
- **Proposed notes** are planned work. A candidate that overlaps one points to it.

Read also the rules and designs that govern the scope: the `AGENTS.md` files, the policies they link, such as for dependencies or tests, and the architecture and design documents that the README, the `AGENTS.md` files, or the notes point to. The parts of a design that describe the code as it is are constraints; the parts that describe plans are planned work, like proposed notes. Archived notes are history: read them for calibration, never as constraints.

Done when every active note and design document that touches the scope is listed with its role, or you have confirmed that none does.

## 2. Divide the survey

When your tools can start sub-agents, a whole repository or a large area goes to fresh ones, on the most capable model available, running in parallel: one per `area/*` label from the Labels line, or per top-level package or directory where the repository has no area labels. Give each surveyor this skill's path, its paths, the notes and documents from step 1 for those paths, and the constraints. Each one examines the substantial machinery of its paths as well as the obvious unused symbols, continues past the first promising deletion, and returns its candidates in the form of step 4, those classed Keep included, and its leads.

Each surveyor looks for candidates in its paths but searches for producers and consumers across the whole repository. A candidate that spans areas belongs to the area that declares it, such as the module that declares a type or a field; a surveyor that meets one in another area lists it as a lead. Findings outside the scope are leads too, listed without a full record.

A small area, up to a few thousand lines, is surveyed in the current context, and so is any scope when you cannot start sub-agents; say so in the report.

Done when every part of the scope has a surveyor.

## 3. Search

Let these questions guide the search:

- **Does each feature have a complete effect path?** Trace it from where its value is produced, through what passes it on, to an observable result. A field copied through every layer may have no writer, no reader, or only implementations that reject it. A configuration value may be overridden before anything reads it: follow the reads that decide and their precedence. A branch, fallback, or check may guard a case that the types, the callers, or an earlier check already rule out. Search the constructors and the code that emits each variant, as well as the callers.
- **Which distinctions change what a consumer does?** For each variant, flag, status, or mode, find the consumer that acts differently on it. Several internal states that every consumer treats alike need one public value. Keep the distinctions that authorization, durability, or ownership need.
- **Could a smaller, explicit behavior replace a subsystem?** A fixed interval in place of a calendar, an explicit parameter in place of a stored default, a reported failure in place of automatic rollback. Name the capability given up and the machinery removed. A production caller makes this a decision for the user, not a reason to drop the candidate.
- **Can the consumer read the original value when it needs it?** Copied state, caches, change events followed by a read, and a formula or a number written again where its source could be called may give way to reading the source at the time of use. First settle when the consumer must see the value: a value read when it was recorded and a value read when it is used can differ.
- **What is the whole cost, and who owns it?** Duplicate implementations, demo or support code that products depend on, packages that only resolve other packages, helpers with their own upgrade cycle. Compare the whole system removed with what replaces it, including the glue that remains. Moving a concept closer to its owner, or adding a check that keeps two copies equal, does not remove its cost.
- **Does a dependency or the platform already do it?** Hand-rolled code that the standard library, an installed dependency, or a well-maintained package covers. Count the code and its own tests that go, the cost of the dependency, and every behavior the glue must keep, such as limits, cancellation, fake clocks in tests, and packaging. A replacement that rebuilds the same behavior around the library is not a simplification. Follow the project's dependency policy, and prefer what is already installed.

Documents and tests are maintained too: a document that restates the code or another document, and a test that only covers behavior nothing can reach. A test, check, type, or note that exists only to keep something working is not evidence that the thing is needed; it is part of what would go.

A defect you notice along the way is not a candidate: it goes to the report as a claim in the form of step 1 of the `verify-bug` skill, with its location, trigger, symptom, and kind.

Done when every part of the scope has been searched with every question.

## 4. Prove each candidate

Search with the project's search tool, then read the matches. Search the exact name in every form a consumer could use: property reads and writes, string forms such as event names, configuration keys, wire strings, and names built from a template, and both method and function calls. Cover every place code is loaded from: every package and application, scripts, configuration and manifests, package exports, loaders that resolve a name at run time, generated files, and the other languages in the repository. Judge an example or a fixture by what actually runs it, not by the name of its directory. Tests and declarations show a contract, not a shipped producer or consumer. The history adds evidence: `git log -S <name>` shows when a name came in and whether anything has ever read it.

No caller in the repository is weaker evidence than no way to reach it. A package API, a plugin or extension point, a configuration key users set, or a stored or wire format may have consumers outside the repository; look for the document or note that makes it public before calling it dead.

Stored data needs its own care. Removing a write loses for good the data that saves or records made from now on would have carried, so a reader that a design plans is a reason to keep it. Ceasing to read an old format needs a clear error for data in that format, and the question of whether anyone still has such data goes to the user.

An unused-code checker or a duplication detector that the project already runs gives leads, not proof, since both miss code loaded by name and generated code.

Before merging two mechanisms into one, show that they express the same fact. A copy or a validation at a trust boundary, such as a parser, a configuration loader, a queue, a file, a process, or network input, keeps its place. In asynchronous code, map each promise, flag, cancellation path, and cleanup to its owner before collapsing any of them.

Record for each candidate:

- the location and the module that owns it;
- the effect path found: the producers and consumers, or their absence, with the searches that show it;
- what disappears: code, tests, documents, configuration, dependencies, stored fields;
- what remains, including glue;
- what a user, a caller, or stored data loses, if anything;
- the strongest reason to keep it.

Then classify it:

- **Unreachable:** nothing in a shipped path produces or consumes it, so removing it changes no behavior.
- **Duplicate:** a copy of a value, a formula, or an implementation that could read or call its source instead, so one of the copies goes and behavior stays the same.
- **Narrower behavior:** removing it gives up a capability. State the loss; the user decides.
- **Keep:** it serves an obligation the project keeps, the evidence is not enough, the change would only move the same complexity elsewhere, or it removes too little. Say which.

A candidate removes enough when the reader holds one concept fewer, or the project keeps one field, test, or dependency fewer. A smaller one is classed Keep for removing too little.

Done when every candidate has its record and its class.

## 5. Report and propose

When surveyors ran as sub-agents, check the facts each candidate rests on the way the `verify-bug` skill checks a fact about the code: rerun the searches, and read the code paths. Where you disagree, add your reasons beside the candidate instead of removing it.

Report:

- the parts of the scope surveyed, and any part not searched, so the survey is called complete only when it was;
- the candidates, the ones that remove the most first, each with its record, its class, and its destination;
- the Keep candidates that others would be likely to propose again, with their reasons, and the rest of them in one line at the end;
- the suspected defects, and the leads outside the scope;
- whether surveyors ran as sub-agents or in this context.

Each candidate gets one destination:

- **Change directly:** an unreachable or duplicate candidate whose change is small, such as one module and its tests.
- **Ask:** a small narrowing, as a question for the user, such as whether anyone still has data in an old format.
- **Propose:** a larger removal or duplicate, or a narrowing that is large or contested. Offer to record it as a proposed `simplification` note with the `decision-notes` skill, with the consumer evidence, what the project stops maintaining, the capability given up, and acceptance criteria that can be observed. When a note already owns the same decision, update that note instead. A proposal that needs more than one pull request goes on to the `note-to-tickets` skill.
- **Record why it stays:** a Keep candidate whose reason others would miss. Offer to record it as a rejected `simplification` note, so the next survey reads the reason instead of proposing it again.

Write notes only when the user agrees. When the user asks to implement a candidate, make each direct change in its own commit through the `commit` skill after the narrowest checks of the check table pass, and carry out a proposal by the "Implement a proposal" procedure of the `decision-notes` skill.

Write the report in the conversation's language and the notes in the language the `Decision notes` line names, both by the principles of the `plain-language` skill.

Done when every candidate has a destination, and every note the user approved is written and passes the `decision-notes` verifier.
