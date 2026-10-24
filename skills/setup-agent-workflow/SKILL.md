---
name: setup-agent-workflow
description: Create or refresh a repository's Agent workflow section in AGENTS.md, the per-repository settings that the other workflow skills read, including the issue label scheme, and install git hooks that remove AI attribution from commit messages and keep files small enough for agents to read whole. Use when the user asks to set up or update the agent workflow, the issue labels, AI attribution stripping, or a file size limit for a repository, or when another skill finds the section missing or out of date.
---

# Set up the agent workflow

The workflow skills carry method; the `## Agent workflow` section carries one repository's facts. It caches what an agent cannot look up in one step: which branch is the base, where decision notes live and in which language, which tracker holds tickets, which labels classify issues, the house style for prose, what hooks and CI already run, and which command is the narrowest check for each kind of change. Lookups that take one file or one command, such as the script list in `package.json`, stay in the environment.

Everything the workflow installs lives under `.agents/`, which one set of files shares across agents; Claude Code reaches the project skills through a `.claude/skills` link. [references/layout.md](references/layout.md) shows the layout.

## The section

Other skills read these field names; keep them exactly. Values below are an example.

```markdown
## Agent workflow

Maintained with the `setup-agent-workflow` skill. Edit values freely; keep the field names.

- Base branch: `main`
- Decision notes: `.agents/notes/`, written in English. Every decision record, ADRs included, is a decision note written with the `decision-notes` skill. Files under `.agents/notes/archived/` are frozen history: read them as history and leave them unchanged.
- Tracker: GitHub issues on `origin`, through `gh`. Tickets for decision notes follow the `note-to-tickets` skill. The pull request that completes a ticket says `Fixes #N` in its description, and its commits carry no ticket reference. Work committed straight to the base branch, without a pull request, says `Refs #N` in its commits and `Fixes #N` in the one that completes the ticket. The change that closes a note's last open ticket also moves the note to `implemented/`.
- Labels: every issue and pull request gets exactly one `kind/*` label and every `area/*` label that applies. Use only the labels listed here; when none fits, refresh this section with the `setup-agent-workflow` skill.
  - `kind/feature`: a new user- or model-facing capability. `kind/bug-fix`: corrects a defect. `kind/simplification`: removes code, behavior, or surface without adding capability. `kind/architecture`: the structure of the shipped code. `kind/process`: tooling and workflow around the code. `kind/testing`: test infrastructure and strategy.
  - `area/api`: `src/api/**`. `area/ui`: `src/ui/**`, `src/styles/**`. `area/docs`: `docs/**`, `README.md`.
- Prose: documents, decision notes, tickets, pull request descriptions, and commit bodies are revised with the `plain-language` skill. House style: sentence-case headings; straight quotes in English text.
- File size: files stay under 5,000 tokens (bytes / 4) so an agent can read them whole. `.agents/file-size.json` lists excluded paths, exceptions with their reasons, and the baseline of older files over the limit, which may shrink but not grow. The pre-commit hook and CI run `.agents/scripts/check_file_size.py`.
- Hooks: pre-commit runs `lint-staged` (ESLint and Prettier on staged files) and `.agents/scripts/check_file_size.py`; commit-msg removes AI attribution lines and pre-push rejects commits that still credit an AI tool, both through `.agents/scripts/strip_attribution.py`. The `prepare` script in `package.json` connects `.agents/hooks/` on `npm install`.
- CI: GitHub Actions `ci.yml` runs lint, typecheck, the file size check, and the full test suite on Linux and Windows for every pull request.

