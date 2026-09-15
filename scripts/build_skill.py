#!/usr/bin/env python3
"""Package skills/mimir for chat apps that accept uploaded skills, and print
the release notes for a version from CHANGELOG.md.

Two packages from the same files, because the apps disagree on the layout:

* mimir.skill     a zip with the skill FOLDER at the root    Claude, ChatGPT
* mimir-m365.zip  a zip with SKILL.md itself at the root     Microsoft 365 Copilot

Both carry a trimmed frontmatter (name plus a short Polish description:
Claude.ai caps descriptions at 200 characters, and fields another app may not
know are dropped) and a Polish short_description in agents/openai.yaml,
because that is what users see in their skills list. Files in the repo stay
untouched.

Usage:
    python3 scripts/build_skill.py              # both packages into dist/
    python3 scripts/build_skill.py --out DIR    # both packages into DIR
    python3 scripts/build_skill.py --notes 2.2.1

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
DIST = ROOT / "dist"
SKILL_NAME = "mimir"

DESCRIPTION_LIMIT = 200
# Polish on purpose: apps show this line in the user's skills list, and today
# every visitor who gets the package link comes from Polish campaigns.
SHORT_DESCRIPTION = (
    "Mimir buduje Twój drugi mózg (vault notatek SIXPACK i opcjonalny asystent AI) "
    "w 15-minutowej rozmowie. Użyj, gdy ktoś mówi: uruchom Mimira, zbuduj mi second brain."
)
SHORT_DISPLAY = "Twój drugi mózg w 15 minut"

# Microsoft 365 Copilot, Agent Builder custom skills (preview), per Microsoft Learn.
M365_INSTRUCTIONS_LIMIT = 20000
M365_MAX_FILES = 350
M365_MAX_DEPTH = 3
M365_ALLOWED_SUFFIXES = {
    ".json", ".xml", ".yaml", ".yml", ".ini", ".config", ".utf8", ".txt", ".rtf",
    ".md", ".html", ".htm", ".csv", ".tsv", ".png", ".jpg", ".jpeg", ".gif", ".bmp",
    ".log", ".py", ".js", ".mjs", ".cjs", ".ts", ".mts", ".sh", ".bash",
}

SKIP = {"__pycache__", ".DS_Store"}
_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def bundle_skill_md(text: str) -> str:
    """SKILL.md with a frontmatter of exactly name + SHORT_DESCRIPTION."""
    match = _FRONTMATTER.match(text)
    if not match:
        raise ValueError("SKILL.md has no frontmatter")
    head = f"name: {SKILL_NAME}\ndescription: {json.dumps(SHORT_DESCRIPTION, ensure_ascii=False)}"
    return f"---\n{head}\n---\n{text[match.end():]}"


def bundle_openai_yaml(text: str) -> str:
    return re.sub(
        r"(?m)^(\s*short_description:\s*).*$",
        lambda m: m.group(1) + json.dumps(SHORT_DISPLAY, ensure_ascii=False),
        text,
    )


TRANSFORMS = {"SKILL.md": bundle_skill_md, "agents/openai.yaml": bundle_openai_yaml}


def bundle_files() -> list:
    return [
        p for p in sorted(SKILL_DIR.rglob("*"))
        if p.is_file() and not SKIP & set(p.relative_to(SKILL_DIR).parts)
    ]


def _write(out: Path, prefix: str) -> Path:
    if len(SHORT_DESCRIPTION) > DESCRIPTION_LIMIT:
        raise ValueError(f"SHORT_DESCRIPTION is {len(SHORT_DESCRIPTION)} chars, limit {DESCRIPTION_LIMIT}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as bundle:
        for p in bundle_files():
            rel = p.relative_to(SKILL_DIR).as_posix()
            transform = TRANSFORMS.get(rel)
            if transform:
                bundle.writestr(prefix + rel, transform(p.read_text(encoding="utf-8")))
            else:
                bundle.write(p, prefix + rel)
    return out


def build(out: Path = DIST / "mimir.skill") -> Path:
    """Claude and ChatGPT: the skill folder at the zip root."""
    return _write(out, f"{SKILL_NAME}/")


def m365_problems() -> list:
    problems = []
    files = bundle_files()
    if len(files) > M365_MAX_FILES:
        problems.append(f"{len(files)} files, limit {M365_MAX_FILES}")
    for p in files:
        rel = p.relative_to(SKILL_DIR)
        if len(rel.parts) - 1 > M365_MAX_DEPTH:
            problems.append(f"{rel.as_posix()}: deeper than {M365_MAX_DEPTH} folders")
        if p.suffix.lower() not in M365_ALLOWED_SUFFIXES:
            problems.append(f"{rel.as_posix()}: file type not accepted by Microsoft 365 Copilot")
    instructions = bundle_skill_md((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"))
    if len(instructions) >= M365_INSTRUCTIONS_LIMIT:
        problems.append(f"SKILL.md is {len(instructions)} chars, limit {M365_INSTRUCTIONS_LIMIT}")
    return problems


def build_m365(out: Path = DIST / "mimir-m365.zip") -> Path:
    """Microsoft 365 Copilot Agent Builder: SKILL.md itself at the zip root."""
    problems = m365_problems()
    if problems:
        raise ValueError("Microsoft 365 package: " + "; ".join(problems))
    return _write(out, "")


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
    ap = argparse.ArgumentParser(description="Package mimir.skill + mimir-m365.zip / print release notes")
    ap.add_argument("--out", type=Path, default=DIST, help="folder for both packages (default dist/)")
    ap.add_argument("--notes", metavar="VERSION", help="print the CHANGELOG section for VERSION and exit")
    args = ap.parse_args()
    try:
        if args.notes:
            sys.stdout.write(changelog_section(args.notes))
            return 0
        print(f"built: {build(args.out / 'mimir.skill')}")
        print(f"built: {build_m365(args.out / 'mimir-m365.zip')}")
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
