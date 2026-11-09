"""仓库整洁度业务规则：阻止常见垃圾文件进入提交。"""

from pathlib import Path, PurePosixPath
import sys
from typing import List, Optional


HOOKS_DIR = Path(__file__).resolve().parent.parent
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

from functions import staged_paths


JUNK_FILE_NAMES = {
    ".ds_store": "macOS Finder metadata",
    "desktop.ini": "Windows Explorer metadata",
    "ehthumbs.db": "Windows thumbnail cache",
    "thumbs.db": "Windows thumbnail cache",
}

JUNK_DIRECTORY_NAMES = {
    "$recycle.bin": "Windows recycle bin",
    "__macosx": "macOS archive metadata",
}

JUNK_SUFFIXES = {
    ".orig": "merge or patch backup",
    ".rej": "rejected patch",
    ".swn": "Vim swap file",
    ".swo": "Vim swap file",
    ".swp": "Vim swap file",
}


def junk_reason(path: str) -> Optional[str]:
    """返回垃圾文件类型；普通文件返回 None。"""
    parts = PurePosixPath(path).parts
    if not parts:
        return None

    for part in parts[:-1]:
        reason = JUNK_DIRECTORY_NAMES.get(part.casefold())
        if reason:
            return reason

    name = parts[-1]
    folded_name = name.casefold()

    if folded_name in JUNK_FILE_NAMES:
        return JUNK_FILE_NAMES[folded_name]
    if name.startswith("._"):
        return "macOS AppleDouble metadata"
    if name.startswith(".#") or (name.startswith("#") and name.endswith("#")):
        return "Emacs temporary file"
    if name.endswith("~"):
        return "editor backup file"

    for suffix, reason in JUNK_SUFFIXES.items():
        if folded_name.endswith(suffix):
            return reason

    return None


def main(args: List[str]) -> int:
    if args:
        print("用法：no_junk_files/main.py", file=sys.stderr)
        return 2

    violations = [
        (path, reason)
        for path in staged_paths()
        if (reason := junk_reason(path)) is not None
    ]
    if not violations:
        return 0

    print("检测到不应提交的垃圾文件：", file=sys.stderr)
    for path, reason in violations:
        print(f"  {path} ({reason})", file=sys.stderr)
    print("\n请从暂存区移除这些文件，并按需清理工作区后重新提交。", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
