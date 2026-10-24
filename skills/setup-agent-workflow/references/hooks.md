# Hook checks

Two optional checks run as git hooks. Both run a Python 3.10+ script that is copied into the repository, because hooks and CI cannot reach the skill directory, and both install the same way.

| Check | Hooks | Script | What it does |
|---|---|---|---|
| AI attribution | commit-msg, pre-push | `strip_attribution.py` | Removes AI attribution lines from commit messages as they are written, and rejects a push of commits that still carry them, or whose author is an AI tool, with a command that rewrites those unpushed commits. Recommended for every repository. |
| File size | pre-commit | `check_file_size.py` | Keeps the files agents edit under a token budget, so an agent can read them whole. |

The skill's `scripts/` directory holds each script, its hook templates, and their tests.

## Install, for step 6

1. Copy each chosen script from this skill's `scripts/` directory to `scripts/` in the repository. If the repository keeps its tools in another folder, use that folder and change the path in the hooks.
2. Copy the hook templates into `.githooks/`: `commit-msg-attribution` to `.githooks/commit-msg`, `pre-push-attribution` to `.githooks/pre-push`, and `pre-commit-file-size` to `.githooks/pre-commit`. Run `chmod +x` on each, and add `.githooks/* text eol=lf` to `.gitattributes`, so that a checkout with `core.autocrlf` does not give the shell scripts Windows line endings. When `.githooks/` already has a hook of that name, call the template from it instead of replacing it.
3. Connect the hooks to the repository's hook setup:
   - **No hook manager:** `git config core.hooksPath .githooks`. This setting applies to one clone only. In an npm project, offer to add `git config core.hooksPath .githooks` to the `prepare` script in `package.json`, so `npm install` connects the hooks in every new clone and cloud environment; otherwise the Hooks line records the command for new clones. If `.git/hooks/` already holds hooks, changing `core.hooksPath` turns them off; ask the user first.
   - **husky:** add `sh .githooks/commit-msg "$1"` to `.husky/commit-msg`, `sh .githooks/pre-push "$@"` to `.husky/pre-push`, and `sh .githooks/pre-commit` to `.husky/pre-commit`.
   - **lefthook:** in `lefthook.yml`, add a command `run: sh .githooks/commit-msg {1}` under `commit-msg`, a command `run: sh .githooks/pre-push` with `use_stdin: true` under `pre-push`, and a command `run: sh .githooks/pre-commit` under `pre-commit`.
   - **pre-commit framework:** add local hooks with `language: system` and `pass_filenames: false`: `entry: sh .githooks/commit-msg` with `stages: [commit-msg]`, and `entry: sh .githooks/pre-commit` with `always_run: true`. The framework does not pass git's list of pushed refs to a pre-push hook, so the pre-push check cannot run there; tell the user.
4. Do the per-check steps below.
5. Record the hooks in the Hooks line, with how they are connected.

Done when the checks below pass. Report how the hooks are connected. When the user commits these files from Windows, remind them to record the executable bits with `git update-index --chmod=+x .githooks/*` once the files are staged.

## AI attribution

The rules live in the docstring of `strip_attribution.py`: which trailers and lines count as attribution, and the list of AI tool names. A project adds tool names, as regular expressions, in `.attribution.json` at the repository root: `{"identities": ["my-agent"]}`. The check needs no other settings.

Verify the installed hooks without committing anything: write a message with a `Co-Authored-By: Claude <noreply@anthropic.com>` line to a temporary file outside the repository, run `sh .githooks/commit-msg <file>`, and confirm the line is gone; then run `sh .githooks/pre-push origin origin </dev/null` and confirm it exits 0.

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

1. Write the approved settings to `.file-size.json` at the repository root.
2. Create the baseline: `python scripts/check_file_size.py --write-baseline`.
3. In the CI workflow that runs on pull requests, add a step that runs `python3 scripts/check_file_size.py --all` (Python 3.10 or later; `python` on Windows runners). Without CI, tell the user that only the hook enforces the limit, and `git commit --no-verify` skips the hook.
4. Add a `File size` line to the section, and the CI step to the CI line:

   ```markdown
   - File size: files stay under 5,000 tokens (bytes / 4) so an agent can read them whole. `.file-size.json` lists excluded paths, exceptions with their reasons, and the baseline of older files over the limit, which may shrink but not grow. The pre-commit hook and CI run `scripts/check_file_size.py`.
   ```

Verify: `python scripts/check_file_size.py --all` exits 0, and `sh .githooks/pre-commit` exits 0. Report the baseline entries.
