---
name: design-interface
description: Design an interface before its code, starting from what callers need, comparing structurally different designs when the interface is new and public, defining its data and operations, screening for flaws that mislead the next contributor, and writing the contract that the tests are derived from. Use when work adds or changes an interface, such as a new module, a public function or type, or a change that crosses modules, and when another skill needs an interface settled.
---

# Design interface

An interface is everything a caller must know to use a module correctly: the types and signatures, and also the invariants, the order of calls, the errors, the configuration it needs, and its performance. It decides how much every caller must learn and what the tests can check, so it is settled before the tests and the code. A module is **deep** when a small interface gives callers a lot of behavior, and **shallow** when the interface is nearly as complex as what it hides; prefer the deep design.

Two words keep their meaning throughout. A **seam** is where a module's interface lives: the place where a test or another implementation can take a dependency's place. The **system boundary** is where outside data enters: user input, files, the network, configuration, other processes.

A change that uses an existing interface as it is skips this skill: the existing interface, its documentation, and its tests are the contract.

The skill runs without stopping for anyone, so that it can be one step of a longer workflow. It decides what the intent leaves open by the rules in step 6, and records every choice in its report, where the caller and the review that follows can see it.

## 1. Ground the design

- Read the intent, such as the ticket, the decision note, or the request, and the decision notes and design documents that touch the area. Implemented notes and the parts of designs that describe the code as it is are constraints; a proposed note may already sketch the interface.
- Read the code the interface will connect to, and find the interfaces in the project that do similar work. Follow their conventions for naming, errors, passing dependencies, and where validation sits. Reuse a type the codebase already defines for the same information.
- Sort each dependency the module will have into one of these categories, which decide how tests take its place:
  - **In-process:** pure computation or in-memory state. Tests run it for real.
  - **Local stand-in:** a dependency with a local substitute, such as an in-memory database or filesystem. Tests run the substitute.
  - **Owned, across a process or the network:** a service the project owns. The module takes it through a port, an interface the project defines, with a production adapter and an in-memory adapter for tests.
  - **Third party:** a service the project does not control. The module takes it through a port, and tests use a fake adapter.

A port with only one adapter is a guess about the future, not a seam: add one only when production and tests both need an adapter.

Done when you can name the code the interface connects to, the constraints, the conventions to follow, and each dependency's category.

## 2. Write what callers need

List what each caller must be able to do, in the callers' terms: what it has, what it wants back, and what it does when something goes wrong. Then write a draft of two or three real call sites in the callers' own code. The draft makes the needs concrete; it does not fix the shape yet, since a call site already implies one.

Done when the needs cover the main ways the intent says the interface will be used.

## 3. Choose the shape

Outline the data each operation takes and returns, and the operations themselves, with the call sites this shape gives the callers. Prefer the shape in which data structures carry the decisions: trace each common access through the structure, and when the answer is "a map or a cache can be added later", the structure is wrong.

For a new public interface, or one that crosses modules, compare at least two structurally different shapes before choosing; the first idea is rarely the best. How much work that takes depends on the interface:

- **A new module, or an interface with state, dependencies, or several operations:** when your tools can start sub-agents, give the alternatives to fresh ones running in parallel, each with a different constraint: the smallest interface, with one to three entry points that each do as much as they can; the most common call made trivial; and, when a dependency crosses a process or the network, the design built around ports and adapters. Give each the intent, the grounding from step 1, and the needs from step 2, and tell it that existing signatures may change. Each returns its interface, its call sites, what it hides, how it handles dependencies, and its trade-offs. Without sub-agents, write the alternatives yourself, one after another, leaving each one unchanged once written.
- **A single function without dependencies:** write two or three alternatives yourself, a line or two each.

Two alternatives with the same structure, such as the same functions with different names, count as one.

Compare the shapes by:

- **depth:** how much a caller can do for each thing it must learn;
- **locality:** whether a likely future change lands in one module or across callers;
- **seams:** where tests and other implementations can take a dependency's place.

The deletion test helps: imagine the module deleted. When the complexity disappears with it, the module only passed calls through; when the complexity reappears in every caller, it earned its place. Choose one shape, or combine parts of several, and state why the others lost. The chosen shape's call sites are the specification from here on: when the types and the call sites disagree, change the types.

Done when one shape is chosen, with its call sites and the reasons the others lost.

## 4. Define the data and the operations

For each kind of data in the chosen shape, write a **data definition**:

- its shape, as a type, or as a comment in a language without types;
- its interpretation: what it means, with units, valid ranges, and the invariants every operation preserves;
- its kind: atomic, enumeration, interval, a union of variants, a record, a collection, or a recursive structure. The kind decides which test cases the `tdd` skill derives from it;
- data examples: named values, at least one for each variant. They go where the project keeps such values, such as test fixtures or documentation, not into production code. An example whose values come from content data, such as a table the project ships, refers to that data instead of copying its values.

