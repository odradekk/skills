# Repository layout

Everything this workflow installs in a repository lives under `.agents/`, so one tree serves every agent and the root holds only what must be there:

```
AGENTS.md                          instructions every agent reads; agents look for it at the root
CLAUDE.md                          one line, @AGENTS.md, because Claude Code reads CLAUDE.md
.claude/skills -> ../.agents/skills   link, so Claude Code loads the project skills
.agents/
  notes/                           decision notes; accepted/, rejected/, and archived/ are frozen and read-only,
                                   each with an AGENTS.md that says so; notes/.rgignore keeps archived/ out of searches
  skills/                          project skills, such as the generated <repo>-code-review
  hooks/                           git hooks; core.hooksPath points here; hooks/.gitattributes keeps LF
  scripts/                         the scripts the hooks run
  file-size.json                   settings of the file size check
  attribution.json                 extra AI tool names for the attribution check, when needed
```

A plain `rg` from the root skips directories whose names start with a dot; the workflow skills always name `.agents/` paths explicitly. People searching the whole repository add `--hidden`.

## The `.claude/skills` link

Claude Code loads project skills from `.claude/skills`, so that path is a relative symbolic link to `../.agents/skills`. Record the link in git directly; this works on every platform, including Windows without permission to create links, and stages the link:

```sh
mkdir -p .claude
git update-index --add --cacheinfo "120000,$(printf '../.agents/skills' | git hash-object -w --stdin),.claude/skills"
```

Then make the working tree match:

- **Where symbolic links work** (Linux, macOS, and Windows with Developer Mode and `core.symlinks` set to `true`): `git checkout -- .claude/skills`.
- **On Windows without them**, git writes `.claude/skills` as a small text file holding the path. Replace it with a directory junction, which needs no administrator rights, and tell git to leave it alone in this clone:

  ```sh
  rm -f .claude/skills
  cmd //c "mklink /J .claude\skills .agents\skills"
  git update-index --skip-worktree .claude/skills
  echo '/.claude/skills/' >> .git/info/exclude
  ```

  The repair belongs to one clone. Repeat it in each new Windows clone, or enable Developer Mode once per machine and set `git config --global core.symlinks true`, after which `git checkout -- .claude/skills` creates a real link.

Done when `.claude/skills/` lists the same skills as `.agents/skills/` and `git status` shows nothing for `.claude/skills`.

## Move an older layout

Earlier versions of this workflow used other paths. Move each one that exists in the same change, with `git mv` for tracked files and `mv` for untracked ones:

| Older path | New path |
|---|---|
| `docs/decisions/`, holding the lifecycle folders | `.agents/notes/` |
| The `docs/decisions/archived/` line in the root `.rgignore` | `archived/` in `.agents/notes/.rgignore` |
| `.githooks/` | `.agents/hooks/` |
| The `.githooks/* text eol=lf` line in the root `.gitattributes` | `* text eol=lf` in `.agents/hooks/.gitattributes` |
| `scripts/check_file_size.py`, `scripts/strip_attribution.py` | `.agents/scripts/` |
| `.file-size.json`, `.attribution.json` | `.agents/file-size.json`, `.agents/attribution.json` |
| `.claude/skills/` as a real directory | `.agents/skills/`, then the link above |

Then update everything that names the old paths:

- the script paths inside the hooks, and `git config core.hooksPath .agents/hooks` together with a `prepare` script or hook manager calls that name `.githooks`;
- the Agent workflow section;
- links into the notes from files outside the notes directory.

Note IDs are filenames, so ticket references survive the move. Links between notes, and from notes to the rest of the repository, stay valid because `docs/decisions/` and `.agents/notes/` sit at the same depth. Archived notes move with the tree unchanged, which keeps them frozen.

Done when the `decision-notes` verifier passes on `.agents/notes/`, the hooks run from `.agents/hooks/`, and no file names an old path.
