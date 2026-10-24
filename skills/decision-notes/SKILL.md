---
name: decision-notes
description: Write, update, and retire a repository's decision notes, the agent-written RFCs that record why a change was made and which alternatives lost. Use when proposing substantial work, recording a decision whose rationale code and tests cannot carry, implementing or rejecting a proposal, changing code that an implemented note describes, archiving or pruning notes, or adopting existing ADRs.
---

# Decision notes

A decision note records what code, tests, and docs cannot: the problem, the choice, the alternatives it beat, and what it costs. Code is the authority for *what* the system does; notes are the repository's memory of *why*. One decision has one **owner** note.

## Locate the notes

Read the `Decision notes` line in the `## Agent workflow` section of the repository's `AGENTS.md`: it gives the notes directory and the language for note bodies. If the section is missing, run the `setup-agent-workflow` skill first. Create folders when the first note needs them.

## Layout

Each note lives at `<notes>/<lifecycle>/<class>/YYYY-MM-DD-slug.md`.

The **lifecycle** folder is the note's status; a note moves between folders as its status changes:

- `proposed/`: reviewed before it is built; not built yet, or only partly.
- `implemented/`: the decision shipped, and the note is kept current with the code.
- `rejected/`: considered and declined; kept only as a **guardrail**.
- `archived/`: **frozen** history of implemented decisions.

The **class** folder is the kind of decision, from this closed set:

| Class | Covers |
|---|---|
| `feature` | A new user- or model-facing capability. |
| `bug-fix` | Corrects a defect or closes a gap that a failure exposed. |
| `simplification` | Removes code, behavior, or surface without adding capability. Refactors belong here; the test is whether observable behavior changes. |
| `architecture` | The structure of the shipped code: module relations, data flow, runtime vocabulary. |
| `process` | Tooling and workflow around the code: CI, release, dependencies, conventions. |
| `testing` | Test infrastructure and strategy. |

The date is the day the topic was first proposed; for an existing topic, take it from git history. The slug is lowercase kebab-case. Dates instead of sequence numbers let parallel branches add notes without collisions. Notes link to each other with relative Markdown links, which the verifier checks. The folder tree is the index; keep no separate index file.

The filename without `.md` is the note's **ID**. It stays the same when the note moves between folders, so tickets and commits refer to the note by ID. A note lists none of its tickets, pull requests, or commits: they point to the note instead (see the `note-to-tickets` skill).

## When to write one

Write or update a note in the same change only for lasting rationale that code, tests, and existing docs do not carry:

- Substantial work that should be reviewed before it is built starts in `proposed/`.
- A decision already made starts in `implemented/` when it is hard to reverse, surprising without context, and the result of a real trade-off.

When a note already owns the decision, update that note. Mechanical edits, local UI adjustments, and easily reversed choices need no note.

## Format

The first three lines are exactly:

```markdown
# <title>

Status: <status>
```

The status agrees with the lifecycle folder: `Status: proposed`, `Status: implemented`, or `Status: rejected — <why, in one line>`. An archived note keeps `Status: implemented` and has `Archived: YYYY-MM-DD` on line 4.

The body opens with `## Problem`, written so it stands without the solution. Each lifecycle has required sections; free-form technical sections, such as a data format or a module diagram, may sit between them.

| Lifecycle | Required sections | Not allowed |
|---|---|---|
| `proposed` | Problem, Proposal, Alternatives considered, Acceptance criteria, Risks | |
| `implemented` | Problem, Decision, Alternatives considered, Consequences | Proposal, Plan, Migration plan, Acceptance criteria |
| `rejected` | Problem, Proposal, Alternatives considered | |

- **Proposal:** the intended change. Future tense, plans, and open questions belong here.
- **Acceptance criteria:** the observable state that means done.
- **Risks:** what could go wrong, and what the change knowingly gives up.
- **Decision:** what shipped, in the present tense.
- **Consequences:** what the trade-off cost and what it bought.
- **Alternatives considered:** each genuine alternative and why it lost, one paragraph per alternative that starts with the alternative in bold. A decision recorded without the options it beat gets argued again. Record the alternatives that were really weighed.

A section may be one sentence; its length follows the decision. Headings stay in English whatever the body language, because the verifier matches them. Revise every note you write or rewrite with the `plain-language` skill, including its new-reader check.

## Write a new note

