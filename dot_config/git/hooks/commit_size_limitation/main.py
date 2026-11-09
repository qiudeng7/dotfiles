"""提交规模业务规则。"""

from pathlib import Path
import sys
from typing import List, Tuple


HOOKS_DIR = Path(__file__).resolve().parent.parent
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

from functions import (
    staged_file_size,
    staged_paths,
    staged_submodule_paths,
)


MAX_STAGED_FILE_BYTES = 50 * 1024 * 1024


def oversized_staged_file_sizes(paths: List[str]) -> List[Tuple[str, int]]:
    """检查文件大小；gitlink 只引用子仓库提交，没有本仓库文件内容。"""
    violations = []
    submodules = staged_submodule_paths()
    for path in paths:
        if path in submodules:
            continue
        size = staged_file_size(path)
        if size > MAX_STAGED_FILE_BYTES:
            violations.append((path, size))
    return violations


def format_size(size: int) -> str:
    return f"{size / 1024 / 1024:.1f} MiB"


def main(args: List[str]) -> int:
    if args:
        print("用法：commit_size_limitation/main.py", file=sys.stderr)
        return 2

    oversized_files_by_size = oversized_staged_file_sizes(staged_paths())
    if oversized_files_by_size:
        print(f"检测到超过 {format_size(MAX_STAGED_FILE_BYTES)} 的暂存文件：", file=sys.stderr)
        for path, size in oversized_files_by_size:
            print(f"  {path} ({format_size(size)})", file=sys.stderr)
        print("\n请压缩资源、使用外部存储，或在确有必要时使用 git commit --no-verify。", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
