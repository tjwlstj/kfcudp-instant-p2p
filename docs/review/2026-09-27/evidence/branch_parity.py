#!/usr/bin/env python3
"""Compare paired Stonecutter branches (`//? if >=26.x { ... //?} else { ... //?}`).

The 26.x (Mojang names) and 1.21.x (Yarn names) bodies of each pair are
normalized to one vocabulary, so the remaining diff shows behavioural
differences: a fix applied to one Minecraft era but not the other.

The rename table is a heuristic. A reported pair still needs a human reading,
and an empty report does not prove that both eras behave the same.

Usage (from the repository root):
    py -3 docs/review/2026-09-27/evidence/branch_parity.py src
    py -3 docs/review/2026-09-27/evidence/branch_parity.py src --all
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
    """Yield (line, condition, 26.x body, 1.21.x body) for each `26` if/else pair."""
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        match = IF_RE.match(lines[i])
        if not (match and "26" in match.group(1)):
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="source root, usually src")
    parser.add_argument("--all", action="store_true",
                        help="also print import-only and short (<6 line) differences")
    args = parser.parse_args()

    total, differing, reported = 0, 0, []
    for path in sorted(args.source.rglob("*.java")):
        for line_no, condition, era26, era121 in pairs(path):
            total += 1
            a, b = normalize(era26), normalize(era121)
            if a == b:
                continue
            differing += 1
            if not args.all and (all(x.startswith("import") for x in a + b) or max(len(a), len(b)) < 6):
                continue
            diff = [d for d in difflib.unified_diff(a, b, "26.x", "1.21.x", n=0, lineterm="")
                    if not d.startswith(("---", "+++", "@@"))]
            reported.append((len(diff), path.as_posix(), line_no, condition, diff))

    reported.sort(key=lambda row: -row[0])
    print(f"pairs={total} textually-different={differing} reported={len(reported)}")
    for size, rel, line_no, condition, diff in reported:
        print(f"\n### {rel}:{line_no} ({condition}) diff-lines={size}")
        for line in diff:
            print("   ", line[:170])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
