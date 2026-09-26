#!/usr/bin/env python3
"""Compare the documented Java and verification-tool trees with the checkout.

The baseline inventory prose in code-tree.md is historical. Only the fenced
physical tree under each document's tree heading represents the current files.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TREE_ROW = re.compile(r"^(?P<indent>(?:│  |   )*)(?:├─ |└─ )(?P<entry>\S+)")
CURRENT_COUNT = re.compile(r"현재 Java 소스는\s*\*\*(\d+)개\*\*")
DOCUMENTS = (
    ("README.md", "## 코드 트리"),
    ("docs/research/code-tree.md", "## 물리적 파일 트리"),
)


def physical_tree(document: Path, heading: str) -> str:
    lines = document.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index(heading) + 1
    except ValueError as exc:
        raise ValueError(f"missing heading {heading!r}") from exc

    for index in range(start, len(lines)):
        line = lines[index].strip()
        if line.startswith("## "):
            break
        if line == "```text":
            for end in range(index + 1, len(lines)):
                if lines[end].strip() == "```":
                    return "\n".join(lines[index + 1 : end])
            break
    raise ValueError(f"missing closed text tree under {heading!r}")


def java_paths_in_tree(tree: str) -> set[str]:
    directories: dict[int, str] = {-1: ""}
    java_paths: set[str] = set()
    for line in tree.splitlines():
        match = TREE_ROW.match(line)
        if not match:
            continue
        depth = len(match.group("indent")) // 3
        entry = match.group("entry")
        if depth - 1 not in directories:
            raise ValueError(f"tree row has no parent: {line}")
        path = "/".join(part for part in (directories[depth - 1], entry) if part)
        for old_depth in [level for level in directories if level >= depth]:
            del directories[old_depth]
        if entry.endswith("/"):
            directories[depth] = path.rstrip("/")
        elif entry.endswith(".java"):
            if path in java_paths:
                raise ValueError(f"duplicate Java path: {path}")
            java_paths.add(path)
    if not java_paths:
        raise ValueError("physical tree contains no Java files")
    return java_paths


def tool_paths_in_tree(tree: str) -> set[str]:
    """Read the separate tool inventory without treating prose as file entries."""
    directories: dict[int, str] = {-1: "tools"}
    files: set[str] = set()
    for line in tree.splitlines():
        match = TREE_ROW.match(line)
        if not match:
            continue
        depth = len(match.group("indent")) // 3
        entry = match.group("entry")
        if depth - 1 not in directories:
            raise ValueError(f"tool tree row has no parent: {line}")
        path = "/".join((directories[depth - 1], entry)).rstrip("/")
        for old_depth in [level for level in directories if level >= depth]:
            del directories[old_depth]
        if entry.endswith("/"):
            directories[depth] = path
        elif path in files:
            raise ValueError(f"duplicate tool path: {path}")
        else:
            files.add(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).resolve().parents[2],
        help="repository root (default: root containing this script)",
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    source = repo / "src"
    if not source.is_dir():
        print(f"FAIL: source directory missing: {source}")
        return 1
    actual = {file.relative_to(repo).as_posix() for file in source.rglob("*.java") if file.is_file()}
    if not actual:
        print("FAIL: no Java source files found under src/")
        return 1

    errors: list[str] = []
    for relative_document, heading in DOCUMENTS:
        document = repo / relative_document
        if not document.is_file():
            errors.append(f"{relative_document}: document missing")
            continue
        try:
            documented = java_paths_in_tree(physical_tree(document, heading))
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"{relative_document}: {exc}")
            continue
        for missing in sorted(actual - documented):
            errors.append(f"{relative_document}: undocumented Java file: {missing}")
        for stale in sorted(documented - actual):
            errors.append(f"{relative_document}: Java tree entry has no source: {stale}")

        if relative_document == "README.md":
            count = CURRENT_COUNT.search(document.read_text(encoding="utf-8"))
            if not count:
                errors.append("README.md: current Java count is missing")
            elif int(count.group(1)) != len(actual):
                errors.append(
                    f"README.md: current Java count is {count.group(1)}, "
                    f"but src/ contains {len(actual)}"
                )

    tool_document = repo / "docs/research/verification-tools.md"
    tool_count: int | None = None
    if tool_document.is_file():
        try:
            tool_text = tool_document.read_text(encoding="utf-8")
            tool_block = re.search(r"```text\s*\n(.*?)\n```", tool_text, flags=re.DOTALL)
            if not tool_block or not tool_block.group(1).startswith("tools/\n"):
                raise ValueError("missing fenced tool inventory")
            documented_tools = tool_paths_in_tree(tool_block.group(1))
            actual_tools = {
                file.relative_to(repo).as_posix()
                for file in (repo / "tools").rglob("*")
                if file.is_file() and "__pycache__" not in file.parts and file.suffix != ".pyc"
            }
            for missing in sorted(actual_tools - documented_tools):
                errors.append(f"verification-tools.md: undocumented tool file: {missing}")
            for stale in sorted(documented_tools - actual_tools):
                errors.append(f"verification-tools.md: tool tree entry has no file: {stale}")
            tool_count = len(actual_tools)
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"verification-tools.md: {exc}")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: README and research code tree list all {len(actual)} Java files")
    if tool_count is not None:
        print(f"PASS: verification tool tree lists all {tool_count} tool files")
    else:
        print("SKIP: verification tool tree (not in this checkout)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
