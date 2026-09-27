#!/usr/bin/env python3
"""Compare paired Stonecutter branches (`//? if >=26.x { ... //?} else { ... //?}`).

The 26.x (Mojang names) and 1.21.x (Yarn names) bodies of each pair are
normalized to one vocabulary, so the remaining diff shows behavioural
differences: a fix applied to one Minecraft era but not the other.

Two kinds of version code cannot be compared this way and are listed for a
human reading instead: `//? if` blocks without an `else` (for example a
26.3-only method or a `>=1.21.9 <26.1` range), and the individual arms of
three-way splits written as separate blocks.

The rename table is a heuristic. A reported pair still needs a human reading,
and an empty report does not prove that both eras behave the same.

Usage (from the repository root):
    py -3 docs/review/2026-09-27/evidence/branch_parity.py src
    py -3 docs/review/2026-09-27/evidence/branch_parity.py src --with-imports
"""

from __future__ import annotations

import argparse
import difflib
import re
from pathlib import Path

# Yarn (1.21.x) -> Mojang (26.x) names that commonly differ.
RENAMES = [
    (r"\bMinecraftClient\b", "Minecraft"), (r"\bText\b", "Component"),
    (r"\bFormatting\b", "ChatFormatting"), (r"\bServerPlayerEntity\b", "ServerPlayer"),
    (r"\bPlayerEntity\b", "Player"), (r"\bPlayerManager\b", "PlayerList"),
    (r"\bServerCommandSource\b", "CommandSourceStack"), (r"\bGameMode\b", "GameType"),
    (r"\bServerInfo\b", "ServerData"), (r"\bButtonWidget\b", "Button"),
    (r"\bDrawContext\b", "GuiGraphics"), (r"\bTextFieldWidget\b", "EditBox"),
    (r"\bCheckboxWidget\b", "Checkbox"), (r"\bClickableWidget\b", "AbstractWidget"),
    (r"\btextRenderer\b", "font"), (r"\bTextRenderer\b", "Font"),
    (r"\bgetPlayerManager\(\)", "getPlayerList()"),
    (r"\bgetPlayerList\(\)\.getPlayerList\(\)", "getPlayerList().getPlayers()"),
    (r"\bgetUuid\(\)", "getUUID()"), (r"\bnetworkHandler\b", "connection"),
    (r"\bsendMessage\(([^;]*), false\)", r"sendSystemMessage(\1)"),
    (r"\bsetScreen\(", "setScreenAndShow("), (r"\bcurrentScreen\b", "screen"),
    (r"\bclient\b", "minecraft"), (r"\bformatted\(", "withStyle("), (r"\bdimensions\(", "bounds("),
    (r"\bIdentifier\.of\(", "Identifier.fromNamespaceAndPath("),
]

IF_RE = re.compile(r"^\s*//\? if (.+?) \{\s*$")
ELSE_RE = re.compile(r"^\s*(?:\*/)?//\?\} else \{\s*$")
END_RE = re.compile(r"^\s*(?:\*/)?//\?\}\s*$")


def normalize(lines: list[str]) -> list[str]:
    out = []
    for line in lines:
        s = line.strip().removeprefix("/*").removesuffix("*/").strip()
        if s.startswith("*/"):
            s = s[2:].strip()
        if not s or s.startswith(("//", "*", "/**")):
            continue
        for pattern, replacement in RENAMES:
            s = re.sub(pattern, replacement, s)
        out.append(s)
    return out