| Change | Narrowest check |
|---|---|
| Behavior in `src/**/*.ts` | `pnpm vitest run <test files>` |
| Types in `src/**/*.ts` | `pnpm tsc --noEmit` |
| `**/*.md` | `pnpm markdownlint <files>` |
| `package.json`, lockfile, `tsconfig*.json`, build config | `pnpm build` |
```

Table rules:

- One row per distinct check. A `<placeholder>` names what the agent fills in for a given change.
- Every command exists in this repository, and every focused command has been run (step 4).
- The full suite gets no row: the CI line says what runs exhaustively.

## Steps

### 1. Find the file

Work at the repository root (`git rev-parse --show-toplevel`). The section lives in the root `AGENTS.md`, which most agents read. Claude Code reads `CLAUDE.md` instead, so `CLAUDE.md` must load `AGENTS.md`, either as a symlink to it or through an `@AGENTS.md` line. Plan to create `AGENTS.md` if it is missing, to create `CLAUDE.md` containing `@AGENTS.md` if that is missing, and to add the `@AGENTS.md` line to an existing `CLAUDE.md` that does not load `AGENTS.md` yet.

If the section already exists, this run is a refresh: every later step compares against the current values.

Done when you know which files you will create or edit, and whether this is a first setup or a refresh.

### 2. Detect the facts

Read each value from a file or a command:

- **Base branch:** `git symbolic-ref --short refs/remotes/origin/HEAD`, without the `origin/` prefix. If that ref is unset, use the `HEAD branch` line of `git remote show origin`. Without a remote, it is a question for the user.
- **Toolchain:** the manifests at the root and in each workspace package (`package.json` scripts, `Makefile`, `justfile`, `Taskfile.yml`, `pyproject.toml`, `tox.ini`, `noxfile.py`, `Cargo.toml`, `go.mod`, `*.sln` or `*.csproj`, `build.gradle`, `pom.xml`, `CMakeLists.txt`) and the test directory layout.
- **Hooks:** `git config core.hooksPath`, `.husky/`, `lefthook.yml`, `.pre-commit-config.yaml`, and non-sample files in `.git/hooks/`. Record what each hook runs.
- **CI:** `.github/workflows/`, `.gitlab-ci.yml`, and other CI configuration. Record which checks run on pull requests and on which platforms.
- **Tracker:** GitHub issues when `origin` is on GitHub and `gh repo view --json hasIssuesEnabled` reports `true`; GitLab issues when `origin` is on GitLab and `glab` is installed; otherwise `none`, which leaves the line as `Tracker: none` without the ticket conventions.
- **Labels:** with a tracker, its current labels and a draft of the scheme, as [references/labels.md](references/labels.md) describes. Without a tracker, the line reads `Labels: none`.
- **Existing decision records:** `docs/adr/`, `docs/decisions/`, `adr/`, `doc/adr/`, `.agents/notes/`, `docs/rfcs/`, or ADR-style files elsewhere.
- **An older layout of this workflow:** decision notes with lifecycle folders in `docs/decisions/`, hooks in `.githooks/`, hook scripts in `scripts/`, hook settings at the root, or project skills in a real `.claude/skills/` directory. [references/layout.md](references/layout.md) lists what moves where.
- **House style:** the prose rules that a style guide (such as `CONTRIBUTING.md` or a docs style page) or a prose linter configuration (such as `.vale.ini` or `.markdownlint*`) states. Record only stated rules; with none, write `House style: none`.
- **Notes language:** the language of the repository's existing docs.
- **Hook checks:** whether the attribution check (`.agents/scripts/strip_attribution.py` and its hooks) and the file size check (`.agents/file-size.json` and `.agents/scripts/check_file_size.py`) are installed. On a refresh, `python .agents/scripts/check_file_size.py --all` shows whether the repository still passes the size limit.

Done when every field has a value backed by a file or command output, or is listed as a question for the user.

### 3. Draft the rows

List the kinds of change this repository has: source code per language or package group, tests, docs, manifests and build configuration, generated files. For each, choose the narrowest command that fails on a regression there: one test file or test name rather than the suite, one package rather than the workspace, the changed files rather than the tree. Prefer a project script when it accepts those targets; otherwise call the tool directly. In a monorepo whose packages use different commands, write one row per package group.

Done when every kind of change has a row, or a recorded reason why no check applies to it.

### 4. Prove every row

Run each focused command once against one real target, and read its output to confirm it ran only that target, for example by checking the reported test or file count. This step catches argument-forwarding mistakes, such as a `--` separator that a script runner passes on to the test tool. A broad command, such as a full build or a whole-project typecheck, only needs to exist in a manifest; run it as well when it finishes in about a minute. Fix or drop every row whose command fails. If a command fails because the repository is already broken, keep the row and note the failure for the report.

Done when every row was run, or is a broad command you confirmed exists.

### 5. Confirm with the user

Show the drafted section, or on a refresh only the differences from the current one. Ask all open questions in one message: the base branch when detection was ambiguous, the tracker, the label scheme with the plan for each existing label (see [references/labels.md](references/labels.md)), the notes directory (an existing records directory, otherwise `.agents/notes/`), the move of an older layout of this workflow to `.agents/` when one exists, the notes language, when records in another format exist, whether to migrate them now, and which hook checks to install that are not installed yet: the attribution check, recommended for every repository, and the file size check, with its preview (see [references/hooks.md](references/hooks.md)).

Done when the user has approved the section.

### 6. Write

Write the section and the `CLAUDE.md` import planned in step 1. Create the `.agents/` layout and the `.claude/skills` link, moving an older layout first, as [references/layout.md](references/layout.md) describes. Leave the notes directory uncreated: the `decision-notes` skill creates folders when it writes the first note. If the user chose to migrate existing records, follow "Adopt existing records" in the `decision-notes` skill. Install the hook checks the user chose as [references/hooks.md](references/hooks.md) describes. With a tracker, apply the approved label plan as [references/labels.md](references/labels.md) describes. Leave the changes uncommitted unless the user asked for a commit; then commit them with the `commit` skill.

### 7. Report

State the files changed, each row and whether it was run, the labels created, renamed, merged, or kept, the answers the user gave, and anything that needs attention, such as a hook that repeats CI work or a check that already fails on the base branch.
