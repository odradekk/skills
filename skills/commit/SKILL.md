---
name: commit
description: Commit the current changes as Conventional Commits grouped by intent, without asking for confirmation, and report what was committed. Use when the user asks to commit, or to split uncommitted work into separate commits, and when another skill needs a commit made.
---

# Commit

The user's request to commit is the approval: choose the scope, group it, write the messages, commit, and report. Questions are replaced by the rules below; work stops only in the cases under [Stop](#stop).

## 1. Read the state

```sh
git status --porcelain=v1 --branch
git diff --cached --stat
git diff --stat
git log -10 --format=%s
```

Choose the scope:

- **The user named files or a part of the work:** only that.
- **Something is staged:** only the staged changes, as one commit. The user chose what goes in the index, possibly part of a file; committing it as it stands keeps that choice. Everything unstaged stays as it is.
- **Nothing is staged:** the whole working tree, untracked files included.

Read the diff of every file in scope, and every untracked file in it whole.

Done when you know what changed in every file in scope.

## 2. Stop

- **A merge, rebase, cherry-pick, or revert is in progress, or there are conflicts:** stop and report.
- **HEAD is detached:** stop and report.
- **A file in scope looks like a secret or an accident:** `.env` files, private keys and certificates (`*.pem`, `*.key`, `id_rsa*`), credential or token files, build output, editor and OS files, or a large binary that was never tracked before. Leave it out of every commit and list it in the report; commit the rest.

## 3. Group

With the whole working tree in scope, make one commit per change that someone could review or revert on its own. Keep code with its tests, types, and docs. Order the commits so each builds on the ones before it, such as a refactor before the feature that needs it. A file with parts that belong to two groups goes into the group it mostly belongs to; the other group's message mentions it.

Give each group a Conventional Commits type: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `style`, `build`, `ci`, or `chore`.

## 4. Write each message

- **Subject:** `<type>(<scope>): <summary>`, in the format and language of the repository's recent subjects, such as `feat(story): 接入阿莎姬的羁绊剧情`. Without a history to follow, use the notes language from the `## Agent workflow` section, or English. Imperative, at most 72 characters, no final period.
- **Body:** only when the subject cannot carry why the change was made or what a reader must know; wrap it at about 72 characters. Write it by the principles of the `plain-language` skill.
- **Ticket references:** only for work committed straight to the base branch, which has no pull request to carry them: `Refs #N`, or `Fixes #N` in the commit that completes the ticket, as the Tracker line says. On any other branch, the pull request carries them.
- **No AI attribution:** no co-author trailer for an AI tool, no "Generated with" line, no session link. A commit-msg hook may remove them too; write the message without them.

## 5. Commit each group

For each group, in order:

1. Make the index hold exactly this group: `git add -A -- <paths>`, which also records deletions and renames, then confirm with `git diff --cached --name-only`. A staged scope is already in the index.
2. Write the message to a temporary file outside the repository and run `git commit -F <file>`.
3. When a hook changes files, such as a formatter, stage the changes to this group's files and commit again. When a hook rejects the commit because of this change, fix the cause and commit again; when the rejection has another cause, stop and report the hook's output. Let every hook run.

Done when every file in scope is committed, or listed as left out with the reason.

## 6. Report

List each commit with its short hash and subject, the files left out and why, and the changes that remain uncommitted. Committing does not push; pushing belongs to the `pr` skill or to the user's request.
