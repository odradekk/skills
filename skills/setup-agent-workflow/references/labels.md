# Issue labels

Labels classify issues and pull requests so related work is easy to find: what kind of work it is, and which parts of the system it touches. Everything else has a better home. The tracker's open and closed states and its project boards carry status; a ticket's first line carries its decision note ID; priority, assignment, and due dates use the tracker's own fields when a project needs them.

## The scheme

- **Kind:** exactly one per issue and pull request. The defaults are the six decision note classes, with the same names and meanings, so a note and the tickets split from it share one vocabulary: `kind/feature`, `kind/bug-fix`, `kind/simplification`, `kind/architecture`, `kind/process`, `kind/testing`. Add a kind only for work none of them covers, such as `kind/docs` for documentation-only work.
- **Area:** every one that applies. An area is a part of the system that someone would search by, usually a top-level source folder or package group, plus areas such as docs and tooling. Each area lists the paths it covers. Merge folders that always change together; split a folder only when its parts are worked on separately.

Names are lowercase kebab-case after the prefix. All kinds share one color and all areas share another, so the two families are easy to tell apart.

## Detect, for step 2

List the labels the tracker has now, with how many issues use each, through the tracker's tool. For example, with `gh`:

```sh
gh label list --limit 200 --json name,description
gh issue list --label "<name>" --state all --limit 1000 --json number --jq length
```

Draft the areas from the repository's top-level structure. For each existing label, plan one outcome:

- **Rename** it to a label of the scheme when it means the same thing, such as `bug` to `kind/bug-fix`. A rename keeps its issues.
- **Merge** it into a label of the scheme when two labels mean one thing: add the scheme label to its issues, then delete it.
- **Keep** it outside the scheme when it serves another purpose, such as `good first issue`.

## Propose, for step 5

Show the kinds with their meanings, the areas with their paths, and the plan for every existing label with the number of issues it touches.

## Apply, for step 6

This changes the tracker, so apply only the plan the user approved: create each new label with its description, rename in place where the tracker allows it so the label keeps its issues, and for a merge add the new label to every issue of the old one before deleting the old one. For example, with `gh`:

```sh
gh label create "kind/feature" --color "<hex>" --description "<meaning>"
gh label edit "bug" --name "kind/bug-fix" --description "<meaning>"
gh issue edit <N> --add-label "kind/bug-fix"
gh label delete "<old>" --yes
```

Record the scheme in the section's `Labels` line. Done when listing the tracker's labels again shows every label the line lists with its description, and every approved rename and merge is complete.

## Refresh

Compare three things: the `Labels` line, the tracker's labels, and the repository's structure.

- A new top-level part of the code: propose a new area.
- An area whose paths no longer exist: propose moving its open issues to the area that replaced it. Keep the label while closed issues use it, unless the user approves deleting it.
- Labels created on the tracker outside the scheme: propose rename, merge, or keep, as in detection.
- An area that nearly every issue gets, or that no issue gets: propose splitting or merging it.

Every change to labels on existing issues needs the user's approval.
