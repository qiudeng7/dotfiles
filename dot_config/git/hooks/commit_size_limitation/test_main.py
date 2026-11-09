"""在临时 Git 索引中验证普通文件、符号链接和 gitlink 的检查边界。"""

import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from commit_size_limitation import main as size_check
from functions import staged_paths, staged_submodule_paths
from no_junk_files import main as junk_check


class StagedSizeTests(unittest.TestCase):
    def setUp(self):
        self.previous_cwd = os.getcwd()
        self.directory = tempfile.TemporaryDirectory(prefix="git-hook-size-test-")
        os.chdir(self.directory.name)
        self.git("init", "--quiet")

    def tearDown(self):
        os.chdir(self.previous_cwd)
        self.directory.cleanup()

    def git(self, *args, data=None):
        return subprocess.run(
            ["git", *args], input=data, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=True,
        ).stdout.decode().strip()

    def add_blob(self, path, content, mode="100644"):
        oid = self.git("hash-object", "-w", "--stdin", data=content)
        self.git("update-index", "--add", "--cacheinfo", mode, oid, path)

    def add_gitlink(self, path):
        # 此对象不在主仓库，复现真实 submodule 的对象库边界。
        self.git("update-index", "--add", "--cacheinfo", "160000", "1" * 40, path)

    def test_normal_file_passes(self):
        self.add_blob("normal.txt", b"hello")
        self.assertEqual(size_check.main([]), 0)

    def test_oversized_file_still_rejected_with_gitlink(self):
        self.add_blob("large.bin", b"123456789")
        self.add_gitlink("drawing")
        with patch.object(size_check, "MAX_STAGED_FILE_BYTES", 8):
            self.assertEqual(
                size_check.oversized_staged_file_sizes(staged_paths()),
                [("large.bin", 9)],
            )
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(size_check.main([]), 1)

    def test_gitlink_skipped_even_with_special_path(self):
        path = "skills/drawing name\t中文"
        self.add_gitlink(path)
        self.assertIn(path, staged_paths())
        self.assertEqual(staged_submodule_paths(), {path})
        self.assertEqual(size_check.main([]), 0)

    def test_symlink_is_still_checked(self):
        self.add_blob("link", b"long-target", mode="120000")
        with patch.object(size_check, "MAX_STAGED_FILE_BYTES", 8):
            self.assertEqual(
                size_check.oversized_staged_file_sizes(staged_paths()),
                [("link", 11)],
            )

    def test_gitlink_path_still_checked_for_junk(self):
        self.add_gitlink("__MACOSX/drawing")
        self.assertEqual(size_check.main([]), 0)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(junk_check.main([]), 1)


if __name__ == "__main__":
    unittest.main()
