"""Tests for strip_attribution.py and its hooks. Run: python -m unittest discover -s skills/setup-agent-workflow/scripts"""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).parent
SCRIPT = SCRIPTS / "strip_attribution.py"

MESSAGE = """\
feat(api): add the Claude API client

Add the Claude API client and retry on 529.
Claude: the client now backs off exponentially.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Refs #12
Co-authored-by: Alice <alice@example.com>
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_123
"""

CLEANED = """\
feat(api): add the Claude API client

Add the Claude API client and retry on 529.
Claude: the client now backs off exponentially.

Refs #12
Co-authored-by: Alice <alice@example.com>
"""


class Repo:
    """A temporary repository with the hooks installed and a bare remote."""

    def __init__(self, root: Path):
        self.root = root / "work"
        remote = root / "remote.git"
        subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
        self.root.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "commit.gpgsign", "false")
        self.git("remote", "add", "origin", str(remote))
        (self.root / "scripts").mkdir()
        (self.root / "scripts" / "strip_attribution.py").write_bytes(SCRIPT.read_bytes())
        hooks = self.root / ".githooks"
        hooks.mkdir()
        for template, hook in (("commit-msg-attribution", "commit-msg"), ("pre-push-attribution", "pre-push")):
            (hooks / hook).write_bytes((SCRIPTS / template).read_bytes())
            (hooks / hook).chmod(0o755)
        self.git("config", "core.hooksPath", ".githooks")

    def git(self, *args, check=True):
        return subprocess.run(["git", "-C", str(self.root), *args], check=check, capture_output=True,
                              text=True, encoding="utf-8")

    def commit(self, name, message, *extra):
        (self.root / name).write_text(name, encoding="utf-8")
        self.git("add", name)
        subprocess.run(["git", "-C", str(self.root), "commit", "-q", "-F", "-", *extra],
                       input=message, capture_output=True, text=True, encoding="utf-8", check=True)

    def message(self, rev="HEAD"):
        return self.git("log", "-1", "--format=%B", rev).stdout


class StripAttributionTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name)

    def run_on(self, message, cwd=None):
        path = self.tmp / "COMMIT_EDITMSG"
        path.write_text(message, encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), str(path)], cwd=cwd or self.tmp,
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        return path.read_text(encoding="utf-8"), result.stderr

    def test_removes_attribution_and_keeps_everything_else(self):
        cleaned, report = self.run_on(MESSAGE)
        self.assertEqual(cleaned, CLEANED)
        self.assertIn("removed AI attribution: Co-Authored-By: Claude Opus 5.5", report)

    def test_recognizes_other_agents_and_keeps_human_trailers(self):
        message = ("fix: handle empty input\n\n"
                   "Reviewed-by: Bob <bob@example.com>\n"
                   "Co-authored-by: Codex <codex@openai.com>\n"
                   "Co-authored-by: Cursor Agent <cursoragent@cursor.com>\n"
                   "Co-authored-by: Copilot <198982749+Copilot@users.noreply.github.com>\n"
                   "Signed-off-by: aider (gpt-4o) <noreply@aider.chat>\n")
        cleaned, _ = self.run_on(message)
        self.assertEqual(cleaned, "fix: handle empty input\n\nReviewed-by: Bob <bob@example.com>\n")

    def test_project_identities_come_from_the_config(self):
        repo = Repo(self.tmp)
        (repo.root / ".attribution.json").write_text(json.dumps({"identities": ["my-agent"]}), encoding="utf-8")
        cleaned, _ = self.run_on("fix: x\n\nCo-authored-by: My-Agent <bot@example.com>\n", cwd=repo.root)
        self.assertEqual(cleaned, "fix: x\n")

    def test_hooks_clean_commits_and_block_pushes_until_fixed(self):
        repo = Repo(self.tmp)
        repo.commit("a.txt", MESSAGE)
        self.assertEqual(repo.message().rstrip("\n"), CLEANED.rstrip("\n"))
        self.assertEqual(repo.git("push", "-q", "-u", "origin", "main", check=False).returncode, 0)

        repo.commit("b.txt", "fix: b\n\nCo-Authored-By: Claude <noreply@anthropic.com>\n", "--no-verify")
        rejected = repo.git("push", "-q", "origin", "main", check=False)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("Attribution lines in", rejected.stderr)

        command, base = re.search(r'git rebase --exec "(.+?)" (\S+)', rejected.stderr).groups()
        repo.git("rebase", "-q", "--exec", command, base)
        self.assertNotIn("anthropic.com", repo.message())
        self.assertEqual(repo.git("push", "-q", "origin", "main", check=False).returncode, 0)

    def test_pre_push_rejects_an_ai_author_on_a_new_branch(self):
        repo = Repo(self.tmp)
        repo.commit("a.txt", "chore: init\n")
        repo.git("push", "-q", "-u", "origin", "main")
        repo.git("switch", "-q", "-c", "feature")
        repo.commit("b.txt", "feat: b\n", "--author=Claude <noreply@anthropic.com>")
        rejected = repo.git("push", "-q", "origin", "feature", check=False)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("AI author or committer in", rejected.stderr)


if __name__ == "__main__":
    unittest.main()
