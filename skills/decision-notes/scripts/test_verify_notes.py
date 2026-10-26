"""Tests for verify_notes.py. Run: python -m unittest discover -s skills/decision-notes/scripts"""

import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("verify_notes.py")
# Built at run time, so that this file holds no citation for the verifier to check where the skill is installed.
CITE = "Decision" + " note: "

PROPOSED = """\
# Parse the policy once

Status: proposed

## Problem

The resolver parses a policy that its callers already parsed.

## Proposal

Pass the parsed policy to the resolver.

## Alternatives considered

**Keep the second parse.** It protects callers that do not exist.

## Acceptance criteria

Malformed policies are still rejected.

## Risks

A future caller must parse before calling the resolver.
"""

ACCEPTED = """\
# Event-sourced sessions

Status: accepted

## Problem

Session state was rebuilt from mutable files.

## Proposal

The session log becomes the only source of truth.

```markdown
## Problem

This heading is an example inside a code block.
```

## Alternatives considered

**Snapshot files.** They drift from the log.

## Acceptance criteria

A session replays exactly from its log.

## Risks

The log grows without bound.
"""

REJECTED = """\
# Merge the compaction packages

Status: rejected — the split keeps ownership clear

## Problem

Two packages share one release cadence.

## Proposal

Merge them into one package.

## Alternatives considered

**Keep the split.** Each package keeps one owner.
"""

ARCHIVED = """\
# Old storage layout

Status: accepted
Archived: 2026-03-01

## Problem

This link pointed at a file that no longer exists: [old](../../missing.md).
"""


def run_verifier(notes_dir, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(notes_dir), *args], capture_output=True, text=True
    )


def git(root, *args):
    subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=test", "-c", "user.email=test@example.com",
         "-c", "commit.gpgsign=false", "-c", "core.hooksPath=", *args],
        check=True, capture_output=True,
    )


class VerifyNotesTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.notes = self.root / "notes"
        self.notes.mkdir()

    def write(self, relative, text):
        path = self.notes / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
        path.write_text(text, encoding="utf-8")
        return path

    def write_source(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def commit_base(self):
        git(self.root, "init", "-q")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "base")

    def assert_problem(self, result, fragment):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(fragment, result.stdout)

    def assert_clean(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_valid_tree_passes(self):
        citation = f"\nIt builds on {CITE}2026-01-01-event-sourced-sessions.\n"
        self.write("proposed/architecture/2026-01-02-parse-policy-once.md", PROPOSED + citation)
        self.write("accepted/architecture/2026-01-01-event-sourced-sessions.md", ACCEPTED)
        self.write("accepted/AGENTS.md", "# Accepted decision notes\n")
        self.write("accepted/CLAUDE.md", "@AGENTS.md\n")
        self.write("rejected/simplification/2026-01-03-merge-compaction-packages.md", REJECTED)
        self.write("archived/architecture/2025-12-01-old-storage-layout.md", ARCHIVED)
        self.assert_clean(run_verifier(self.notes))

    def test_status_must_match_lifecycle_folder(self):
        self.write("accepted/feature/2026-01-02-parse-policy-once.md", PROPOSED)
        self.assert_problem(run_verifier(self.notes), "line 3 must be 'Status: accepted'")

    def test_layout_rejects_unknown_class_and_bad_filename(self):
        self.write("proposed/refactor/2026-01-02-parse-policy-once.md", PROPOSED)
        self.write("proposed/feature/Parse_Policy.md", PROPOSED)
        result = run_verifier(self.notes)
        self.assert_problem(result, "refactor: unexpected entry")
        self.assertIn("Parse_Policy.md: notes are files named", result.stdout)

    def test_missing_required_section(self):
        self.write("accepted/feature/2026-01-02-parse-policy-once.md",
                   PROPOSED.replace("Status: proposed", "Status: accepted").replace("## Risks", "## Downsides"))
        self.assert_problem(run_verifier(self.notes), "missing required section '## Risks'")

    def test_marker_stands_in_for_alternatives(self):
        section = "## Alternatives considered\n\n**Snapshot files.** They drift from the log.\n"
        text = ACCEPTED.replace(section, "<!-- decision-notes: alternatives-not-recorded -->\n")
        self.assertNotEqual(text, ACCEPTED)
        self.write("accepted/architecture/2026-01-01-event-sourced-sessions.md", text)
        self.assert_clean(run_verifier(self.notes))

    def test_broken_relative_link_in_a_proposal(self):
        self.write("proposed/architecture/2026-01-02-parse-policy-once.md", PROPOSED + "\nSee [the guide](../../missing.md).\n")
        self.assert_problem(run_verifier(self.notes), "broken link '../../missing.md'")

    def test_a_proposal_refers_to_another_note_by_id(self):
        self.write("accepted/architecture/2026-01-01-event-sourced-sessions.md", ACCEPTED)
        link = "\nSee [sessions](../../accepted/architecture/2026-01-01-event-sourced-sessions.md).\n"
        self.write("proposed/architecture/2026-01-02-parse-policy-once.md", PROPOSED + link)
        self.assert_problem(run_verifier(self.notes), "refer to another note by its ID")

    def test_a_proposal_cites_a_missing_note(self):
        self.write("proposed/architecture/2026-01-02-parse-policy-once.md", PROPOSED + f"\n{CITE}2026-01-09-gone\n")
        self.assert_problem(run_verifier(self.notes), "cites decision note '2026-01-09-gone', which does not exist")

    def test_archived_note_needs_archived_line(self):
        text = ARCHIVED.replace("Archived: 2026-03-01\n", "")
        self.write("archived/architecture/2025-12-01-old-storage-layout.md", text)
        self.assert_problem(run_verifier(self.notes), "line 4 must be 'Archived: YYYY-MM-DD'")

    def test_header_holds_only_the_lines_the_lifecycle_script_writes(self):
        text = ACCEPTED.replace("Status: accepted\n", "Status: accepted\nOwner: the storage team\n")
        self.write("accepted/architecture/2026-01-01-event-sourced-sessions.md", text)
        self.assert_problem(run_verifier(self.notes), "sessions.md:4: 'Owner: the storage team' is not a header line")

    def test_supersession_links_go_both_ways(self):
        old = ACCEPTED.replace("# Event-sourced sessions", "# Snapshot sessions")
        new = ACCEPTED.replace("Status: accepted\n", "Status: accepted\nSupersedes: 2026-01-01-snapshot-sessions\n")
        self.write("accepted/architecture/2026-01-01-snapshot-sessions.md", old)
        self.write("accepted/architecture/2026-02-01-event-sourced-sessions.md", new)
        self.assert_problem(run_verifier(self.notes),
                            "2026-01-01-snapshot-sessions has no 'Superseded by: 2026-02-01-event-sourced-sessions'")

    def test_base_reports_edits_and_deletions_of_frozen_notes(self):
        self.write("accepted/architecture/2026-01-01-event-sourced-sessions.md", ACCEPTED)
        self.write("rejected/simplification/2026-01-03-merge-compaction-packages.md", REJECTED)
        self.write("archived/architecture/2025-12-01-old-storage-layout.md", ARCHIVED)
        self.commit_base()
        self.write("accepted/architecture/2026-01-01-event-sourced-sessions.md", ACCEPTED + "\nA later edit.\n")
        (self.notes / "rejected/simplification/2026-01-03-merge-compaction-packages.md").unlink()
        self.write("archived/architecture/2025-12-01-old-storage-layout.md", ARCHIVED + "\nA later edit.\n")

        result = run_verifier(self.notes, "--base", "HEAD")

        self.assert_problem(result, "2026-01-01-event-sourced-sessions.md: frozen note changed since HEAD")
        self.assertIn("2026-01-03-merge-compaction-packages.md: frozen note deleted since HEAD", result.stdout)
        self.assertIn("2025-12-01-old-storage-layout.md: frozen note changed since HEAD", result.stdout)

    def test_base_reports_a_frozen_note_moved_back_to_proposals(self):
        self.write("accepted/architecture/2026-01-01-event-sourced-sessions.md", ACCEPTED)
        self.commit_base()
        (self.notes / "accepted/architecture/2026-01-01-event-sourced-sessions.md").unlink()
        self.write("proposed/architecture/2026-01-01-event-sourced-sessions.md",
                   ACCEPTED.replace("Status: accepted", "Status: proposed"))

        result = run_verifier(self.notes, "--base", "HEAD")

        self.assert_problem(result, "frozen note moved from accepted/ to proposed/ since HEAD")

    def test_base_allows_the_lifecycle_scripts_own_edits(self):
        old = ACCEPTED.replace("# Event-sourced sessions", "# Snapshot sessions")
        self.write("accepted/architecture/2026-01-01-snapshot-sessions.md", old)
        self.write("accepted/architecture/2026-02-01-event-sourced-sessions.md", ACCEPTED)
        self.commit_base()
        (self.notes / "accepted/architecture/2026-01-01-snapshot-sessions.md").unlink()
        self.write("archived/architecture/2026-01-01-snapshot-sessions.md", old.replace(
            "Status: accepted\n", "Status: accepted\nArchived: 2026-03-01\nSuperseded by: 2026-02-01-event-sourced-sessions\n"))
        self.write("accepted/architecture/2026-02-01-event-sourced-sessions.md", ACCEPTED.replace(
            "Status: accepted\n", "Status: accepted\nSupersedes: 2026-01-01-snapshot-sessions\n"))

        self.assert_clean(run_verifier(self.notes, "--base", "HEAD"))

    def test_code_may_cite_notes_in_every_lifecycle(self):
        self.write("accepted/architecture/2026-01-01-event-sourced-sessions.md", ACCEPTED)
        self.write("proposed/architecture/2026-01-02-parse-policy-once.md", PROPOSED)
        self.write("rejected/simplification/2026-01-03-merge-compaction-packages.md", REJECTED)
        self.write("archived/architecture/2025-12-01-old-storage-layout.md", ARCHIVED)
        self.write_source("src/log.ts", f"/**\n * The log is the only source of truth.\n * {CITE}2026-01-01-event-sourced-sessions\n */\n")
        self.write_source("src/policy.py", f"# {CITE}2026-01-02-parse-policy-once\n# {CITE}2026-01-03-merge-compaction-packages\n")
        self.write_source("src/store.ts", f"// {CITE}2025-12-01-old-storage-layout\n")
        git(self.root, "init", "-q")
        git(self.root, "add", "src/log.ts")

        self.assert_clean(run_verifier(self.notes))

    def test_code_citation_of_a_missing_note(self):
        self.write("accepted/architecture/2026-01-01-event-sourced-sessions.md", ACCEPTED)
        self.write_source(".gitignore", "build/\n")
        self.write_source("build/out.js", f"// {CITE}2026-01-09-gone\n")
        self.write_source("src/added.ts", f"export const a = 1;\n// {CITE}2026-01-09-gone\n")
        git(self.root, "init", "-q")

        result = run_verifier(self.notes)

        self.assert_problem(result, "src/added.ts:2: cites decision note '2026-01-09-gone', which does not exist")
        self.assertNotIn("out.js", result.stdout)


if __name__ == "__main__":
    unittest.main()
