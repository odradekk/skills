"""Tests for check_file_size.py. Run: python -m unittest discover -s skills/setup-agent-workflow/scripts"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("check_file_size.py")
OVER = "x" * 20_004   # 5,001 tokens
UNDER = "x" * 20_000  # 5,000 tokens: exactly the limit


class CheckFileSizeTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.git("init", "-q")
        self.config({"max_tokens": 5000, "exclude": ["**/*.lock", "dist/**"], "exceptions": {}})

    def git(self, *args):
        subprocess.run(
            ["git", "-C", str(self.root), "-c", "user.name=test", "-c", "user.email=test@example.com",
             "-c", "commit.gpgsign=false", *args],
            check=True, capture_output=True,
        )

    def config(self, settings):
        (self.root / ".file-size.json").write_text(json.dumps(settings), encoding="utf-8")

    def write(self, relative, content, stage=True):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode() if isinstance(content, str) else content)
        if stage:
            self.git("add", relative)

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "commit")

    def run_check(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.root, capture_output=True, text=True)

    def assert_problem(self, result, fragment):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(fragment, result.stdout)

    def test_staged_file_over_limit_fails_with_split_instructions(self):
        self.write("src/big.ts", OVER)
        result = self.run_check()
        self.assert_problem(result, "src/big.ts: about 5,001 tokens")
        self.assertIn("How to split a file", result.stdout)

    def test_file_at_limit_passes(self):
        self.write("src/ok.ts", UNDER)
        self.assertEqual(self.run_check().returncode, 0)

    def test_checks_staged_content_and_only_staged_files(self):
        self.write("src/big.ts", OVER)
        (self.root / "src/big.ts").write_text("small", encoding="utf-8")  # working tree differs from the index
        self.write("src/untracked.ts", OVER, stage=False)
        result = self.run_check()
        self.assert_problem(result, "src/big.ts")
        self.assertNotIn("untracked.ts", result.stdout)

    def test_excluded_binary_and_excepted_files_are_skipped(self):
        self.config({"max_tokens": 5000, "exclude": ["**/*.lock", "dist/**"],
                     "exceptions": {"docs/spec.md": "one standard; splitting breaks its numbering"}})
        self.write("app/deep/yarn.lock", OVER)
        self.write("dist/bundle.js", OVER)
        self.write("art/image.png", b"\0" + OVER.encode())
        self.write("docs/spec.md", OVER)
        self.assertEqual(self.run_check().returncode, 0)

    def test_baselined_file_may_stay_but_not_grow(self):
        self.config({"max_tokens": 5000, "exclude": [], "exceptions": {}, "baseline": {"src/legacy.ts": 5001}})
        self.write("src/legacy.ts", OVER)
        self.assertEqual(self.run_check().returncode, 0)
        self.write("src/legacy.ts", OVER + "xxxx")
        self.assert_problem(self.run_check(), "more than its baseline of 5,001")

    def test_shrunk_baselined_file_asks_to_lower_the_baseline(self):
        self.config({"max_tokens": 5000, "exclude": [], "exceptions": {}, "baseline": {"src/legacy.ts": 6000}})
        self.write("src/legacy.ts", OVER)
        result = self.run_check()
        self.assert_problem(result, "less than its baseline of 6,000")
        self.assertNotIn("How to split a file", result.stdout)

    def test_write_baseline_creates_then_only_lowers_or_removes(self):
        self.write("src/a.ts", OVER + "x" * 400)  # 5,101 tokens
        self.write("src/b.ts", OVER)
        self.commit()
        self.assertEqual(self.run_check("--write-baseline").returncode, 0)
        baseline = json.loads((self.root / ".file-size.json").read_text(encoding="utf-8"))["baseline"]
        self.assertEqual(baseline, {"src/a.ts": 5101, "src/b.ts": 5001})

        self.write("src/a.ts", OVER)      # shrinks to 5,001
        self.write("src/b.ts", UNDER)     # drops under the limit
        self.write("src/c.ts", OVER)      # new and over the limit
        result = self.run_check("--write-baseline")
        baseline = json.loads((self.root / ".file-size.json").read_text(encoding="utf-8"))["baseline"]
        self.assertEqual(baseline, {"src/a.ts": 5001})
        self.assertIn("not added src/c.ts", result.stdout)

    def test_write_baseline_never_raises_an_entry(self):
        self.config({"max_tokens": 5000, "exclude": [], "exceptions": {}, "baseline": {"src/a.ts": 5001}})
        self.write("src/a.ts", OVER + "x" * 400)
        self.run_check("--write-baseline")
        baseline = json.loads((self.root / ".file-size.json").read_text(encoding="utf-8"))["baseline"]
        self.assertEqual(baseline, {"src/a.ts": 5001})

    def test_all_checks_committed_files(self):
        self.write("src/big.ts", OVER)
        self.commit()
        self.assertEqual(self.run_check().returncode, 0)  # nothing staged
        self.assert_problem(self.run_check("--all"), "src/big.ts")

    def test_pre_commit_hook_blocks_a_commit_over_the_limit(self):
        hooks = self.root / ".githooks"
        hooks.mkdir()
        (hooks / "pre-commit").write_bytes(SCRIPT.with_name("pre-commit-file-size").read_bytes())
        (hooks / "pre-commit").chmod(0o755)
        (self.root / "scripts").mkdir()
        (self.root / "scripts" / "check_file_size.py").write_bytes(SCRIPT.read_bytes())
        self.git("config", "core.hooksPath", ".githooks")
        self.commit()

        self.write("src/big.ts", OVER)
        blocked = subprocess.run(["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@example.com",
                                  "-c", "commit.gpgsign=false", "commit", "-q", "-m", "big"],
                                 capture_output=True, text=True)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("src/big.ts: about 5,001 tokens", blocked.stdout + blocked.stderr)

        self.write("src/big.ts", UNDER)
        self.commit()

    def test_invalid_configuration_exits_2(self):
        self.config({"max_tokens": "5000"})
        result = self.run_check()
        self.assertEqual(result.returncode, 2)
        self.assertIn("max_tokens must be a positive integer", result.stderr)


if __name__ == "__main__":
    unittest.main()
