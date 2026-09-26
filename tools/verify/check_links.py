#!/usr/bin/env python3
"""Check local Markdown links and GitHub-style #L123 source references.

External URLs and non-line fragments (such as section anchors) are outside
this check. This verifies a cited location, not the claim made about it.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


INLINE_LINK = re.compile(r"!?\[[^\]\n]+\]\((?P<target><[^>\n]+>|[^)\n]+)\)")
REFERENCE_LINK = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(?P<target><[^>]+>|\S+)")
LINE_FRAGMENT = re.compile(r"^L(?P<first>\d+)(?:-L(?P<last>\d+))?$")


def markdown_files(repo: Path) -> list[Path]:
    files = set(repo.glob("*.md"))
    for folder in ("docs", ".agents/skills", ".claude/skills"):
        directory = repo / folder
        if directory.is_dir():
            files.update(directory.rglob("*.md"))
    return sorted(file for file in files if file.is_file())


def destinations(line: str) -> list[str]:
    targets = [match.group("target") for match in INLINE_LINK.finditer(line)]
    definition = REFERENCE_LINK.match(line)
    if definition:
        targets.append(definition.group("target"))
    return targets


def target_url(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<"):
        return raw[1 : raw.index(">")]
    return raw.split(maxsplit=1)[0] if raw else ""


def check_target(repo: Path, source: Path, raw: str, line_number: int) -> str | None:
    url = html.unescape(target_url(raw))
    if not url or url.startswith(("/", "//")):
        return None
    try:
        parts = urlsplit(url)
    except ValueError as exc:
        return f"invalid link {url!r}: {exc}"
    if parts.scheme or parts.netloc:
        return None
    path = unquote(parts.path)
    resolved = (source.parent / path).resolve() if path else source.resolve()
    try:
        resolved.relative_to(repo)
    except ValueError:
        return f"local link escapes repository: {url}"
    if not resolved.exists():
        return f"missing local link: {url}"

    fragment = unquote(parts.fragment)
    if fragment.startswith("L") and fragment[1:2].isdigit():
        match = LINE_FRAGMENT.fullmatch(fragment)
        if not match:
            return f"malformed line fragment: {url}"
        if not resolved.is_file():
            return f"line fragment targets a directory: {url}"
        first = int(match.group("first"))
        last = int(match.group("last") or first)
        try:
            length = len(resolved.read_text(encoding="utf-8").splitlines())
        except (OSError, UnicodeError) as exc:
            return f"cannot read line target {url}: {exc}"
        if first < 1 or last < first or last > length:
            return f"line fragment outside 1..{length}: {url}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).resolve().parents[2],
        help="repository root (default: root containing this script)",
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    documents = markdown_files(repo)
    if not documents:
        print(f"FAIL: no Markdown documents found under {repo}")
        return 1

    errors: list[str] = []
    checked = 0
    for source in documents:
        fence: str | None = None
        for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.lstrip()
            marker = re.match(r"^(`{3,}|~{3,})", stripped)
            if marker:
                if fence is None:
                    fence = marker.group(1)[0]
                elif marker.group(1)[0] == fence:
                    fence = None
                continue
            if fence is not None:
                continue
            for raw in destinations(line):
                checked += 1
                problem = check_target(repo, source, raw, line_number)
                if problem:
                    errors.append(f"{source.relative_to(repo).as_posix()}:{line_number}: {problem}")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: checked {checked} Markdown links in {len(documents)} documents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
