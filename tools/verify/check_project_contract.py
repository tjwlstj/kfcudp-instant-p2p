#!/usr/bin/env python3
"""Check version declarations and repository skill discovery contracts.

This is a source/configuration check, not a Gradle or Minecraft runtime test.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path


CANONICAL_SKILL = Path(".agents/skills/instant-p2p-maintainer/SKILL.md")
CLAUDE_SKILL = Path(".claude/skills/instant-p2p-maintainer/SKILL.md")


def fail(message: str) -> None:
    print(f"FAIL {message}", file=sys.stderr)


def versions_in_settings(source: str) -> list[str]:
    groups = re.findall(r"\bversions\s*\(([^)]*)\)", source, flags=re.DOTALL)
    return [version for group in groups for version in re.findall(r'"([^"]+)"', group)]


def versions_in_ci(source: str) -> list[str]:
    match = re.search(r"\bminecraft\s*:\s*\[([^]]*)\]", source, flags=re.DOTALL)
    if match is None:
        raise ValueError("build workflow is missing the minecraft matrix")
    return re.findall(r'"([^"]+)"|\'([^\']+)\'', match.group(1))


def frontmatter(source: str) -> dict[str, str]:
    match = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", source, flags=re.DOTALL)
    if match is None:
        raise ValueError("skill has no YAML frontmatter")
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"\'')
    return result


def ignored(repo: Path, relative: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", "--no-index", "--", relative],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(f"git check-ignore failed for {relative}: {result.stderr.strip()}")
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--require-claude",
        action="store_true",
        help="Require the Claude skill pointer (use when checking PR #1)",
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    errors: list[str] = []

    try:
        settings = (repo / "settings.gradle.kts").read_text(encoding="utf-8")
        workflow = (repo / ".github/workflows/build.yml").read_text(encoding="utf-8")
        properties = tomllib.loads((repo / "stonecutter.properties.toml").read_text(encoding="utf-8"))
        declared = versions_in_settings(settings)
        ci_groups = versions_in_ci(workflow)
        ci = [left or right for left, right in ci_groups]
        property_versions = [key for key in properties if key != "mod"]
        if not declared or len(declared) != len(set(declared)):
            errors.append("settings.gradle.kts has no versions or has duplicates")
        if len(ci) != len(set(ci)):
            errors.append("CI minecraft matrix has duplicate versions")
        if declared != ci:
            errors.append(f"Stonecutter/CI version order differs: settings={declared}, CI={ci}")
        if set(declared) != set(property_versions):
            errors.append(
                f"Stonecutter/property version set differs: settings={declared}, properties={property_versions}"
            )
        for version in declared:
            values = properties.get(version, {})
            if "deps" not in values or "fabric_api" not in values["deps"]:
                errors.append(f"{version} has no deps.fabric_api")
            if version.startswith("1.21") and "yarn" not in values.get("deps", {}):
                errors.append(f"{version} has no deps.yarn")
            if version.startswith("26.") and "yarn" in values.get("deps", {}):
                errors.append(f"{version} unexpectedly declares deps.yarn")
        vcs = re.search(r'\bvcsVersion\s*=\s*"([^"]+)"', settings)
        if vcs is None or vcs.group(1) not in declared:
            errors.append("Stonecutter vcsVersion is absent from the version list")
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"version configuration cannot be read: {exc}")
        declared = []

    canonical = repo / CANONICAL_SKILL
    claude = repo / CLAUDE_SKILL
    claude_status = "SKIP Claude skill pointer (not in this checkout)"
    try:
        canonical_meta = frontmatter(canonical.read_text(encoding="utf-8"))
        if not canonical_meta.get("name") or not canonical_meta.get("description"):
            errors.append(f"{CANONICAL_SKILL} is missing name or description")
        if ignored(repo, CANONICAL_SKILL.as_posix()):
            errors.append(f"{CANONICAL_SKILL} is ignored by git")
        if ignored(repo, "docs/research/verification-fixture.md"):
            errors.append("docs/research/*.md is ignored by git")
        if not ignored(repo, ".claude/settings.local.json"):
            errors.append("personal .claude/settings.local.json is not ignored by git")

        if claude.is_file():
            claude_source = claude.read_text(encoding="utf-8")
            claude_meta = frontmatter(claude_source)
            for key in ("name", "description"):
                if claude_meta.get(key) != canonical_meta.get(key):
                    errors.append(f"{CLAUDE_SKILL} {key} differs from the canonical skill")
            pointer = "../../../.agents/skills/instant-p2p-maintainer/SKILL.md"
            if pointer not in claude_source:
                errors.append(f"{CLAUDE_SKILL} does not link to the canonical skill")
            if ignored(repo, CLAUDE_SKILL.as_posix()):
                errors.append(f"{CLAUDE_SKILL} is ignored by git")
            if ignored(repo, "docs/research/nested/verification-fixture.md"):
                errors.append("nested docs/research Markdown is ignored by git")
            claude_status = "PASS Claude skill pointer and documentation ignore rules"
        elif args.require_claude or not ignored(repo, CLAUDE_SKILL.as_posix()):
            errors.append(f"required {CLAUDE_SKILL} is missing")
    except (OSError, ValueError, RuntimeError) as exc:
        errors.append(f"skill/ignore contract cannot be read: {exc}")

    if errors:
        for item in errors:
            fail(item)
        return 1
    print(claude_status)
    print(f"PASS {len(declared)} Stonecutter, CI, and dependency versions")
    print("PASS canonical skill discovery and git ignore rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
