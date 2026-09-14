#!/usr/bin/env python3
"""Package skills/mimir as mimir.skill for upload to Claude.ai, and print the
release notes for a version from CHANGELOG.md.

A .skill file is a zip whose root is the skill folder. Claude.ai caps the
description at 200 characters. SKILL.md in the repo keeps the long
description that trigger matching in Claude Code relies on; only the copy
inside the bundle gets SHORT_DESCRIPTION.

Usage:
    python3 scripts/build_skill.py                       # writes dist/mimir.skill
    python3 scripts/build_skill.py --out path/mimir.skill
    python3 scripts/build_skill.py --notes 2.2.0         # CHANGELOG section to stdout

Stdlib only. GitHub Actions runs it on every v* tag (release.yml).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "mimir"
DEFAULT_OUT = ROOT / "dist" / "mimir.skill"

DESCRIPTION_LIMIT = 200
# Polish on purpose: Claude.ai shows this line in the user's Skills list, and
# today every visitor who gets the .skill link comes from Polish campaigns.
SHORT_DESCRIPTION = (
    "Mimir buduje Twój drugi mózg (vault notatek SIXPACK i opcjonalny asystent AI) "
    "w 15-minutowej rozmowie. Użyj, gdy ktoś mówi: uruchom Mimira, zbuduj mi second brain."
)
SKIP = {"__pycache__", ".DS_Store"}

_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def short_skill_md(text: str) -> str:
    """SKILL.md with its description replaced by SHORT_DESCRIPTION.

    Handles a folded (`description: >`) or single-line description; every
    other frontmatter key and the whole body stay as they are."""
    match = _FRONTMATTER.match(text)
    if not match:
        raise ValueError("SKILL.md has no frontmatter")
    lines = match.group(1).splitlines()
    out, i = [], 0
    while i < len(lines):
        if lines[i].startswith("description:"):
            i += 1
            while i < len(lines) and (not lines[i] or lines[i][0].isspace()):
                i += 1
            out.append("description: " + json.dumps(SHORT_DESCRIPTION, ensure_ascii=False))
            continue
        out.append(lines[i])
        i += 1
    return "---\n" + "\n".join(out) + "\n---\n" + text[match.end():]


def bundle_files() -> list:
    return [
        p for p in sorted(SKILL_DIR.rglob("*"))
        if p.is_file() and not SKIP & set(p.relative_to(SKILL_DIR).parts)
    ]


def build(out: Path = DEFAULT_OUT) -> Path:
    if len(SHORT_DESCRIPTION) > DESCRIPTION_LIMIT:
        raise ValueError(f"SHORT_DESCRIPTION is {len(SHORT_DESCRIPTION)} chars, limit {DESCRIPTION_LIMIT}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as bundle:
        for p in bundle_files():
            rel = p.relative_to(SKILL_DIR)
            arcname = (Path(SKILL_DIR.name) / rel).as_posix()
            if rel.as_posix() == "SKILL.md":
                bundle.writestr(arcname, short_skill_md(p.read_text(encoding="utf-8")))
            else:
                bundle.write(p, arcname)
    return out


def changelog_section(version: str) -> str:
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(
        rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|^\[[^\]]+\]: |\Z)",
        text, re.MULTILINE | re.DOTALL,
    )
    if not match or not match.group(1).strip():
        raise ValueError(f"CHANGELOG.md has no section for {version}")
    return match.group(1).strip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Package mimir.skill / print release notes")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="where to write mimir.skill")
    ap.add_argument("--notes", metavar="VERSION", help="print the CHANGELOG section for VERSION and exit")
    args = ap.parse_args()
    try:
        if args.notes:
            sys.stdout.write(changelog_section(args.notes))
            return 0
        print(f"built: {build(args.out)}")
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
