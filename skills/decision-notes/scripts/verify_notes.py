#!/usr/bin/env python3
"""Check a decision-notes directory against the decision-notes format.

Usage: verify_notes.py NOTES_DIR [--base REF]

Checks the lifecycle/class/filename layout, each note's header and its agreement
with the lifecycle folder, the header lines only note_lifecycle.py writes and the
symmetry of supersession links, and the required sections. Archived notes get only
the header checks: their bodies predate later rules. In proposals, the only notes
anyone edits, it also checks relative links and "Decision note: <ID>" references,
and rejects a path link to another note, since a path breaks when a note moves.
Inside a git repository, it checks every "Decision note: <ID>" citation in the files
outside the notes directory that git tracks or does not ignore: the ID must name a
note. With --base, it reports every frozen note (accepted, rejected, archived) that
existed at REF and was changed, moved, or deleted since, apart from the edits
note_lifecycle.py makes. Exit status: 0 clean, 1 problems found, 2 usage or git error.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote

LIFECYCLES = ("proposed", "accepted", "rejected", "archived")
FROZEN = ("accepted", "rejected", "archived")
CLASSES = ("feature", "bug-fix", "simplification", "architecture", "process", "testing")
GUIDE_FILES = ("AGENTS.md", "CLAUDE.md")
SECTIONS = ("Problem", "Proposal", "Alternatives considered", "Acceptance criteria", "Risks")
REQUIRED = {"proposed": SECTIONS, "accepted": SECTIONS, "rejected": SECTIONS[:3]}
ALTERNATIVES_MARKER = "<!-- decision-notes: alternatives-not-recorded -->"

ID = r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*"
FILENAME = re.compile(r"(\d{4}-\d{2}-\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.md")
REJECTED_STATUS = re.compile(r"Status: rejected — \S.*")
ARCHIVED_LINE = re.compile(r"Archived: (\d{4}-\d{2}-\d{2})")
SUPERSESSION = re.compile(rf"(Supersedes|Supersedes in part|Superseded by|Superseded in part by): ({ID})(?: — (\S.*))?")
FENCE = re.compile(r" {0,3}(`{3,}|~{3,})")
HEADING = re.compile(r"## +(.+?)(?: +#+)? *")
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?")
INLINE_CODE = re.compile(r"`+[^`]*`+")
SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
CITATION = re.compile(rf"Decision note: ({ID})")
CITATION_LINE = r"Decision note: [0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]"  # git grep's ERE prefilter for CITATION

Problem = tuple[Path, "int | None", str]  # (path, line number or None, message)
Link = tuple[Path, int, str, str, "str | None"]  # (path, line number, kind, other ID, part)


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


def header_end(lines: list[str]) -> int:
    """Return the index just after the header lines that follow the status line."""
    end = 3
    while end < len(lines) and lines[end].strip():
        end += 1
    return end


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
            if class_dir.name.startswith(".") or (class_dir.is_file() and class_dir.name in GUIDE_FILES):
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


def check_header(path: Path, lines: list[str], lifecycle: str) -> tuple[list[tuple[int, str]], list[Link]]:
    """Return the header problems and the supersession links the header declares."""
    def line(number: int) -> str:
        return lines[number - 1].rstrip() if len(lines) >= number else ""

    problems, links = [], []
    if not line(1).startswith("# ") or not line(1)[2:].strip():
        problems.append((1, "line 1 must be '# <title>'"))
    if line(2):
        problems.append((2, "line 2 must be blank"))
    status = line(3)
    if lifecycle == "rejected" and not REJECTED_STATUS.fullmatch(status):
        problems.append((3, "line 3 must be 'Status: rejected — <reason>' in rejected/"))
    elif lifecycle in ("proposed", "accepted") and status != f"Status: {lifecycle}":
        problems.append((3, f"line 3 must be 'Status: {lifecycle}' in {lifecycle}/"))
    elif lifecycle == "archived" and status != "Status: accepted" and not REJECTED_STATUS.fullmatch(status):
        problems.append((3, "line 3 must be 'Status: accepted' or 'Status: rejected — <reason>' in archived/"))

    first = 4
    if lifecycle == "archived":
        match = ARCHIVED_LINE.fullmatch(line(4))
        if not match or not is_date(match.group(1)):
            problems.append((4, "line 4 must be 'Archived: YYYY-MM-DD' in archived/"))
        first = 5
    for number in range(first, header_end(lines) + 1):
        text = line(number)
        match = SUPERSESSION.fullmatch(text)
        if not match or ("in part" in match.group(1)) != (match.group(3) is not None):
            problems.append((number, f"'{text}' is not a header line; only note_lifecycle.py writes header lines"))
        elif lifecycle not in ("accepted", "archived"):
            problems.append((number, f"supersession lines belong to accepted and archived notes, not {lifecycle}/"))
        else:
            links.append((path, number, match.group(1), match.group(2), match.group(3)))
    return problems, links


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
    return problems


def check_references(path: Path, lines: list[str], notes_dir: Path, ids: set[str]) -> list[tuple[int, str]]:
    """Check the relative links and the note references of a proposal."""
    problems = []
    notes_root = notes_dir.resolve()
    for number, line in outside_fences(lines):
        for note_id in CITATION.findall(line):
            if note_id not in ids:
                problems.append((number, f"cites decision note '{note_id}', which does not exist"))
        for target in LINK.findall(INLINE_CODE.sub("", line)):
            if target.startswith("#") or SCHEME.match(target):
                continue
            if target.startswith("/"):
                problems.append((number, f"link '{target}' must be relative"))
                continue
            file_part = Path(unquote(target.split("#", 1)[0].split("?", 1)[0]))
            resolved = (path.parent / file_part).resolve()
            if FILENAME.fullmatch(file_part.name) and notes_root in resolved.parents:
                problems.append((number, f"link '{target}' points at a note by path; refer to another note by its ID, "
                                         f"as 'Decision note: {file_part.stem}', since a path breaks when the note moves"))
            elif not resolved.exists():
                problems.append((number, f"broken link '{target}'"))
    return problems


def check_supersession(links: list[Link], ids: set[str]) -> list[Problem]:
    """Every supersession link has its counterpart in the other note."""
    declared = {(path.stem, kind, other, part) for path, _, kind, other, part in links}
    counterpart = {"Supersedes": "Superseded by", "Supersedes in part": "Superseded in part by",
                   "Superseded by": "Supersedes", "Superseded in part by": "Supersedes in part"}
    problems = []
    for path, number, kind, other, part in links:
        if other not in ids:
            problems.append((path, number, f"names decision note '{other}', which does not exist"))
        elif (other, counterpart[kind], path.stem, part) not in declared:
            expected = f"{counterpart[kind]}: {path.stem}" + (f" — {part}" if part else "")
            problems.append((path, number, f"{other} has no '{expected}'; link notes with note_lifecycle.py supersede"))
    return problems


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


def lifecycle_edit_only(before: str, after: str, base_lifecycle: str, lifecycle: str) -> bool:
    """Whether after differs from before only by header lines note_lifecycle.py adds."""
    old = before.replace("\r\n", "\n").lstrip("﻿").splitlines()
    new = after.replace("\r\n", "\n").lstrip("﻿").splitlines()
    if old[:3] != new[:3] or old[header_end(old):] != new[header_end(new):]:
        return False
    old_header, new_header = old[3:header_end(old)], new[3:header_end(new)]
    added = list(new_header)
    for line in old_header:
        if line not in added:
            return False
        added.remove(line)
    for line in added:
        archiving = lifecycle == "archived" and base_lifecycle != "archived"
        if not (ARCHIVED_LINE.fullmatch(line) and archiving) and not (SUPERSESSION.fullmatch(line) and base_lifecycle == "accepted"):
            return False
    return True


def frozen_changes(notes_dir: Path, base: str, current: dict[str, tuple[Path, str]]) -> list[Problem]:
    """Report frozen notes at base that changed since, other than by note_lifecycle.py."""
    def git(*args: str) -> str:
        result = subprocess.run(["git", "-c", "core.quotepath=false", "-C", str(notes_dir), *args],
                                capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
        return result.stdout

    problems = []
    listing = git("diff", "--name-status", "--no-renames", "--relative", base, "--", *FROZEN)
    for entry in listing.splitlines():
        status, _, relative = entry.partition("\t")
        parts = Path(relative).parts
        if status.startswith("A") or len(parts) != 3 or not FILENAME.fullmatch(parts[2]):
            continue
        base_lifecycle, note_id = parts[0], Path(parts[2]).stem
        where = notes_dir / relative
        if note_id not in current:
            problems.append((where, None, f"frozen note deleted since {base}; frozen notes are never deleted"))
            continue
        path, lifecycle = current[note_id]
        if lifecycle != base_lifecycle and not (lifecycle == "archived" and base_lifecycle in ("accepted", "rejected")):
            problems.append((where, None, f"frozen note moved from {base_lifecycle}/ to {lifecycle}/ since {base}"))
            continue
        before = git("show", f"{base}:./{relative}")
        if not lifecycle_edit_only(before, path.read_text(encoding="utf-8"), base_lifecycle, lifecycle):
            problems.append((path if lifecycle != base_lifecycle else where, None,
                             f"frozen note changed since {base}; only note_lifecycle.py changes frozen notes"))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a decision-notes directory.")
    parser.add_argument("notes_dir", type=Path, help="the decision-notes directory, such as .agents/notes")
    parser.add_argument("--base", help="git ref whose frozen notes must still be unchanged, usually the merge base")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(errors="backslashreplace")
    if not args.notes_dir.is_dir():
        print(f"error: {args.notes_dir} is not a directory", file=sys.stderr)
        return 2

    notes, problems = collect_notes(args.notes_dir)
    ids = {path.stem for path, _ in notes}
    links: list[Link] = []
    for path, lifecycle in notes:
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except UnicodeDecodeError:
            problems.append((path, None, "not valid UTF-8"))
            continue
        found, declared = check_header(path, lines, lifecycle)
        links += declared
        if lifecycle != "archived":
            found += check_sections(lines, lifecycle)
        if lifecycle == "proposed":
            found += check_references(path, lines, args.notes_dir, ids)
        problems += [(path, line, message) for line, message in found]
    problems += check_supersession(links, ids)

    try:
        citations = code_citations(args.notes_dir)
    except RuntimeError as error:
        print(f"error: git grep for citations failed: {error}", file=sys.stderr)
        return 2
    for path, line, note_id in citations:
        if note_id not in ids:
            problems.append((Path(path), line, f"cites decision note '{note_id}', which does not exist"))

    if args.base:
        try:
            problems += frozen_changes(args.notes_dir, args.base, {path.stem: (path, lifecycle) for path, lifecycle in notes})
        except RuntimeError as error:
            print(f"error: git against {args.base} failed: {error}", file=sys.stderr)
            return 2

    for path, line, message in problems:
        location = path.as_posix() if line is None else f"{path.as_posix()}:{line}"
        print(f"{location}: {message}")
    print(f"{len(notes)} notes and {len(citations)} citations in code checked, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
