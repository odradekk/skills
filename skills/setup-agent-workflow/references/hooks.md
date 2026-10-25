# Hook checks

Three optional checks run as git hooks. Each runs a Python 3.10+ script copied into `.agents/scripts/`, because hooks and CI cannot reach the skill directory, and all install the same way.

| Check | Hooks | Script | What it does |
|---|---|---|---|
| AI attribution | commit-msg, pre-push | `strip_attribution.py` | Removes AI attribution lines from commit messages as they are written, and rejects a push of commits that still carry them, or whose author is an AI tool, with a command that rewrites those unpushed commits. Recommended for every repository. |
| Frozen notes | post-checkout, post-merge, post-rewrite | `note_lifecycle.py` | Makes the decision notes in `accepted/`, `rejected/`, and `archived/` read-only again after git writes them, since git does not record the flag. The same script is the only way frozen notes change. Recommended for every repository with decision notes. |
| File size | pre-commit | `check_file_size.py` | Keeps the files agents edit under a token budget, so an agent can read them whole. |

The skill's `scripts/` directory holds each script, its hook templates, and their tests, except `note_lifecycle.py` and its tests, which belong to the `decision-notes` skill.

## Install, for step 6

1. Copy each chosen script from this skill's `scripts/` directory to `.agents/scripts/`, and for the frozen-notes check `note_lifecycle.py` from the `decision-notes` skill's `scripts/` directory (`../decision-notes/scripts/` from this skill's directory).
2. Copy the hook templates into `.agents/hooks/`: `commit-msg-attribution` to `.agents/hooks/commit-msg`, `pre-push-attribution` to `.agents/hooks/pre-push`, `pre-commit-file-size` to `.agents/hooks/pre-commit`, and `frozen-notes` to `.agents/hooks/post-checkout`, `.agents/hooks/post-merge`, and `.agents/hooks/post-rewrite`. When the notes directory is not `.agents/notes`, change the `NOTES=` line of the three copies. Run `chmod +x` on each, and write `* text eol=lf` to `.agents/hooks/.gitattributes`, so that a checkout with `core.autocrlf` does not give the shell scripts Windows line endings. When `.agents/hooks/` already has a hook of that name, call the template from it instead of replacing it.
3. Connect the hooks to the repository's hook setup:
   - **No hook manager:** `git config core.hooksPath .agents/hooks`. This setting applies to one clone only. In an npm project, offer to add `git config core.hooksPath .agents/hooks` to the `prepare` script in `package.json`, so `npm install` connects the hooks in every new clone and cloud environment; otherwise the Hooks line records the command for new clones. If `.git/hooks/` already holds hooks, changing `core.hooksPath` turns them off; ask the user first.
   - **husky:** add `sh .agents/hooks/commit-msg "$1"` to `.husky/commit-msg`, `sh .agents/hooks/pre-push "$@"` to `.husky/pre-push`, and `sh .agents/hooks/pre-commit` to `.husky/pre-commit`.
   - **lefthook:** in `lefthook.yml`, add a command `run: sh .agents/hooks/commit-msg {1}` under `commit-msg`, a command `run: sh .agents/hooks/pre-push` with `use_stdin: true` under `pre-push`, and a command `run: sh .agents/hooks/pre-commit` under `pre-commit`.
   - **pre-commit framework:** add local hooks with `language: system` and `pass_filenames: false`: `entry: sh .agents/hooks/commit-msg` with `stages: [commit-msg]`, and `entry: sh .agents/hooks/pre-commit` with `always_run: true`. The framework does not pass git's list of pushed refs to a pre-push hook, so the pre-push check cannot run there; tell the user.
   - **The frozen-notes hooks** connect the same way under each manager: `sh .agents/hooks/post-checkout`, `sh .agents/hooks/post-merge`, and `sh .agents/hooks/post-rewrite` under the hooks of those names, or, in the pre-commit framework, local hooks with `stages: [post-checkout]`, `[post-merge]`, and `[post-rewrite]` and `always_run: true`.
4. Do the per-check steps below.
5. Record the hooks in the Hooks line, with how they are connected.

Done when the checks below pass. Report how the hooks are connected. When the user commits these files from Windows, remind them to record the executable bits with `git update-index --chmod=+x .agents/hooks/*` once the files are staged.

## AI attribution

The rules live in the docstring of `strip_attribution.py`: which trailers and lines count as attribution, and the list of AI tool names. A project adds tool names, as regular expressions, in `.agents/attribution.json`: `{"identities": ["my-agent"]}`. The check needs no other settings.

Verify the installed hooks without committing anything: write a message with a `Co-Authored-By: Claude <noreply@anthropic.com>` line to a temporary file outside the repository, run `sh .agents/hooks/commit-msg <file>`, and confirm the line is gone; then run `sh .agents/hooks/pre-push origin origin </dev/null` and confirm it exits 0.

## Frozen notes

The rules for frozen notes live in the `decision-notes` skill: only `note_lifecycle.py` changes a note in `accepted/`, `rejected/`, or `archived/`, on the user's word, and the read-only flag makes a hand edit fail at once. The flag stops an agent's editing tools, not a deliberate `chmod`; the `decision-notes` verifier with `--base`, which the `pre-push-checks` skill runs, rejects any frozen note that changed anyway.

Make the existing frozen notes read-only once: `python .agents/scripts/note_lifecycle.py .agents/notes protect`. On a refresh, copy `note_lifecycle.py` again when the one in the `decision-notes` skill has changed.

Verify: `sh .agents/hooks/post-checkout` exits 0, and a note in `accepted/`, if there is one, is read-only afterwards.

## File size

Agents read a file whole before editing it, and they add to existing files far more often than they split them. The pre-commit hook checks the staged content of staged files against a token budget, estimated as bytes / 4; CI checks every tracked file. Files already over the limit when the check is installed go into a baseline: each may shrink but not grow. A failure message tells the agent how to split the file.

### Default settings

```json
{
  "max_tokens": 5000,
  "exclude": [
    "**/*.lock", "**/package-lock.json", "**/pnpm-lock.yaml", "**/go.sum",
    "**/*.min.js", "**/*.min.css", "**/*.map",
    "**/*.generated.*", "**/__generated__/**", "**/__snapshots__/**",
    "**/vendor/**", "**/third_party/**",
    "**/*.svg"
  ],
  "exceptions": {}
}
```

The exclusions cover files nobody reads whole to edit: lockfiles, minified files and source maps, generated code and test snapshots, third-party code, and SVG exported from design tools. Build output directories such as `dist/` are usually ignored by git and so never checked. Binary files are always skipped. Add the repository's own generated or data paths, such as a schema dump or a large fixture.

### Preview, for step 5

Before asking the user, show which files the baseline would record. Write the settings to a temporary file outside the repository, then run from the repository root:

```sh
python <this skill's directory>/scripts/check_file_size.py --all --config <temporary file>
```

Every file it reports would go into the baseline. Show the settings and that list, and ask whether to install the check and whether any listed file belongs in `exclude` or `exceptions` instead.

### Per-check steps

1. Write the approved settings to `.agents/file-size.json`.
2. Create the baseline: `python .agents/scripts/check_file_size.py --write-baseline`.
3. In the CI workflow that runs on pull requests, add a step that runs `python3 .agents/scripts/check_file_size.py --all` (Python 3.10 or later; `python` on Windows runners). Without CI, tell the user that only the hook enforces the limit, and `git commit --no-verify` skips the hook.
4. Add a `File size` line to the section, and the CI step to the CI line:

   ```markdown
   - File size: files stay under 5,000 tokens (bytes / 4) so an agent can read them whole. `.agents/file-size.json` lists excluded paths, exceptions with their reasons, and the baseline of older files over the limit, which may shrink but not grow. The pre-commit hook and CI run `.agents/scripts/check_file_size.py`.
   ```

Verify: `python .agents/scripts/check_file_size.py --all` exits 0, and `sh .agents/hooks/pre-commit` exits 0. Report the baseline entries.
