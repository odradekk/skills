"""Tests for verify_notes.py. Run: python -m unittest discover -s skills/decision-notes/scripts"""

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

IMPLEMENTED = """\
# Event-sourced sessions

Status: implemented

## Problem

Session state was rebuilt from mutable files.

## Decision

The session log is the only source of truth.

```markdown
## Proposal

This heading is an example inside a code block.
```

## Alternatives considered

**Snapshot files.** They drift from the log.

## Consequences

Replays are exact; the log grows without bound.
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

Status: implemented
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
         "-c", "commit.gpgsign=false", *args],
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
        path.write_text(text, encoding="utf-8")
        return path

    def write_source(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def assert_problem(self, result, fragment):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(fragment, result.stdout)

    def test_valid_tree_passes(self):
        link = "\nSee [the proposal](../../proposed/architecture/2026-01-02-parse-policy-once.md).\n"
        self.write("proposed/architecture/2026-01-02-parse-policy-once.md", PROPOSED)
        self.write("implemented/architecture/2026-01-01-event-sourced-sessions.md", IMPLEMENTED + link)
        self.write("rejected/simplification/2026-01-03-merge-compaction-packages.md", REJECTED)
        self.write("archived/architecture/2025-12-01-old-storage-layout.md", ARCHIVED)
        result = run_verifier(self.notes)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_status_must_match_lifecycle_folder(self):
        self.write("implemented/feature/2026-01-02-parse-policy-once.md", PROPOSED)
        self.assert_problem(run_verifier(self.notes), "line 3 must be 'Status: implemented'")

    def test_layout_rejects_unknown_class_and_bad_filename(self):
        self.write("proposed/refactor/2026-01-02-parse-policy-once.md", PROPOSED)
        self.write("proposed/feature/Parse_Policy.md", PROPOSED)
        result = run_verifier(self.notes)
        self.assert_problem(result, "refactor: unexpected entry")
        self.assertIn("Parse_Policy.md: notes are files named", result.stdout)

    def test_missing_required_section(self):
        self.write("proposed/feature/2026-01-02-parse-policy-once.md", PROPOSED.replace("## Risks", "## Downsides"))
        self.assert_problem(run_verifier(self.notes), "missing required section '## Risks'")

    def test_proposal_sections_are_not_allowed_in_implemented(self):
        text = IMPLEMENTED.replace("## Consequences", "## Acceptance criteria\n\nDone.\n\n## Consequences")
        self.write("implemented/architecture/2026-01-01-event-sourced-sessions.md", text)
        self.assert_problem(run_verifier(self.notes), "'## Acceptance criteria' is not allowed in implemented/")

    def test_marker_stands_in_for_alternatives(self):
        section = "## Alternatives considered\n\n**Snapshot files.** They drift from the log.\n"
        text = IMPLEMENTED.replace(section, "<!-- decision-notes: alternatives-not-recorded -->\n")
        self.assertNotEqual(text, IMPLEMENTED)
        self.write("implemented/architecture/2026-01-01-event-sourced-sessions.md", text)
        result = run_verifier(self.notes)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_broken_relative_link_in_active_note(self):
        text = IMPLEMENTED + "\nSee [the old note](../feature/2026-01-01-gone.md).\n"
        self.write("implemented/architecture/2026-01-01-event-sourced-sessions.md", text)
        self.assert_problem(run_verifier(self.notes), "broken link '../feature/2026-01-01-gone.md'")

    def test_archived_note_needs_archived_line(self):
        text = ARCHIVED.replace("Archived: 2026-03-01\n", "")
        self.write("archived/architecture/2025-12-01-old-storage-layout.md", text)
        self.assert_problem(run_verifier(self.notes), "line 4 must be 'Archived: YYYY-MM-DD'")

    def test_base_reports_changed_archived_note_only(self):
        sealed = self.write("archived/architecture/2025-12-01-old-storage-layout.md", ARCHIVED)
        git(self.root, "init", "-q")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "base")
        sealed.write_text(ARCHIVED + "\nA later edit.\n", encoding="utf-8")
        self.write("archived/feature/2026-02-01-newly-archived.md", ARCHIVED)

        result = run_verifier(self.notes, "--base", "HEAD")

        self.assert_problem(result, "2025-12-01-old-storage-layout.md: archived note changed since HEAD")
        self.assertNotIn("newly-archived", result.stdout)

    def test_code_may_cite_implemented_proposed_and_rejected_notes(self):
        self.write("implemented/architecture/2026-01-01-event-sourced-sessions.md", IMPLEMENTED)
        self.write("proposed/architecture/2026-01-02-parse-policy-once.md", PROPOSED)
        self.write("rejected/simplification/2026-01-03-merge-compaction-packages.md", REJECTED)
        self.write_source("src/log.ts", f"/**\n * The log is the only source of truth.\n * {CITE}2026-01-01-event-sourced-sessions\n */\n")
        self.write_source("src/policy.py", f"# {CITE}2026-01-02-parse-policy-once\n# {CITE}2026-01-03-merge-compaction-packages\n")
        git(self.root, "init", "-q")
        git(self.root, "add", "src/log.ts")

        result = run_verifier(self.notes)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_code_citation_of_a_missing_note(self):
        self.write("implemented/architecture/2026-01-01-event-sourced-sessions.md", IMPLEMENTED + f"\n{CITE}2026-01-09-gone\n")
        self.write_source(".gitignore", "build/\n")
        self.write_source("build/out.js", f"// {CITE}2026-01-09-gone\n")
        self.write_source("src/new.ts", f"export const a = 1;\n// {CITE}2026-01-09-gone\n")
        git(self.root, "init", "-q")

        result = run_verifier(self.notes)

        self.assert_problem(result, "src/new.ts:2: cites decision note '2026-01-09-gone', which does not exist")
        self.assertNotIn("out.js", result.stdout)
        self.assertNotIn("event-sourced-sessions.md", result.stdout)

    def test_code_citation_of_an_archived_note(self):
        self.write("archived/architecture/2025-12-01-old-storage-layout.md", ARCHIVED)
        self.write_source("src/store.ts", f"// {CITE}2025-12-01-old-storage-layout\n")
        git(self.root, "init", "-q")

        result = run_verifier(self.notes)

        self.assert_problem(result, "src/store.ts:1: cites archived decision note '2025-12-01-old-storage-layout'")


if __name__ == "__main__":
    unittest.main()
