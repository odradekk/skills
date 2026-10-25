---
name: pr
description: Push the current branch and open its pull request, or merge request, on the platform that hosts the repository, or update an existing one, with a description written for reviewers, without asking for confirmation. Use when the user asks to open, create, or update a pull or merge request, and when another skill needs one opened.
---

# Pull request

The user's request is the approval: check, push, write the description, create or update the pull request, and report its link. Questions are replaced by the rules below; work stops only in the cases this skill names.

## 1. Read the state

Read the repository's `## Agent workflow` section for the base branch, Tracker, Labels, Decision notes, and Prose lines; if it is missing, run the `setup-agent-workflow` skill first. Then:

```sh
git status --porcelain=v1 --branch
git rev-list --count origin/<base>..HEAD
```

Pull requests live on the platform that hosts `origin`; reach it through its command-line tool or MCP tools. Look for an open pull request for this branch, for example `gh pr view --json number,url,state,title,body`. When the tool is not signed in, stop and tell the user how to sign in.

- **HEAD is detached, or the current branch is the base branch:** stop and report; a pull request needs its own branch.
- **No commits ahead of the base:** stop and report.
- **Uncommitted changes:** when they belong to the work this pull request carries, commit them with the `commit` skill first. When they do not, or you cannot tell, stop and report them.

Done when you know the branch, its commits, the platform, and whether a pull request already exists.

## 2. Check and push

1. **Checks:** run steps 1 to 4 of the `pre-push-checks` skill. Fix a failure the branch caused, commit the fix with the `commit` skill, and rerun the check. Record a failure that already exists on the base for the Testing section.
2. **Push:** `git push -u origin <branch>` when the branch has no upstream, `git push` otherwise.
   - When the pre-push hook rejects commits that credit an AI tool, run the rebase command it prints, which rewrites only unpushed commits, and push again.
   - When the push is rejected as not a fast-forward, stop and report. Force-push only when the user asked to rewrite this branch's history, and then with `git push --force-with-lease`.

Done when the branch is pushed and its checks have run.

## 3. Write the title and description

The title is the subject of the only commit, or else a summary in the same style.

The description is for reviewers, written in the notes language from the Agent workflow section, headings included:

- **Why:** the problem in one or two sentences. The tracker's closing reference from the Tracker line, such as `Fixes #N`, for each ticket the pull request completes; the plain ticket reference for related ones; and the decision note ID when it implements a note.
- **What changed:** the changes to behavior, interfaces, configuration, and stored data that a reviewer must know, grouped by area. The pull request already lists the commits; describe the change, not the commit list.
- **Testing:** the commands that step 2 ran, with their results, and what no check covers. A performance number is reported the way the `measure-performance` skill reports one: the primary number here, the rest linked.
- **Notes for reviewers**, only when there is something to say: risks, where to start reading, follow-up work.

Revise the description with the `plain-language` skill. It carries no AI attribution: no "Generated with" line, no session link, and no co-author line for an AI tool.

## 4. Create or update

When the platform has the labels from the Labels line, add one `kind/*` and every `area/*` that the changed paths and the completed tickets call for. Mark the pull request as a draft, or add reviewers and assignees, only when the user asked for it. Write the description to a temporary file outside the repository.

To create, for example with `gh`:

```sh
gh pr create --base <base> --title "<title>" --body-file <file> --label "<kind>" --label "<area>"
```

To update an existing pull request after new commits or a review round, rewrite only the sections the new work changed, and keep the text and media that people added. Then update its title, description, and labels, for example with `gh pr edit <N> --title "<title>" --body-file <file> --add-label "<label>" --remove-label "<label>"`.

Done when reading the pull request back from the platform shows the current title, description, and labels.

## 5. Report

Give the link, whether the pull request was created or updated, the commits pushed, the checks run and their results, the labels, and anything left out, such as uncommitted changes or a failure that already exists on the base.
