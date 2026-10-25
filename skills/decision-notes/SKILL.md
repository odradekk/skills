---
name: decision-notes
description: Write proposals for a repository's decision notes, the agent-written RFCs that record what the user decided, why, and which alternatives lost, and move notes through their lifecycle on the user's word: accepting, rejecting, superseding, and archiving them, after which they are frozen. Use when planning substantial work, recording a decision whose rationale code and tests cannot carry, when the user accepts, rejects, or replaces a decision, when archiving notes, citing a note from code, or adopting existing ADRs.
---

# Decision notes

A decision note records what code, tests, and docs cannot: the problem, the choice the user made, the alternatives it beat, and what it costs. Code is the authority for what the system does; notes are the authority for what the user decided and why. One decision has one **owner** note. Every change to the repository traces to its source: an accepted note, a ticket that cites one, or the user's request, recorded in the commit or pull request.

**Planning writes notes; work carries them out.** Notes are written and revised only while they are proposals, during planning with the user: through this skill and `grill-decision`, and in the planning steps of `find-simplifications`, `improve-architecture`, `deep-code-review`, `setup-performance`, and `note-to-tickets`. The skills that carry out work, such as `implement`, `design-interface`, `tdd`, `refactor`, `simplify-change`, `diagnose-bug`, `commit`, and `pr`, never write, edit, move, or delete a note. They cite the note they carry out, and report a conflict with an accepted note, or a decision the notes have not made, for planning to take up.

## Locate the notes

Read the `Decision notes` line in the `## Agent workflow` section of the repository's `AGENTS.md`: it gives the notes directory and the language for note bodies. If the section is missing, run the `setup-agent-workflow` skill first. Create folders when the first note needs them.

## Layout

Each note lives at `<notes>/<lifecycle>/<class>/YYYY-MM-DD-slug.md`. The **lifecycle** folder is the note's status:

- `proposed/`: a decision being planned. It may be revised freely until the user accepts or rejects it.
- `accepted/`: a decision the user accepted. It is **frozen**, and work carries it out. How far the work has got lives in its tickets and pull requests, not in the note.
- `rejected/`: a proposal the user declined, **frozen** and kept as a **guardrail**: the reason it lost stops the idea from being proposed again unexamined.
- `archived/`: **frozen** history, accepted or rejected, that no longer guides new work. It still explains why existing code is the way it is.

The **class** folder is the kind of decision, from this closed set:

| Class | Covers |
|---|---|
| `feature` | A new user- or model-facing capability. |
| `bug-fix` | Corrects a defect or closes a gap that a failure exposed. |
| `simplification` | Removes code, behavior, or surface without adding capability. Refactors belong here; the test is whether observable behavior changes. |
| `architecture` | The structure of the shipped code: module relations, data flow, runtime vocabulary. |
| `process` | Tooling and workflow around the code: CI, release, dependencies, conventions. |
| `testing` | Test infrastructure and strategy. |

The date is the day the topic was first proposed. The slug is lowercase kebab-case. Dates instead of sequence numbers let parallel branches add notes without collisions. The folder tree is the index; keep no separate index file.

The filename without `.md` is the note's **ID**. It never changes, so tickets, commits, code, and other notes refer to a note by its ID: in a note, as `Decision note: <ID>`. A path link to another note would break when that note moves, and a frozen note cannot repair it. A note lists none of its tickets, pull requests, or commits: they point to the note (see the `note-to-tickets` skill). A note names concepts, modules, and behaviors rather than file paths, so that moving code never touches a note; code points to the note instead (see [Cite notes from code](#cite-notes-from-code)).

## Frozen notes

Notes in `accepted/`, `rejected/`, and `archived/` are frozen. Their files are read-only, and nobody edits, moves, renames, or deletes them by hand. Each of these folders holds a short `AGENTS.md`, with a `CLAUDE.md` that imports it, saying so to any agent that opens a file there.

Only `scripts/note_lifecycle.py` in this skill's directory changes them, and only on the user's word. It lifts the read-only flag for its own edit and restores it. Its edits are the whole list of what a frozen note ever gets: the status line when a proposal enters `accepted/` or `rejected/`, the `Supersedes` and `Superseded by` lines that link two notes, and the `Archived` line. Git does not record the read-only flag, so the frozen-notes hook that `setup-agent-workflow` installs runs `note_lifecycle.py protect` after every checkout, merge, and rebase; the verifier with `--base` rejects every other change.

