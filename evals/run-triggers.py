#!/usr/bin/env python3
"""Trigger eval for the `mimir` skill.

For every row in evals/triggers.md, runs `claude -p <prompt>` in a throwaway
folder where the skill is available, and checks whether the agent invoked the
`mimir` skill (a `Skill` tool call whose input mentions "mimir"). Compares
with the row's expected value (fire / no-fire) and prints a scoreboard.

Writes nothing outside a temp folder. Needs the Claude Code CLI (`claude`).

Usage:
    python3 evals/run-triggers.py            # all rows
    python3 evals/run-triggers.py N01 T03    # selected ids
    python3 evals/run-triggers.py --runs 3   # repeat each prompt (flakiness check)
    python3 evals/run-triggers.py --skill-dir /path/to/other/mimir   # A/B another version
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "mimir"
TABLE = ROOT / "evals" / "triggers.md"
ROW = re.compile(r"^\|\s*([TN]\d+)\s*\|\s*(fire|no-fire)\s*\|\s*(.+?)\s*\|\s*$")


def load_cases(only: set[str]) -> list[tuple[str, str, str]]:
    cases = []
    for line in TABLE.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if m and (not only or m.group(1) in only):
            cases.append((m.group(1), m.group(2), m.group(3)))
    return cases


def skill_fired(stream: str) -> bool:
    for raw in stream.splitlines():
        raw = raw.strip()
        if not raw.startswith("{"):
            continue
        try:
            ev = json.loads(raw)
        except json.JSONDecodeError:
            continue
        msg = ev.get("message")
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            if block.get("name") != "Skill":
                continue
            if "mimir" in json.dumps(block.get("input", {})).lower():
                return True
    return False


def run_once(prompt: str, workdir: Path, timeout: int) -> tuple[bool, str]:
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "stream-json", "--verbose",
        "--max-turns", "2",
        # project-only settings: a user-level copy of the skill (e.g. an older
        # `npx skills add` install) would otherwise shadow the one under test
        "--setting-sources", "project",
        "--disallowedTools", "Write,Edit,MultiEdit,NotebookEdit,Bash",
    ]
    env = {k: v for k, v in os.environ.items() if not k.startswith("EVAL_")}
    try:
        proc = subprocess.run(
            cmd, cwd=workdir, capture_output=True, text=True, timeout=timeout, env=env,
        )
    except subprocess.TimeoutExpired:
        return False, "timeout"
    out = proc.stdout
    if proc.returncode != 0 and not out.strip():
        return False, f"claude exited {proc.returncode}: {proc.stderr.strip()[:200]}"
    return skill_fired(out), ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="case ids to run (default: all)")
    ap.add_argument("--runs", type=int, default=1, help="repetitions per case")
    ap.add_argument("--timeout", type=int, default=180, help="seconds per run")
    ap.add_argument("--skill-dir", type=Path, default=SKILL_DIR,
                    help="skill folder to test (default: skills/mimir in this repo)")
    args = ap.parse_args()

    if shutil.which("claude") is None:
        print("claude CLI not found on PATH", file=sys.stderr)
        return 2
    cases = load_cases(set(args.ids))
    if not cases:
        print("no cases matched", file=sys.stderr)
        return 2

    tmp = Path(tempfile.mkdtemp(prefix="mimir-evals-"))
    (tmp / ".claude" / "skills").mkdir(parents=True)
    (tmp / ".claude" / "skills" / "mimir").symlink_to(args.skill_dir.resolve(), target_is_directory=True)

    passed = 0
    failures: list[str] = []
    print(f"workdir {tmp}  cases {len(cases)}  runs/case {args.runs}\n")
    print(f"{'id':5} {'expected':9} {'got':22} result")
    try:
        for cid, expected, prompt in cases:
            fired = []
            err = ""
            for _ in range(args.runs):
                f, e = run_once(prompt, tmp, args.timeout)
                fired.append(f)
                err = err or e
            n_fire = sum(fired)
            got = f"fire {n_fire}/{len(fired)}"
            ok = (n_fire == len(fired)) if expected == "fire" else (n_fire == 0)
            ok = ok and not err
            passed += ok
            if not ok:
                failures.append(f"{cid} ({expected}, got {got}{', ' + err if err else ''})")
            print(f"{cid:5} {expected:9} {got:22} {'PASS' if ok else 'FAIL'}{'  ' + err if err else ''}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{passed}/{len(cases)} passed")
    if failures:
        print("failures: " + "; ".join(failures))
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
