# File size check

Agents read a file whole before editing it, and they add to existing files far more often than they split them. This optional check keeps the files agents edit under a token budget, estimated as bytes / 4. The pre-commit hook checks the staged content of staged files; CI checks every tracked file. Files already over the limit when the check is installed go into a baseline: each may shrink but not grow. A failure message tells the agent how to split the file.

The skill's `scripts/` directory holds the three pieces: `check_file_size.py` (the check), `pre-commit-file-size` (the hook), and their tests.

## Default settings

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

## Preview, for step 5

Before asking the user, show which files the baseline would record. Write the settings to a temporary file outside the repository, then run from the repository root:

```sh
python <this skill's directory>/scripts/check_file_size.py --all --config <temporary file>
```

Every file it reports would go into the baseline. Show the settings and that list, and ask whether to install the check and whether any listed file belongs in `exclude` or `exceptions` instead.

## Install, for step 6

1. Copy `check_file_size.py` from this skill's `scripts/` directory to `scripts/check_file_size.py` in the repository; hooks and CI cannot reach the skill directory. If the repository keeps its tools in another folder, use that folder and change the path in the hook.
2. Write the approved settings to `.file-size.json` at the repository root.
3. Create the baseline: `python scripts/check_file_size.py --write-baseline`.
4. Copy `pre-commit-file-size` to `.githooks/pre-commit`, run `chmod +x` on it, and add `.githooks/* text eol=lf` to `.gitattributes`, so that a checkout with `core.autocrlf` does not give the shell script Windows line endings.
5. Connect the hook to the repository's hook setup:
   - **No hook manager:** `git config core.hooksPath .githooks`. This setting applies to one clone only, so the Hooks line records the command for new clones. If `.git/hooks/` already holds hooks, changing `core.hooksPath` turns them off; ask the user first.
   - **husky:** add `sh .githooks/pre-commit` to `.husky/pre-commit`.
   - **lefthook:** add a `file-size` command with `run: sh .githooks/pre-commit` under `pre-commit` in `lefthook.yml`.
   - **pre-commit framework:** add a local hook with `entry: sh .githooks/pre-commit`, `language: system`, `pass_filenames: false`, and `always_run: true`.
6. In the CI workflow that runs on pull requests, add a step that runs `python3 scripts/check_file_size.py --all` (Python 3.10 or later; `python` on Windows runners). Without CI, tell the user that only the hook enforces the limit, and `git commit --no-verify` skips the hook.
7. Add the check to the section: a `File size` line, and the hook and CI step in the Hooks and CI lines:

   ```markdown
   - File size: files stay under 5,000 tokens (bytes / 4) so an agent can read them whole. `.file-size.json` lists excluded paths, exceptions with their reasons, and the baseline of older files over the limit, which may shrink but not grow. The pre-commit hook and CI run `scripts/check_file_size.py`.
   ```

Done when `python scripts/check_file_size.py --all` exits 0 and running `sh .githooks/pre-commit` exits 0. Report the baseline entries and how the hook is connected. When the user commits these files from Windows, remind them to record the hook's executable bit with `git update-index --chmod=+x .githooks/pre-commit` once the file is staged.
