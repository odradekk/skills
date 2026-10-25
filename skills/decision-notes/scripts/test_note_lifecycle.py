"""Tests for note_lifecycle.py. Run: python -m unittest discover -s skills/decision-notes/scripts"""

import os
import stat
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

LIFECYCLE = Path(__file__).with_name("note_lifecycle.py")
VERIFIER = Path(__file__).with_name("verify_notes.py")

PROPOSAL = """\
# {title}

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


def run(script, *args):
    return subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True)


class NoteLifecycleTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        # Cleanups run last in, first out: frozen notes become writable before the directory goes.
        self.addCleanup(self.make_writable, Path(temp.name))
        self.notes = Path(temp.name) / "notes"

    def make_writable(self, root):
        for path in root.rglob("*"):
            if path.is_file():
                os.chmod(path, stat.S_IREAD | stat.S_IWRITE)

    def propose(self, note_id, text=None, newline="\n"):
        path = self.notes / "proposed" / "architecture" / f"{note_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        body = text or PROPOSAL.format(title=note_id)
        with open(path, "w", encoding="utf-8", newline=newline) as file:
            file.write(body)
        return path

    def lifecycle(self, *args):
        return run(LIFECYCLE, self.notes, *args)

    def accept(self, note_id):
        result = self.lifecycle("accept", note_id)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def lines(self, relative):
        return (self.notes / relative).read_text(encoding="utf-8").splitlines()

    def is_read_only(self, relative):
        return not os.access(self.notes / relative, os.W_OK)

    def assert_verified(self):
        result = run(VERIFIER, self.notes)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_accept_freezes_a_proposal(self):
        self.propose("2026-01-01-parse-policy-once")

        self.accept("2026-01-01-parse-policy-once")

        path = "accepted/architecture/2026-01-01-parse-policy-once.md"
        self.assertEqual(self.lines(path)[2], "Status: accepted")
        self.assertTrue(self.is_read_only(path))
        self.assertFalse((self.notes / "proposed/architecture/2026-01-01-parse-policy-once.md").exists())
        self.assertTrue((self.notes / "accepted/AGENTS.md").is_file())
        self.assertEqual((self.notes / "accepted/CLAUDE.md").read_text(encoding="utf-8"), "@AGENTS.md\n")
        self.assert_verified()

    def test_only_a_proposal_can_be_accepted(self):
        self.propose("2026-01-01-parse-policy-once")
        self.accept("2026-01-01-parse-policy-once")

        result = self.lifecycle("accept", "2026-01-01-parse-policy-once")

        self.assertEqual(result.returncode, 1)
        self.assertIn("proposed", result.stderr)

    def test_reject_records_the_reason(self):
        self.propose("2026-01-01-parse-policy-once")

        result = self.lifecycle("reject", "2026-01-01-parse-policy-once", "callers already parse")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        path = "rejected/architecture/2026-01-01-parse-policy-once.md"
        self.assertEqual(self.lines(path)[2], "Status: rejected — callers already parse")
        self.assertTrue(self.is_read_only(path))
        self.assert_verified()

    def test_full_supersession_links_both_notes_and_archives_the_old_one(self):
        self.propose("2026-01-01-old-policy")
        self.propose("2026-02-01-new-policy")
        self.accept("2026-01-01-old-policy")
        self.accept("2026-02-01-new-policy")

        result = self.lifecycle("supersede", "2026-02-01-new-policy", "2026-01-01-old-policy")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        new = self.lines("accepted/architecture/2026-02-01-new-policy.md")
        old = self.lines("archived/architecture/2026-01-01-old-policy.md")
        self.assertEqual(new[3], "Supersedes: 2026-01-01-old-policy")
        self.assertEqual(old[3:5], [f"Archived: {date.today().isoformat()}", "Superseded by: 2026-02-01-new-policy"])
        self.assertTrue(self.is_read_only("archived/architecture/2026-01-01-old-policy.md"))
        self.assertTrue(self.is_read_only("accepted/architecture/2026-02-01-new-policy.md"))
        self.assertIn("archived/", (self.notes / ".rgignore").read_text(encoding="utf-8").splitlines())
        self.assert_verified()

    def test_partial_supersession_keeps_the_old_note_accepted(self):
        self.propose("2026-01-01-old-policy")
        self.propose("2026-02-01-new-policy")
        self.accept("2026-01-01-old-policy")
        self.accept("2026-02-01-new-policy")

        result = self.lifecycle("supersede", "2026-02-01-new-policy", "2026-01-01-old-policy", "--part", "the cache")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        new = self.lines("accepted/architecture/2026-02-01-new-policy.md")
        old = self.lines("accepted/architecture/2026-01-01-old-policy.md")
        self.assertEqual(new[3], "Supersedes in part: 2026-01-01-old-policy — the cache")
        self.assertEqual(old[3], "Superseded in part by: 2026-02-01-new-policy — the cache")
        self.assert_verified()

    def test_supersession_needs_two_accepted_notes(self):
        self.propose("2026-01-01-old-policy")
        self.propose("2026-02-01-new-policy")
        self.accept("2026-01-01-old-policy")

        result = self.lifecycle("supersede", "2026-02-01-new-policy", "2026-01-01-old-policy")

        self.assertEqual(result.returncode, 1)
        self.assertIn("accepted", result.stderr)
        self.assertEqual(self.lines("accepted/architecture/2026-01-01-old-policy.md")[3], "")

    def test_archive_moves_a_rejected_note(self):
        self.propose("2026-01-01-parse-policy-once")
        self.lifecycle("reject", "2026-01-01-parse-policy-once", "callers already parse")

        result = self.lifecycle("archive", "2026-01-01-parse-policy-once")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        lines = self.lines("archived/architecture/2026-01-01-parse-policy-once.md")
        self.assertEqual(lines[2:4], ["Status: rejected — callers already parse", f"Archived: {date.today().isoformat()}"])
        self.assert_verified()

    def test_edits_keep_the_line_endings_of_the_file(self):
        self.propose("2026-01-01-parse-policy-once", newline="\r\n")

        self.accept("2026-01-01-parse-policy-once")

        data = (self.notes / "accepted/architecture/2026-01-01-parse-policy-once.md").read_bytes()
        self.assertEqual(data.count(b"\n"), data.count(b"\r\n"))

    def test_protect_makes_frozen_notes_read_only_and_proposals_writable(self):
        self.propose("2026-01-01-parse-policy-once")
        self.accept("2026-01-01-parse-policy-once")
        proposal = self.propose("2026-02-01-new-policy")
        frozen = self.notes / "accepted/architecture/2026-01-01-parse-policy-once.md"
        os.chmod(frozen, stat.S_IREAD | stat.S_IWRITE)
        os.chmod(proposal, stat.S_IREAD)

        result = self.lifecycle("protect")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(self.is_read_only("accepted/architecture/2026-01-01-parse-policy-once.md"))
        self.assertFalse(self.is_read_only("proposed/architecture/2026-02-01-new-policy.md"))


if __name__ == "__main__":
    unittest.main()