Make invalid states impossible to build where the language allows. An invariant goes into a type first; into validation at the system boundary second; for content the project ships, such as a table in a content file, into a check of that content in the project's tests third; and into a comment last. Outside data is validated where it crosses the system boundary and parsed there into these types; inside, code trusts the types and does not check again. When validating at the boundary would change existing behavior beyond the intent, keep the existing behavior where the value is used, and report the missing boundary check as a follow-up. Business logic goes into functions that take data and return results, and the code that connects them to I/O, the framework, or the UI stays thin.

For each operation, write:

- the **signature:** which data definitions it consumes and produces;
- the **purpose statement:** what it computes from its inputs, in one or two lines, never how;
- the **effect statement,** when it changes state: what changes, in terms of the inputs and the state before the call;
- the errors it promises, and the order of calls it requires, if any.

These products are text until step 7: they go into the contract in step 6.

Done when every kind of data has its definition and every operation has its products.

## 5. Screen for flaws

Assume the next contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Prefer the design in which a change that looks right from one file is right for the whole repository. Check the design for each of these flaws, and revise it, or return to step 3 when the flaw is in the shape:

- **Shallow module:** callers must combine several calls for one task, options expose internal stages, or learning the interface does not spare the caller from learning the implementation.
- **Pass-through:** an operation forwards its arguments to another with the same shape and adds nothing.
- **Leaked detail:** a representation, policy, or protocol detail appears in more than one module, or a wire, storage, or framework type appears on the interface.
- **Split by execution order:** modules for load, validate, transform, and save that each repeat the same representation, instead of one module that owns it.
- **Split ownership:** two modules write the same state, or keep their own copies of it.
- **Two ways to do one task:** the next contributor copies whichever it finds first, and both keep gaining callers.
- **Reachable internals:** callers can import what the module keeps inside; make it unreachable from outside the module.
- **Hand-synced lists:** the same items are listed in several places. Derive the others from one, or make the build fail when they disagree.
- **Untestable through the interface:** a behavior the tests could check only by reaching inside. The seam is in the wrong place.

Done when every flaw on the list is absent or revised, or kept with a stated reason.

## 6. Write the contract

The contract is what the `tdd` skill turns into tests. List, for each operation:

- the data definitions it consumes, with each variant, and each interval with its ends;
- the results its purpose statement promises, each with a worked example whose expected value is computed by hand from the intent;
- each effect, each promised error, and the order of calls it requires;
- each state transition, and the transitions it refuses;
- the numbers the rule itself fixes, such as a cap or a formula the intent states, each with a worked example;
- the tunable data it reads, such as thresholds in a content or configuration file: the rule it applies to that data, and the invariants the data must keep, not the current values;
- what it excludes: the inputs that the types or the system boundary rule out.

When the intent leaves a choice open, such as the wording of a message or what happens at a limit it does not mention, decide it without asking. Prefer, in this order, the existing behavior, the smaller interface, and the way the project already does the same thing, and record the choice as an assumption.

When the design cannot go on, because the intent contradicts itself or an implemented decision, or because it lacks information that no default supplies, write no code. End with the report of step 8, saying what blocks the design, for the caller to resolve.

Done when the contract covers every operation, and every open choice is decided and recorded.

## 7. Write the design into the code

Write the data definitions as types, the purpose, effect, errors, and order into the documentation comment of each operation, and a stub for each operation: the real name and parameters, with a body that fails as not implemented and uses its parameters, such as in the error message, so the compiler's unused checks pass. Update the existing callers so the code compiles; until the `tdd` skill fills in the stubs, they fail at run time.

When the design settles a lasting structural decision that no existing note or document records, such as a module boundary, the owner of a piece of state, or a port with its adapters, and the decision meets the conditions the `decision-notes` skill sets for an implemented note, record it with that skill in the same change as an `architecture` note, with the shapes that lost as its alternatives. It goes to review with the code.

Done when the code compiles or loads with the stubs in place, and the note is written where one is due.

## 8. Report

Report the call sites, the data definitions and operations, the shapes that lost and why, the flaws kept and why, the contract, the assumptions, the follow-ups, such as a missing boundary check, and the note written, if any; or, when the design could not go on, what blocks it.

When another skill called this one, return the report to it. Otherwise write it in the conversation's language, by the principles of the `plain-language` skill.

Done when the report covers every product of steps 3 to 7.

## 9. Keep the design honest

The implementation fills in the stubs against the contract. A deviation, such as a parameter the design did not foresee, is a signal, not friction to absorb silently: decide whether the design was wrong, a requirement was missed, or the implementation is doing too much, and say which.

When the same kind of friction keeps appearing, return to step 3 with what the implementation showed, and design again, smaller, instead of patching. The signs are a pattern, not one case: the same workaround in unrelated places; special cases for unrelated edge cases; casts, or optional fields that are always set, needed to compile; a lock for state the design said was not shared; callers that must know the module's internal rules. A few edge cases do not condemn a design, and complexity in the data is not complexity in the design.