```sh
python <this skill's directory>/scripts/note_lifecycle.py <notes-dir> accept <ID>
python <this skill's directory>/scripts/note_lifecycle.py <notes-dir> reject <ID> "<why, in one line>"
python <this skill's directory>/scripts/note_lifecycle.py <notes-dir> supersede <new ID> <old ID> [--part "<the part replaced>"]
python <this skill's directory>/scripts/note_lifecycle.py <notes-dir> archive <ID>
```

## When to write one

Write a proposal only for lasting rationale that code, tests, and existing docs do not carry:

- substantial work that should be decided before it is built;
- a decision already made but never recorded, when it is hard to reverse, surprising without context, and the result of a real trade-off. It is written as a proposal too, and the user accepts it.

When a proposal already owns the decision, revise that proposal. When an accepted note owns it, a change to the decision is a new proposal that supersedes the accepted note. Mechanical edits, local UI adjustments, and easily reversed choices need no note.

## Format

The first three lines are exactly:

```markdown
# <title>

Status: <status>
```

The status agrees with the lifecycle folder: `Status: proposed`, `Status: accepted`, or `Status: rejected — <why, in one line>`. An archived note keeps its status and has `Archived: YYYY-MM-DD` on line 4. Further header lines, before the blank line that opens the body, link superseding notes: `Supersedes: <ID>`, `Superseded by: <ID>`, or, for part of a decision, `Supersedes in part: <ID> — <the part>` and `Superseded in part by: <ID> — <the part>`. Only `note_lifecycle.py` writes header lines.

The body opens with `## Problem`, written so it stands without the solution. Free-form technical sections, such as a data format or a module diagram, may sit between the required ones:

| Lifecycle | Required sections |
|---|---|
| `proposed`, `accepted` | Problem, Proposal, Alternatives considered, Acceptance criteria, Risks |
| `rejected` | Problem, Proposal, Alternatives considered |

- **Proposal:** the change decided. It is written while the note is a proposal and stays exactly as the user accepted it.
- **Acceptance criteria:** the observable state that means done.
- **Risks:** what could go wrong, and what the change knowingly gives up.
- **Alternatives considered:** each genuine alternative and why it lost, one paragraph per alternative that starts with the alternative in bold. A decision recorded without the options it beat gets argued again. Record the alternatives that were really weighed.

A section may be one sentence; its length follows the decision. Headings stay in English whatever the body language, because the verifier matches them. Revise every proposal you write with the `plain-language` skill, including its new-reader check.

## Write or revise a proposal

1. **Settle the decision.** When neither the conversation nor the work itself shows which alternatives were weighed and why the chosen one won, settle the decision with the user through the `grill-decision` skill first; it returns here with material for every section.
2. **Check the notes it touches.** Search the proposed, accepted, and rejected notes for the same decision, mechanism, or rejected alternative, and say in the proposal how it relates to each match, by ID:
   - an accepted note it would replace, wholly or in part: the Proposal says which part. The link is made when the user accepts the new note;
   - another proposal on the same decision: merge them into one, or propose that the user rejects the other;
   - a rejected note it reopens: the Proposal answers the reason that note was rejected, with what has changed since.

   Done when every match is named in the proposal with its relation.
