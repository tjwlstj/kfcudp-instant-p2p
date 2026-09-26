#!/usr/bin/env python3
"""Run Minecraft-independent Java contract checks against the current sources.

Only Python's standard library and a JDK 21+ are required. Classes are compiled
in a temporary directory, so running this script leaves the checkout untouched.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


SOURCE_DIR = "src/client/java/kfc/udp/client/webrtc"
HARNESS_DIR = "tools/tests/java/kfc/udp/client/webrtc"


@dataclass(frozen=True)
class Suite:
    name: str
    sources: tuple[str, ...]
    harness: str
    optional: bool = False

    @property
    def main_class(self) -> str:
        return "kfc.udp.client.webrtc." + self.harness.removesuffix(".java")


SUITES = (
    Suite("base contracts", ("ChannelRules.java", "VillasMsg.java"), "ContractCheck.java"),
    Suite("local security", ("InviteCodes.java", "LocalGuestListener.java"),
          "LocalSecurityCheck.java", optional=True),
    Suite("role refresh", ("RoleRefreshCoordinator.java",),
          "RoleRefreshCheck.java", optional=True),
)


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
    if not repo.is_dir():
        parser.error(f"repository directory does not exist: {repo}")

    try:
        java, javac = jdk_commands(args.java_home)
    except ValueError as exc:
        parser.error(str(exc))

    with tempfile.TemporaryDirectory(prefix="instant-p2p-contracts-") as output:
        failed = False
        for suite in SUITES:
            sources = [repo / SOURCE_DIR / name for name in suite.sources]
            present = [source.is_file() for source in sources]
            if suite.optional and not any(present):
                print(f"SKIP {suite.name}: source files absent", flush=True)
                continue
            missing = [str(source) for source, exists in zip(sources, present) if not exists]
            harness = tool_root / HARNESS_DIR / suite.harness
            if not harness.is_file():
                missing.append(str(harness))
            if missing:
                print(f"FAIL {suite.name}: missing required file(s): " + ", ".join(missing),
                      file=sys.stderr, flush=True)
                failed = True
                continue

            suite_output = Path(output) / suite.harness.removesuffix(".java")
            suite_output.mkdir()
            print(f"Compiling {suite.name} (release 21)...", flush=True)
            try:
                compiled = subprocess.run(
                    [javac, "--release", "21", "-encoding", "UTF-8", "-d", str(suite_output),
                     *(str(source) for source in sources), str(harness)],
                    cwd=repo,
                    timeout=90,
                    check=False,
                )
                if compiled.returncode:
                    print(f"FAIL {suite.name}: Java compilation failed", file=sys.stderr)
                    failed = True
                    continue

                print(f"Running {suite.name}...", flush=True)
                checked = subprocess.run(
                    [java, "-cp", str(suite_output), suite.main_class],
                    cwd=repo,
                    timeout=30,
                    check=False,
                )
                if checked.returncode:
                    print(f"FAIL {suite.name}: Java checks failed", file=sys.stderr)
                    failed = True
                else:
                    print(f"PASS {suite.name}", flush=True)
            except subprocess.TimeoutExpired as exc:
                print(f"FAIL {suite.name}: {Path(exc.cmd[0]).name} timed out", file=sys.stderr)
                failed = True
            except OSError as exc:
                print(f"FAIL {suite.name}: could not start JDK command: {exc}", file=sys.stderr)
                failed = True
        return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
