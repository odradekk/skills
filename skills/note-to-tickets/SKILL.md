---
name: note-to-tickets
description: Split a proposed decision note into tickets on the repository's issue tracker, one pull request each, every ticket pointing back to the note; also trace a note or ticket to its issues, pull requests, and commits. Use when a proposal is ready to be built and its work needs dividing, or when the user asks which tickets, pull requests, or commits belong to a note or a ticket.
---

# Note to tickets

A ticket says what to build, what counts as done, and what is out of scope. The note keeps the reasons, and the implementer decides how, starting from the code. A ticket is complete when its implementer meets no decision that the user has to make.

Each link is written once, where it is created; the reverse direction comes from a query (see [Trace](#trace)):

| Link | Written in | Reverse lookup |
|---|---|---|
| Ticket → note | The ticket's first line: `Decision note: <note ID>` | Search tickets for the note ID |
| Pull request → ticket | `Fixes #N` in the description of the pull request that completes the ticket; work committed straight to the base branch carries `Refs #N` or `Fixes #N` in its commit messages instead | The tracker lists them on the ticket |
| Pull request → note | The pull request that implements the proposal moves or edits the note | `git log --follow` on the note |

The note ID is the note's filename without `.md`. It stays the same when the note moves between lifecycle folders, so links by ID never break. The note itself lists none of its tickets.

## 1. Read the settings and the note

Read the `Decision notes`, `Tracker`, and `Labels` lines of the repository's `## Agent workflow` section; if the section is missing, run the `setup-agent-workflow` skill first. When the tracker is `none`, tell the user that this repository has no tracker to publish to, and stop.

Only a note in `proposed/` gets tickets: implemented work is done, and rejected work is not built. Read the whole note and the code its Proposal touches. Then look for tickets that already reference the note:

```sh
gh issue list --search '"<note ID>" in:body' --state all --json number,title,state
glab issue list --all --in description --search "<note ID>"
```

When tickets exist, this run extends or revises them instead of creating duplicates.

Done when you know the proposal, the code it touches, and every existing ticket for the note.

## 2. Check that the note is settled

List the hard-to-reverse choices the work requires. Each must be settled in the note, in its Proposal or one of its free-form sections. Settle every open question that a ticket would depend on through the `grill-decision` skill, and update the note, before drafting that ticket.

Done when every choice the tickets depend on is written in the note.

## 3. Draft the tickets

Cut the work into tickets that follow these rules:

- **One ticket is one pull request and one working session.** Merged alone, it leaves CI green.
- **A ticket delivers a behavior that a test can check.** Work with no observable result of its own, such as a type or a helper, joins the ticket that uses it. A prefactor ticket is the exception: it changes structure without changing behavior, existing tests verify it, and it comes first.
- **A wide mechanical change goes expand, migrate, contract.** When one change, such as a rename, breaks call sites across the codebase, the first ticket adds the new form beside the old; migration tickets move the call sites in batches, each blocked by the first; a last ticket, blocked by every batch, deletes the old form.
- **A risk that must be proven first gets the first ticket.** When the note's Risks name something the rest of the work depends on, such as a performance limit, a spike ticket proves it. Its acceptance criterion is the measured result, recorded in the note.
- **Blocking edges.** A ticket is blocked by every ticket whose result it needs, and by any ticket that edits the same files, so that parallel implementers never edit the same files at once.

Map every acceptance criterion of the note to the tickets that satisfy it. When the tickets fall into groups with no blocking edges between them, the note probably holds several independent decisions: tell the user, and suggest splitting the note before publishing.

Done when every criterion of the note maps to at least one ticket and every ticket follows the rules above.

## 4. Write each ticket

The title names the behavior, in the imperative: "Stream session history to reconnecting clients". The body uses this format, in the notes language from the Agent workflow section:

```markdown
Decision note: <note ID>

## Goal
<One to three sentences: the behavior that exists when this ticket is done, from the user's or the caller's side.>

## Acceptance criteria
- [ ] <A result someone can check, preferably with a test.>

## Not in this ticket
- <Adjacent work, and the ticket that owns it.>

## Blocked by
- <#N for each ticket that gates this one, or None.>

## Starting points
- <A module or symbol name, and why the work starts there.>
```

- `Decision note:` is the exact first line; the trace queries match it.
- **Not in this ticket** names the neighboring work an implementer would otherwise be tempted to do, with the ticket that owns it. Leave the section out only when nothing adjacent exists.
- **Starting points** is optional. Name modules and symbols only: line numbers and code go stale.
- Constraints that the note already fixes, such as a data format or an interface, are cited by note ID and section name ("see the Wire format section of `<note ID>`"), not copied.
- Code appears only when a prototype settled something that prose states less precisely, such as a state machine or a schema; quote only the part that carries the decision.

The note's reasons, implementation steps, estimates, priorities, due dates, assignees, and parent issues stay out of the ticket. When a ticket needs a human, for credentials, a design approval, or a deployment, that step is one of its acceptance criteria.

Label each ticket from the `Labels` line: one `kind/*` label, by default the note's class, so a prefactor ticket in a feature proposal is `kind/simplification`; and every `area/*` label whose paths the ticket's work touches, judged from its starting points and the code it will change. Use only the listed labels; when none fits, tell the user that the section needs a refresh through `setup-agent-workflow` before publishing.

Revise every title and body with the `plain-language` skill. The implementer starts without your context, so run its new-reader check over the full set of drafts.

## 5. Confirm with the user

Publishing creates issues that other people can see, so show the plan first: the numbered drafts with title, goal, blocking edges, out-of-scope work, and labels; and the map from the note's acceptance criteria to tickets. Ask whether the granularity and the blocking edges are right, and whether any ticket should be split or merged. Revise until the user approves.

Done when the user has approved the drafts.

## 6. Publish

Create the tickets in dependency order, blockers first. Write each body to a temporary file outside the repository:

```sh
gh issue create --title "<title>" --body-file <file> --label "<kind>" --label "<area>"
glab issue create --title "<title>" --description-file <file> --label "<kind>,<area>"
```

After every ticket exists, replace the draft numbers in the bodies with the real issue numbers (`gh issue edit <N> --body-file <file>`, `glab issue update <N> --description-file <file>`). The note stays unchanged.

Done when every approved ticket exists with its labels, its references use real issue numbers, and the step 1 search for the note ID returns all of them.

## Trace

From a note ID: find the note with `git ls-files '*<note ID>.md'`, then:

```sh
git log --follow --format='%h %as %s' -- <note path>   # commits that wrote, moved, or implemented the note
gh issue list --search '"<note ID>" in:body' --state all --json number,title,state
```

From a ticket: read its first line for the note ID (`gh issue view <N> --json body`, `glab issue view <N> --output json`), and find what references it:

```sh
gh issue view <N> --json state,closedByPullRequestsReferences   # pull requests that close it
gh pr view <PR> --json commits --jq '.commits[] | "\(.oid[:9]) \(.messageHeadline)"'   # the commits of each one
glab api projects/:id/issues/<N>/closed_by                       # merge requests that close it, on GitLab
glab api projects/:id/merge_requests/<MR>/commits                # the commits of each one
git log --all -E --grep='#<N>([^0-9]|$)' --format='%h %as %s'   # commits made straight to the base branch
```

Report the note's lifecycle folder, each ticket with its state, and the pull requests and commits under each ticket.
