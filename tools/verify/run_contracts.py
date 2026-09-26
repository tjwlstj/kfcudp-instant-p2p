#!/usr/bin/env python3
"""Run Minecraft-independent Java contract checks against the current sources.

Only Python's standard library and a JDK 21+ are required. Classes are compiled
in a temporary directory, so running this script leaves the checkout untouched.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


MAIN_CLASS = "kfc.udp.client.webrtc.ContractCheck"
SOURCES = (
    "src/client/java/kfc/udp/client/webrtc/ChannelRules.java",
    "src/client/java/kfc/udp/client/webrtc/VillasMsg.java",
)
HARNESS = "tools/tests/java/kfc/udp/client/webrtc/ContractCheck.java"


def jdk_commands(java_home: Path | None) -> tuple[str, str]:
    home = java_home or (Path(os.environ["JAVA_HOME"]) if os.environ.get("JAVA_HOME") else None)
    if home is not None:
        suffix = ".exe" if os.name == "nt" else ""
        java = home / "bin" / f"java{suffix}"
        javac = home / "bin" / f"javac{suffix}"
        if not java.is_file() or not javac.is_file():
            raise ValueError(f"JDK java and javac were not found under {home / 'bin'}")
        return str(java), str(javac)

    java = shutil.which("java")
    javac = shutil.which("javac")
    if not java or not javac:
        raise ValueError("A JDK 21+ is required; set --java-home or JAVA_HOME, or put java and javac on PATH")
    return java, javac


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="repository root (default: inferred from this script)",
    )
    parser.add_argument(
        "--java-home",
        type=Path,
        help="JDK 21+ directory containing bin/java and bin/javac",
    )
    args = parser.parse_args()

    repo = args.repo.resolve()
    # The harness belongs to this tool checkout; --repo selects the sources
    # under test, including PR branches that do not contain this tool yet.
    tool_root = Path(__file__).resolve().parents[2]
    sources = [repo / source for source in SOURCES] + [tool_root / HARNESS]
    missing = [str(source) for source in sources if not source.is_file()]
    if missing:
        parser.error("missing source file(s): " + ", ".join(missing))

    try:
        java, javac = jdk_commands(args.java_home)
    except ValueError as exc:
        parser.error(str(exc))

    with tempfile.TemporaryDirectory(prefix="instant-p2p-contracts-") as output:
        print("Compiling Java contract checks (release 21)...", flush=True)
        try:
            compiled = subprocess.run(
                [javac, "--release", "21", "-encoding", "UTF-8", "-d", output,
                 *(str(source) for source in sources)],
                cwd=repo,
                timeout=90,
                check=False,
            )
            if compiled.returncode:
                return compiled.returncode

            print("Running Java contract checks...", flush=True)
            checked = subprocess.run(
                [java, "-cp", output, MAIN_CLASS],
                cwd=repo,
                timeout=30,
                check=False,
            )
            return checked.returncode
        except subprocess.TimeoutExpired as exc:
            print(f"Timed out while running {Path(exc.cmd[0]).name}", file=sys.stderr)
            return 124
        except OSError as exc:
            print(f"Could not start JDK command: {exc}", file=sys.stderr)
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