1. **Settle the decision.** When neither the conversation nor the work itself shows which alternatives were weighed and why the chosen one won, settle the decision with the user through the `grill-decision` skill first; it returns here with material for every section.
2. **Check supersession.** Search the active notes (everything outside `archived/`) for notes that cover the same decision, mechanism, or rejected alternative. Give every match an outcome in this same change:
   - A fully superseded implemented note: archive it, or fold it into the new note (see [Retire notes](#retire-notes)).
   - A partially superseded note: keep it, cross-link both notes, and update the facts the new decision changes.
   - An obsolete proposal: reject it.
   - A rejected note that no longer guards against a plausible mistake: delete it.

   Done when every match has an outcome.
3. **Write** the note in its lifecycle and class folder, in the format above.
4. **Verify** (see [Verify](#verify)).

## Implement a proposal

When the work needs more than one pull request, split the proposal into tickets with the `note-to-tickets` skill.

In the change that ships the work (with tickets, the change that closes the last open one), move the note from `proposed/` to `implemented/`, keeping its class and filename. Set `Status: implemented`. Rewrite `## Proposal` as a present-tense `## Decision` about what shipped. Fold `## Acceptance criteria` and `## Risks` into `## Consequences`, or into a present-tense `## Testing` section that names what pins the behavior. Replace plans with what was built. Work that is only partly built stays in `proposed/`. When the proposal has tickets, its open tickets show what remains and the Proposal keeps the whole plan; without tickets, update the Proposal to what remains.

## Keep implemented notes current

When a change moves, renames, or alters something an implemented note names, such as a path, symbol, default, or mechanism, update the note in the same change. Find those notes by searching the notes directory for the names you changed. Rewrite stale facts in place so the note reads as current state, without a change history. Update facts only: reversing the decision itself takes a new note that supersedes the old one.

## Reject a proposal

Move the note to `rejected/<class>/` and set `Status: rejected — <reason>`. The body stays as it was proposed. Close the proposal's open tickets, if any, with the reason and the note ID.

## Retire notes

Judge each note by its future value, never by length or age:

- **Delete** an implemented note that only records a small UI adjustment or a mechanical change. A small change can still carry a lasting naming, compatibility, or ownership rule; such a note stays.
- **Keep active** an implemented note when its rationale, alternatives, ownership boundary, persisted or wire format, security rule, or reintroduction condition is likely to guide a future change.
- **Archive** an implemented note when the decision is complete and unlikely to guide future work, but its rationale is worth keeping as history.
- **Proposed** notes are never archived: reject an obsolete proposal instead.
- **Keep a rejected note** only while its losing idea is still tempting and the note explains why it loses; otherwise delete it.

**Fold** a fully superseded note into its new owner only after the owner carries every unique rationale, alternative, consequence, and verification from the old note; then delete the old note. After deleting any note, repair or remove every link to it (search for its filename).

Calibration examples, from the DeepSeek Harness notes this workflow is adapted from. The word counts show that size is not the test:

- Delete: a collapsed sidebar control rail, 533 words. A closed, minor UI behavior.
- Keep: event-sourced sessions, 248 words. A foundational authority and durability boundary.
- Keep: a dropped image content block, 334 words. It states the condition for bringing the feature back.
- Keep rejected: merging two packages that were split, 426 words. The merge is still tempting.
- Delete rejected: streaming workflow progress through tool calls, 972 words. Its premise is obsolete.

When a case is borderline, state the outcome you chose and why in your report.

## Archive a note

1. Move the file from `implemented/<class>/` to `archived/<class>/` with `git mv`.
2. Insert `Archived: YYYY-MM-DD`, using today's date, directly below the status line. The move and this line are the only edits.
3. Repair links from active files: point them at the current authority, keep them pointing at the archived path only when they cite history on purpose, or delete them.
4. On the first archive in a repository, add `<notes>/archived/` to the root `.rgignore`, so default searches skip frozen history. Search the archive by naming its directory explicitly.

Once archived, a note is frozen: its content, links, and formatting stay exactly as archived, and it is history, never current authority. The verifier's `--base` check fails on any change to an archived note.

## Adopt existing records

When the repository has decision records in another format, such as numbered ADRs in `docs/adr/`, and the user chose to migrate them, convert each record to one note:

- Choose the lifecycle from the record's status: accepted becomes `implemented/`; proposed stays `proposed/`; deprecated or superseded records go through [Retire notes](#retire-notes).
- Choose the class from the content.
- Take the date from the commit that added the record: `git log --follow --diff-filter=A --format=%as -- <file>`. Move it with `git mv` so history follows.
- Apply the format. When the record does not state its alternatives and they cannot be reconstructed from the record or its history, put `<!-- decision-notes: alternatives-not-recorded -->` in place of the section. This marker exists only for adopted records.
- Repair links to the old paths.

## Verify

Run the verifier from this skill's directory, using `python3` where `python` is missing or is Python 2:

```sh
python <this skill's directory>/scripts/verify_notes.py <notes-dir> --base <merge-base>
```

`<merge-base>` is `git merge-base HEAD origin/<base branch>`; omit `--base` when there is no remote base. The verifier checks the folder layout and filenames, the header and its agreement with the folder, the required and disallowed sections, and the relative links in active notes. With `--base`, it also fails when an archived note that exists at the base was changed or removed. It exits 0 when clean.

Done when the verifier exits 0 and every supersession match has an outcome. Report the notes you added, updated, moved, archived, and deleted.
