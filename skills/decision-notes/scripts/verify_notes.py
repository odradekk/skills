#!/usr/bin/env python3
"""Check a decision-notes directory against the decision-notes format.

Usage: verify_notes.py NOTES_DIR [--base REF]

Checks the lifecycle/class/filename layout, each note's header and its
agreement with the lifecycle folder, required and disallowed sections, and
relative links in active notes. Archived notes get only the header check:
they are frozen, so later format rules and their outbound links never apply.
Inside a git repository, also checks every "Decision note: <ID>" citation in
the files outside the notes directory that git tracks or does not ignore: the
ID must name a note, and not an archived one. With --base, also reports
archived notes that existed at REF and were changed or removed since.
Exit status: 0 clean, 1 problems found, 2 usage or git error.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote

LIFECYCLES = ("proposed", "implemented", "rejected", "archived")
CLASSES = ("feature", "bug-fix", "simplification", "architecture", "process", "testing")
REQUIRED = {
    "proposed": ("Problem", "Proposal", "Alternatives considered", "Acceptance criteria", "Risks"),
    "implemented": ("Problem", "Decision", "Alternatives considered", "Consequences"),
    "rejected": ("Problem", "Proposal", "Alternatives considered"),
}
DISALLOWED = {"implemented": ("Proposal", "Plan", "Migration plan", "Acceptance criteria")}
ALTERNATIVES_MARKER = "<!-- decision-notes: alternatives-not-recorded -->"

FILENAME = re.compile(r"(\d{4}-\d{2}-\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.md")
REJECTED_STATUS = re.compile(r"Status: rejected — \S.*")
ARCHIVED_LINE = re.compile(r"Archived: (\d{4}-\d{2}-\d{2})")
FENCE = re.compile(r" {0,3}(`{3,}|~{3,})")
HEADING = re.compile(r"## +(.+?)(?: +#+)? *")
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?")
INLINE_CODE = re.compile(r"`+[^`]*`+")
SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
CITATION = re.compile(r"Decision note: (\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*)")
CITATION_LINE = r"Decision note: [0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]"  # git grep's ERE prefilter for CITATION

Problem = tuple[Path, "int | None", str]  # (path, line number or None, message)


def is_date(text: str) -> bool:
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


def outside_fences(lines: list[str]):
    """Yield (line number, line) for every line outside fenced code blocks."""
    fence = ""
    for number, line in enumerate(lines, 1):
        match = FENCE.match(line)
        if fence:
            closes = match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence)
            if closes and not line[match.end():].strip():
                fence = ""
        elif match:
            fence = match.group(1)
        else:
            yield number, line


def collect_notes(notes_dir: Path) -> tuple[list[tuple[Path, str]], list[Problem]]:
    """Return (note path, lifecycle) pairs and the layout problems found on the way."""
    notes, problems = [], []
    for lifecycle_dir in sorted(notes_dir.iterdir()):
        if lifecycle_dir.name.startswith("."):
            continue
        if not lifecycle_dir.is_dir() or lifecycle_dir.name not in LIFECYCLES:
            problems.append((lifecycle_dir, None, f"unexpected entry; only {', '.join(LIFECYCLES)} folders belong here"))
            continue
        for class_dir in sorted(lifecycle_dir.iterdir()):
            if class_dir.name.startswith("."):
                continue
            if not class_dir.is_dir() or class_dir.name not in CLASSES:
                problems.append((class_dir, None, f"unexpected entry; class folders are {', '.join(CLASSES)}"))
                continue
            for note in sorted(class_dir.iterdir()):
                if note.name.startswith("."):
                    continue
                match = FILENAME.fullmatch(note.name)
                if not note.is_file() or not match or not is_date(match.group(1)):
                    problems.append((note, None, "notes are files named YYYY-MM-DD-slug.md with a lowercase kebab-case slug"))
                    continue
                notes.append((note, lifecycle_dir.name))
    return notes, problems


def check_header(lines: list[str], lifecycle: str) -> list[tuple[int, str]]:
    def line(number: int) -> str:
        return lines[number - 1].rstrip() if len(lines) >= number else ""

    problems = []
    if not line(1).startswith("# ") or not line(1)[2:].strip():
        problems.append((1, "line 1 must be '# <title>'"))
    if line(2):
        problems.append((2, "line 2 must be blank"))
    if lifecycle == "rejected":
        if not REJECTED_STATUS.fullmatch(line(3)):
            problems.append((3, "line 3 must be 'Status: rejected — <reason>' in rejected/"))
    else:
        expected = "Status: implemented" if lifecycle == "archived" else f"Status: {lifecycle}"
        if line(3) != expected:
            problems.append((3, f"line 3 must be '{expected}' in {lifecycle}/"))
    if lifecycle == "archived":
        match = ARCHIVED_LINE.fullmatch(line(4))
        if not match or not is_date(match.group(1)):
            problems.append((4, "line 4 must be 'Archived: YYYY-MM-DD' in archived/"))
    return problems


def check_sections(lines: list[str], lifecycle: str) -> list[tuple[int | None, str]]:
    headings = []
    for number, line in outside_fences(lines):
        match = HEADING.fullmatch(line.rstrip())
        if match:
            headings.append((number, match.group(1)))

    problems = []
    if not headings or headings[0][1] != "Problem":
        problems.append((headings[0][0] if headings else None, "the first section must be '## Problem'"))
    present = {title for _, title in headings}
    has_marker = any(ALTERNATIVES_MARKER in line for _, line in outside_fences(lines))
    for title in REQUIRED[lifecycle]:
        if title not in present and not (title == "Alternatives considered" and has_marker):
            problems.append((None, f"missing required section '## {title}'"))
    for number, title in headings:
        if title in DISALLOWED.get(lifecycle, ()):
            problems.append((number, f"'## {title}' is not allowed in {lifecycle}/"))
    return problems


def check_links(path: Path, lines: list[str]) -> list[tuple[int, str]]:
    problems = []
    for number, line in outside_fences(lines):
        for target in LINK.findall(INLINE_CODE.sub("", line)):
            if target.startswith("#") or SCHEME.match(target):
                continue
            if target.startswith("/"):
                problems.append((number, f"link '{target}' must be relative"))
                continue
            file_part = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not (path.parent / file_part).exists():
                problems.append((number, f"broken link '{target}'"))
    return problems


def changed_archived_notes(notes_dir: Path, base: str) -> list[tuple[str, str]]:
    """Return (git status, repository path) for archived files that existed at base and differ now."""
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", "-C", str(notes_dir),
         "diff", "--name-status", "--no-renames", base, "--", "archived"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    changed = []
    for line in result.stdout.splitlines():
        status, _, path = line.partition("\t")
        if not status.startswith("A"):
            changed.append((status, path))
    return changed


def code_citations(notes_dir: Path) -> list[tuple[str, int, str]]:
    """Return (repository path, line number, note ID) for each citation outside the notes directory.

    Searches the files git tracks or does not ignore, so build output and
    dependencies stay out. Returns nothing when notes_dir is not in a git repository.
    """
    located = subprocess.run(
        ["git", "-C", str(notes_dir), "rev-parse", "--show-toplevel", "--show-prefix"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if located.returncode != 0:
        return []
    root, prefix = (located.stdout.splitlines() + [""])[:2]
    pathspec = ["--", ".", f":(exclude){prefix.rstrip('/')}"] if prefix else ["--", "."]
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", "-C", root, "grep", "--untracked", "-I", "-n", "-z",
         "-E", "-e", CITATION_LINE, *pathspec],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode > 1:
        raise RuntimeError(result.stderr.strip())
    citations = []
    for line in result.stdout.splitlines():
        path, number, text = line.split("\0", 2)
        citations += [(path, int(number), match.group(1)) for match in CITATION.finditer(text)]
    return citations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a decision-notes directory.")
    parser.add_argument("notes_dir", type=Path, help="the decision-notes directory, such as .agents/notes")
    parser.add_argument("--base", help="git ref whose archived notes must still be unchanged, usually the merge base")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(errors="backslashreplace")
    if not args.notes_dir.is_dir():
        print(f"error: {args.notes_dir} is not a directory", file=sys.stderr)
        return 2

    notes, problems = collect_notes(args.notes_dir)
    for path, lifecycle in notes:
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except UnicodeDecodeError:
            problems.append((path, None, "not valid UTF-8"))
            continue
        found = check_header(lines, lifecycle)
        if lifecycle != "archived":
            found += check_sections(lines, lifecycle) + check_links(path, lines)
        problems += [(path, line, message) for line, message in found]

    lifecycle_of = {path.stem: lifecycle for path, lifecycle in notes}
    try:
        citations = code_citations(args.notes_dir)
    except RuntimeError as error:
        print(f"error: git grep for citations failed: {error}", file=sys.stderr)
        return 2
    for path, line, note_id in citations:
        lifecycle = lifecycle_of.get(note_id)
        if lifecycle is None:
            problems.append((Path(path), line, f"cites decision note '{note_id}', which does not exist"))
        elif lifecycle == "archived":
            problems.append((Path(path), line, f"cites archived decision note '{note_id}'; "
                             "cite the note that owns the decision now, or remove the citation"))

    if args.base:
        try:
            changed = changed_archived_notes(args.notes_dir, args.base)
        except RuntimeError as error:
            print(f"error: git diff against {args.base} failed: {error}", file=sys.stderr)
            return 2
        for status, path in changed:
            action = "removed" if status.startswith("D") else "changed"
            problems.append((Path(path), None, f"archived note {action} since {args.base}; archived notes are frozen"))

    for path, line, message in problems:
        location = path.as_posix() if line is None else f"{path.as_posix()}:{line}"
        print(f"{location}: {message}")
    print(f"{len(notes)} notes and {len(citations)} citations in code checked, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