def pairs(path: Path):
    """Yield (line, condition, if-arm body, else-arm body) for each if/else pair.

    Most pairs split 26.x from 1.21.x; a few split inside 1.21.x (for example
    `>=1.21.9`), and those are compared the same way.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        match = IF_RE.match(lines[i])
        if not match:
            i += 1
            continue
        start, condition, depth, else_line = i, match.group(1), 0, None
        j = i + 1
        while j < len(lines):
            if IF_RE.match(lines[j]):
                depth += 1
            elif ELSE_RE.match(lines[j]) and depth == 0:
                else_line = j
                break
            elif END_RE.match(lines[j]):
                if depth == 0:
                    break
                depth -= 1
            j += 1
        if else_line is None:
            i += 1
            continue
        k, depth = else_line + 1, 0
        while k < len(lines):
            if IF_RE.match(lines[k]):
                depth += 1
            elif END_RE.match(lines[k]):
                if depth == 0:
                    break
                depth -= 1
            k += 1
        yield start + 1, condition, lines[start + 1:else_line], lines[else_line + 1:k]
        i = k + 1


def unpaired_blocks(path: Path):
    """Yield (line, condition, body lines) for `//? if` blocks that have no `else` arm."""
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        match = IF_RE.match(line)
        if not match:
            continue
        depth, j = 0, i + 1
        while j < len(lines):
            if IF_RE.match(lines[j]):
                depth += 1
            elif ELSE_RE.match(lines[j]) and depth == 0:
                break
            elif END_RE.match(lines[j]):
                if depth == 0:
                    body = normalize(lines[i + 1:j])
                    yield i + 1, match.group(1), body
                    break
                depth -= 1
            j += 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="source root, usually src")
    parser.add_argument("--with-imports", action="store_true",
                        help="also print pairs and blocks that differ only in import lines")
    args = parser.parse_args()

    def import_only(lines: list[str]) -> bool:
        return bool(lines) and all(x.startswith("import") for x in lines)

    total, differing, import_pairs, reported = 0, 0, 0, []
    single, single_import = [], 0
    for path in sorted(args.source.rglob("*.java")):
        rel = path.as_posix()
        for line_no, condition, era26, era121 in pairs(path):
            total += 1
            a, b = normalize(era26), normalize(era121)
            if a == b:
                continue
            differing += 1
            if import_only(a + b) and not args.with_imports:
                import_pairs += 1
                continue
            diff = [d for d in difflib.unified_diff(a, b, "26.x", "1.21.x", n=0, lineterm="")
                    if not d.startswith(("---", "+++", "@@"))]
            reported.append((len(diff), rel, line_no, condition, diff))
        for line_no, condition, body in unpaired_blocks(path):
            if import_only(body) and not args.with_imports:
                single_import += 1
                continue
            single.append((rel, line_no, condition, body))

    reported.sort(key=lambda row: -row[0])
    print(f"pairs={total} textually-different={differing} import-only={import_pairs} reported={len(reported)}")
    for size, rel, line_no, condition, diff in reported:
        print(f"\n### {rel}:{line_no} ({condition}) diff-lines={size}")
        for line in diff:
            print("   ", line[:170])

    # Blocks written one after another at the same site are the arms of one
    # multi-way split; compare neighbouring arms, and print lone blocks whole.
    groups: list[list[tuple[str, int, str, list[str]]]] = []
    for block in single:
        rel, line_no, _, body = block
        previous = groups[-1][-1] if groups else None
        if previous and previous[0] == rel and line_no - previous[1] <= len(previous[3]) * 2 + 8:
            groups[-1].append(block)
        else:
            groups.append([block])
    lone = [g for g in groups if len(g) == 1]
    print(f"\n\nblocks-without-else={len(single) + single_import} import-only={single_import} "
          f"listed={len(single)} multi-way-sites={len(groups) - len(lone)} lone-blocks={len(lone)}")
    for group in groups:
        rel = group[0][0]
        arms = ", ".join(f"L{line}({cond})" for _, line, cond, _ in group)
        print(f"\n### {rel}: {arms}")
        if len(group) == 1:
            for line in group[0][3]:
                print("    |", line[:170])
            continue
        for (_, l1, c1, b1), (_, l2, c2, b2) in zip(group, group[1:]):
            diff = [d for d in difflib.unified_diff(b1, b2, c1, c2, n=0, lineterm="")
                    if not d.startswith(("---", "+++", "@@"))]
            print(f"  L{l1}({c1}) -> L{l2}({c2}): {'identical' if not diff else str(len(diff)) + ' diff lines'}")
            for line in diff:
                print("   ", line[:170])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