3. **Write** the note in `proposed/<class>/`, in the format above, and show it to the user.
4. **Verify** (see [Verify](#verify)).

## Accept, reject, and supersede

Each is the user's decision, carried out by `note_lifecycle.py` only after the user says so:

- **Accept** a proposal when the user accepts it. Work starts on accepted notes only, and tickets are published for them (see the `note-to-tickets` skill).
- **Reject** a proposal when the user declines it, with the reason in one line, and close its open tickets, if any, with the reason and the note ID.
- **Supersede** when the user accepts a note that replaces an accepted one: accept the new note, then run `supersede <new ID> <old ID>`. It writes the link into both notes, and archives the old note when the whole decision is replaced. With `--part "<the part>"`, the old note stays accepted for the rest, with the part named in both links.

When work runs into an accepted note, the note does not change. The work reports the conflict, and the user decides whether to plan again: a new proposal for the part in question, which supersedes that part of the old note once accepted, while the rest of the old note stays as it was.

## Archive

Archive keeps the set of accepted notes, the constraints every skill reads, small and current. Judge each note by its future value, never by length or age:

- **Keep accepted** a note while its rationale, alternatives, ownership boundary, negative guarantee, stored or wire format, security rule, or reintroduction condition is likely to guide a change.
- **Archive** an accepted note when its work is done and it is unlikely to guide future work, but its rationale is worth keeping as history; and one the user replaced as a whole, which `supersede` archives.
- **Archive** a rejected note when its idea no longer tempts anyone.
- **Never archive a proposal:** an obsolete one is rejected instead.

Nothing frozen is ever deleted. A proposal that nobody relied on may be deleted during planning; one that was discussed is rejected, so its reason stays.

Archiving changes what counts as current, so it is the user's decision. Present the candidates with your reasons, state the borderline ones as such, and run `archive <ID>` for each one the user agrees to. The first archive writes `archived/` to `<notes>/.rgignore`, so searches through the notes directory skip history; search the archive by naming its directory.

Calibration examples, from the DeepSeek Harness notes this workflow is adapted from; the word counts show that size is not the test:

- Archive: a collapsed sidebar control rail, 533 words. A closed, minor UI behavior.
- Keep: event-sourced sessions, 248 words. A foundational authority and durability boundary.
- Keep: a dropped image content block, 334 words. It states the condition for bringing the feature back.
- Keep rejected: merging two packages that were split, 426 words. The merge is still tempting.
- Archive rejected: streaming workflow progress through tool calls, 972 words. Its premise is obsolete.

## Cite notes from code

Someone who opens a file sees the code, not the notes. When a note explains why some code has a shape that would look wrong or arbitrary without it, such as who owns a piece of state, an alternative that was rejected, or a compatibility promise, the documentation comment of the module or export with that shape cites the note on a line of its own:

```
Decision note: <ID>
```

The comment still states the local facts, such as what the code guarantees; the note carries the reasons. The work that carries out an accepted note cites it where its decision shapes the code; a rejected note may be cited where its idea would be tempting. Code that a note merely mentions needs no citation. The marker stays in English whatever the notes language, because the verifier matches it.

A citation stays valid when its note is archived. Read it by the note's lifecycle:

- **accepted:** a constraint. A change to that code follows the note; a change that cannot is reported as a conflict for planning, and the note stays as it is.
- **archived:** history. It explains why the code is the way it is and constrains nothing. A `Superseded by` line leads to the note that holds the decision now.
- **rejected:** a guardrail against the idea it declined.

When work rewrites code under a newer decision, that code cites the newer note.

## Adopt existing records

When the repository has decision records in another format, such as numbered ADRs in `docs/adr/`, and the user chose to migrate them, convert each record into one proposal, then move it with `note_lifecycle.py` as the user confirms:

- Choose the class from the content. Take the date from the commit that added the record: `git log --follow --diff-filter=A --format=%as -- <file>`. Move the file with `git mv`, so its history follows.
- Apply the format. The record's decision becomes the Proposal, and its consequences the Risks. When the record does not state its alternatives and they cannot be reconstructed from the record or its history, put `<!-- decision-notes: alternatives-not-recorded -->` in place of the section. This marker exists only for adopted records.
- An accepted record is accepted; a superseded or deprecated one is accepted and then superseded by the record that replaced it, or archived; a proposed one stays a proposal.
- Repair the links to the old paths, and turn links between records into references by ID.

## Verify

Run the verifier from this skill's directory, using `python3` where `python` is missing or is Python 2:

```sh
python <this skill's directory>/scripts/verify_notes.py <notes-dir> --base <merge-base>
```

`<merge-base>` is `git merge-base HEAD origin/<base branch>`; omit `--base` when there is no remote base. The verifier checks the folder layout and filenames, the header and its agreement with the folder, the header lines and that every supersession link has its counterpart, and the required sections. In proposals, it also checks relative links and `Decision note: <ID>` references, and rejects a path link to another note. Inside a git repository, it checks every `Decision note: <ID>` citation in the files outside the notes directory that git tracks or does not ignore: the ID must name a note. With `--base`, it fails when a frozen note that existed at the base was changed, moved, or deleted since, other than by `note_lifecycle.py`. It exits 0 when clean.

Done when the verifier exits 0. Report the proposals you wrote or revised, and each lifecycle move the user asked for.
