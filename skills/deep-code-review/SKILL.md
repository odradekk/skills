---
name: deep-code-review
description: A strict, user-started review of a change for restructurings that remove concepts while keeping behavior, run by fresh sub-agents and grounded in the decision notes.
disable-model-invocation: true
---

# Deep code review

This review is about structure, not correctness. It looks for restructurings that keep behavior and make branches, modes, flags, helpers, or layers unnecessary, and for changes that leave the code harder to hold in one's head. The project's own review skill (`<repo>-code-review`) checks a change against the project's rules and past failures; run both when both matter. Two other skills remove code instead of judging it: `simplify-change` removes from a change what it adds without need, before its review, and `find-simplifications` surveys code for what the project could stop maintaining, including capabilities worth giving up. This review judges the structure of what remains. Code as it stands, apart from a change, is surveyed by `improve-architecture` for structure worth changing and by `find-simplifications` for what can go.

It only reviews: it reports findings and changes no code.

## 1. Set the scope

- **By default:** the current branch's changes against its merge base with the base branch from the `## Agent workflow` section, plus uncommitted changes.
- **When the user names commits or a pull request:** those changes.

Done when you have the list of files in scope.

## 2. Ground the review

Read the active decision notes that touch the paths in scope:

- **Accepted notes** are constraints. A finding keeps them, or says plainly that it challenges one and why.
- **Rejected notes** are proposals already turned down. A finding that repeats one must say what has changed since the rejection.
- **Proposed notes** are planned work. A finding that overlaps one points to it.

Read the file size limit from `.agents/file-size.json`; without that file, use 5,000 tokens, counted as bytes / 4.

Done when you can list every active note that touches the scope, or have confirmed that none does.

## 3. Hand it to fresh reviewers

When your tools can start sub-agents, the review runs in fresh ones, on the most capable model available, and you coordinate. Give each reviewer only the scope, this skill's path, the notes from step 2, and the file size limit; the conversation and reasoning that produced the code stay out.

Split a large scope into three reviewers working in parallel, one per lens from step 4: structure; boundaries and types; size and flow. A small scope gets one reviewer for all three. Without sub-agents, review it yourself and say in the report that the review ran in the author's context.

## 4. What the reviewers look for

Start with the largest question: for each meaningful part of the change, would a different arrangement of the state model, the ownership boundary, or the existing abstractions make some of its branches, flags, helpers, or layers unnecessary? A rearrangement that leaves the reader holding as many concepts as before is not a simplification.

**Structure**

- **Scattered special cases:** a new condition inserted into an unrelated flow, or a one-off flag or nullable mode that every caller must now consider. Give the case its own path, model, or dispatcher.
- **Logic in the wrong place:** feature logic in a shared path, implementation details crossing an interface, or a new helper where the codebase already has one. Move it to the module that owns the concept, and reuse the existing helper.
- **Duplicated logic:** the same steps written twice. Extract them once.

**Boundaries and types**

- **Indirection that buys nothing:** wrappers that only forward calls, or generic mechanisms that hide a simple data structure. Delete the layer.
- **Unclear contracts:** casts, `any` or `unknown`, needless optional parameters, loosely shaped objects, or silent fallbacks over an invariant nobody stated. Make the boundary explicit with a type, or with validation where data enters.
- **Wide mutable state:** state kept in a wider scope than the code that reads and changes it, such as module or global state for data one function needs, or a field for what could be a local, and a value kept in step with another instead of derived from it. Narrow the scope, in the order of a function that returns its result, a local, a field, module state, and a global, or derive the value.

**Size and flow**

- **Size:** a file the change pushes past the file size limit, or a function that does several jobs. Split it by responsibility.
- **Flow:** independent steps run one after another for no reason, or related updates that can leave state half-applied. Let independent steps run independently, and make related updates atomic.

Every lens ends with the reader's test: for the values the change introduces or changes, can a reader new to the code say where each comes from and what can change it within half a minute? When the answer means tracing through several layers or holding hidden state in mind, the finding names the layers to cut or the state to narrow.

Every finding carries its evidence:

- the location, as file and lines;
- what is wrong, and what it will cost the next change;
- the proposed structure, as a short sketch of the code or the module layout;
- what disappears: branches, types, parameters, or files;
- what keeps behavior the same: the tests that already pin it, or the tests to write before restructuring.

A suggestion without a sketch and a behavior argument stays out of the report. State a major problem as a major problem; do not soften it into a suggestion.

## 5. Report

Order the findings by impact: structural regressions; missed restructurings that would remove a meaningful part of the change; scattered special cases; contract problems; size and decomposition; the rest. Prefer a few well-supported findings to many small ones, and leave out cosmetic notes when structural findings exist.

Mark where each finding belongs:

- **Fix in this change:** the problem and its fix stay inside the changed code.
- **Propose:** the restructuring reaches beyond the change. Offer to record it as a proposed `simplification` note with the `decision-notes` skill; write the note only when the user agrees.

End with a verdict. The change meets the bar when it has no structural regression, no visible missed restructuring that would remove a meaningful part of it, no file pushed past the size limit without a stated reason, no new scattered special cases, and no indirection or contract churn that hides the design.

When reviewers ran as sub-agents, pass their findings on as reported. Check the facts each finding rests on the way the `verify-bug` skill checks a design judgment, such as whether a line exists, the logic is really duplicated, or the cited tests pin the behavior; where you disagree with a judgment, add your reasons beside the finding instead of removing it. Write the report in the notes language from the Agent workflow section, by the principles of the `plain-language` skill.

Done when every finding has its location, evidence, and destination, and the verdict is stated.
