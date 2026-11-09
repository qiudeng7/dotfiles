"""暂存区读取辅助函数。"""

import subprocess
import sys
from typing import List, Set, Tuple


def run_git(args: List[str]) -> bytes:
    """执行 Git 命令并返回 stdout bytes。"""
    result = subprocess.run(
        ["git", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        error = result.stderr.decode("utf-8", errors="replace").strip()
        print(error or f"Git 命令执行失败：git {' '.join(args)}", file=sys.stderr)
        raise SystemExit(result.returncode)

    return result.stdout


def staged_paths() -> List[str]:
    """返回本次提交新增、复制、修改、重命名或变更类型的路径。"""
    output = run_git(
        [
            "diff",
            "--cached",
            "--name-only",
            "--diff-filter=ACMRT",
            "-z",
        ]
    )
    return [
        path.decode("utf-8", errors="surrogateescape")
        for path in output.split(b"\0")
        if path
    ]


def staged_submodule_paths() -> Set[str]:
    """返回索引中 stage 0 的 gitlink 路径，不读取子仓库对象。"""
    paths = set()
    for entry in run_git(["ls-files", "--stage", "-z"]).split(b"\0"):
        if not entry:
            continue
        metadata, path = entry.split(b"\t", 1)
        mode, _object_id, stage = metadata.split()
        if mode == b"160000" and stage == b"0":
            paths.add(path.decode("utf-8", errors="surrogateescape"))
    return paths


def staged_file_line_count(path: str) -> int:
    """返回暂存区中文本文件内容的行数。"""
    content = run_git(["show", f":{path}"])
    if not content:
        return 0

    line_count = content.count(b"\n")
    if not content.endswith(b"\n"):
        line_count += 1
    return line_count


def staged_file_size(path: str) -> int:
    """返回暂存区中文件内容的字节数。"""
    return len(run_git(["show", f":{path}"]))


def staged_numstat() -> List[Tuple[str, str, str]]:
    """返回暂存区 numstat 字段：(新增行, 删除行, 路径)。"""
    output = run_git(["diff", "--cached", "--numstat", "--diff-filter=ACMRT", "-z"])
    if not output:
        return []

    fields = [field for field in output.split(b"\0") if field]
    rows = []
    for field in fields:
        columns = field.split(b"\t")
        if len(columns) < 3:
            continue
        rows.append(
            (
                columns[0].decode("utf-8", errors="replace"),
                columns[1].decode("utf-8", errors="replace"),
                columns[2].decode("utf-8", errors="surrogateescape"),
            )
        )
    return rows


def staged_text_paths() -> List[str]:
    """返回暂存区中的文本文件路径。"""
    return [path for added, deleted, path in staged_numstat() if added != "-" and deleted != "-"]


def staged_binary_paths() -> List[str]:
    """返回暂存区中的二进制文件路径。"""
    return [path for added, deleted, path in staged_numstat() if added == "-" and deleted == "-"]


def staged_change_line_count() -> int:
    """返回本次提交的新增行与删除行总数；二进制文件不计入。"""
    total = 0
    for added, deleted, _path in staged_numstat():
        if added == "-" or deleted == "-":
            continue
        total += int(added) + int(deleted)
    return total
