"""Consistency of the repo itself: what a push must not break.

- SKILL.md frontmatter loads (name, description within the platform limit)
- every file one document points to actually exists, raw GitHub URLs included
- the red lines in SKILL.md (Claude) and AGENTS.md (Codex) say the same thing
- plugin manifests agree with each other and with CHANGELOG.md

Run: python3 -m unittest discover -s tests -v
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "mimir"

# Claude Code cuts a skill description longer than this.
DESCRIPTION_LIMIT = 1024

# Each red line is pinned by a phrase that must appear in BOTH entry points.
# Changing a red line means changing it in both files, or this test fails.
RED_LINE_ANCHORS = {
    "language is detected, not asked": "never ask which one",
    "no credentials": "passwords, tokens, or api keys",
    "private repos": "private by default",
    "existing files untouched": "byte-identical",
    "fresh start renames, never deletes": "<name>-backup-<date>",
    "do only what was asked": "noticing a gap is not permission",
    "confirm external actions": "confirm before creating anything on an external service",
    "no retry loops": "fails twice",
}

REF_RE = re.compile(
    r"(?<![\w/.-])((?:skills/mimir/)?(?:wizard|templates|scripts|agents|evals)/[A-Za-z0-9_.-]+\.(?:md|py|yaml|json))"
)
RAW_URL_RE = re.compile(r"raw\.githubusercontent\.com/533konrad/mimir/main/([^\s)>\]`]+)")
VERSION_HEADING_RE = re.compile(r"(?m)^## \[(\d+\.\d+\.\d+)\] - \d{4}-\d{2}-\d{2}$")


def read(path):
    return path.read_text(encoding="utf-8")


def normalized(text):
    return " ".join(text.lower().split())


def frontmatter_field(text, key):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    lines = match.group(1).splitlines()
    for i, line in enumerate(lines):
        if line.startswith(f"{key}:"):
            value = line[len(key) + 1:].strip()
            if value in (">", "|", ">-", "|-"):
                block = []
                for nxt in lines[i + 1:]:
                    if nxt and not nxt[0].isspace():
                        break
                    block.append(nxt.strip())
                return " ".join(b for b in block if b)
            return value.strip("\"'")
    return None


def markdown_files():
    return [p for p in ROOT.rglob("*.md")
            if ".git" not in p.parts and "inspiracja" not in p.parts]


class SkillFrontmatterTest(unittest.TestCase):
    def setUp(self):
        self.text = read(SKILL_DIR / "SKILL.md")

    def test_name_matches_folder_and_is_kebab_case(self):
        name = frontmatter_field(self.text, "name")
        self.assertEqual(name, SKILL_DIR.name)
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)

    def test_description_fits_the_limit(self):
        description = frontmatter_field(self.text, "description")
        self.assertTrue(description, "description is empty")
        self.assertLessEqual(
            len(description), DESCRIPTION_LIMIT,
            f"description is {len(description)} chars; Claude Code cuts at {DESCRIPTION_LIMIT}",
        )
        self.assertNotRegex(description, r"[<>]", "angle brackets are not allowed in a description")


class ReferencesTest(unittest.TestCase):
    def test_referenced_files_exist(self):
        missing = []
        for doc in markdown_files():
            for ref in REF_RE.findall(read(doc)):
                candidates = (ROOT / ref, SKILL_DIR / ref, doc.parent / ref)
                if not any(c.is_file() for c in candidates):
                    missing.append(f"{doc.relative_to(ROOT)} -> {ref}")
        self.assertEqual(missing, [])

    def test_raw_github_urls_point_at_real_paths(self):
        """The magic-prompt install reads these URLs; a rename breaks it silently."""
        missing = []
        for doc in markdown_files():
            for path in RAW_URL_RE.findall(read(doc)):
                path = path.rstrip(".,;:")
                if not (ROOT / path).exists():
                    missing.append(f"{doc.relative_to(ROOT)} -> {path}")
        self.assertEqual(missing, [])


class PromiseTest(unittest.TestCase):
    """Mimir promises 15 minutes, everywhere: README, landing, ads, wizard.
    A stray "10 minutes" in one place makes every other number look made up."""

    DURATION_RE = re.compile(r"(?i)(?<!\d)(\d{1,2})[ -]?(?:minut\w*|minutes?|min)\b")
    PROMISE = "15"
    # Short sub-steps that are not the promise: connect GitHub in 5, install
    # Obsidian in 3, redo the interview in 2, the obsidian-git interval of 30.
    # Anything else (10, 20...) reads as a competing promise and fails.
    SUB_STEPS = {"2", "3", "5", "30"}

    # Where the promise is made to a user. Internal model instructions carry
    # their own budgets (interview.md: "5-7 minutes" for the interview alone,
    # assistant-spec.md: the "40-minute interrogation" to avoid) and are not
    # checked here.
    USER_FACING = [
        "README.md",
        "skills/mimir/SKILL.md",
        "skills/mimir/wizard/WIZARD.md",
        "skills/mimir/wizard/hosted.md",
        "AGENTS.md",
        "CLAUDE.md",
    ]

    def test_every_advertised_duration_is_15_minutes(self):
        offenders = []
        for rel in self.USER_FACING:
            doc = ROOT / rel
            for line_no, line in enumerate(read(doc).splitlines(), 1):
                for match in self.DURATION_RE.finditer(line):
                    if match.group(1) == self.PROMISE or match.group(1) in self.SUB_STEPS:
                        continue
                    offenders.append(f"{doc.relative_to(ROOT)}:{line_no}: {match.group(0)}")
        self.assertEqual(offenders, [], "Mimir's promise is 15 minutes; see PromiseTest")

    def test_short_skill_description_says_15_minutes(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_skill", ROOT / "scripts" / "build_skill.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertIn("15-minut", module.SHORT_DESCRIPTION)


class RedLinesTest(unittest.TestCase):
    def test_skill_and_agents_carry_the_same_red_lines(self):
        skill = normalized(read(SKILL_DIR / "SKILL.md"))
        agents = normalized(read(ROOT / "AGENTS.md"))
        for label, anchor in RED_LINE_ANCHORS.items():
            with self.subTest(label):
                self.assertIn(anchor, skill, f"SKILL.md lost the red line: {label}")
                self.assertIn(anchor, agents, f"AGENTS.md lost the red line: {label}")


class ManifestsTest(unittest.TestCase):
    def setUp(self):
        self.plugin = json.loads(read(ROOT / ".claude-plugin" / "plugin.json"))
        self.marketplace = json.loads(read(ROOT / ".claude-plugin" / "marketplace.json"))

    def test_plugin_points_at_the_skill(self):
        self.assertEqual(self.plugin["name"], "mimir")
        self.assertRegex(self.plugin["version"], r"^\d+\.\d+\.\d+$")
        for rel in self.plugin["skills"]:
            self.assertTrue((ROOT / rel / "SKILL.md").is_file(), rel)

    def test_marketplace_lists_the_plugin(self):
        entries = {p["name"]: p for p in self.marketplace["plugins"]}
        self.assertIn(self.plugin["name"], entries)
        self.assertTrue((ROOT / entries[self.plugin["name"]]["source"]).is_dir())

    def test_changelog_top_version_matches_plugin(self):
        changelog = read(ROOT / "CHANGELOG.md")
        self.assertIn("## [Unreleased]", changelog)
        versions = VERSION_HEADING_RE.findall(changelog)
        self.assertTrue(versions, "CHANGELOG.md has no released version heading")
        self.assertEqual(
            versions[0], self.plugin["version"],
            "plugin.json and the newest CHANGELOG.md version disagree",
        )

    def test_codex_metadata_is_filled(self):
        yaml = read(SKILL_DIR / "agents" / "openai.yaml")
        for key in ("display_name", "short_description"):
            self.assertRegex(yaml, rf'(?m)^\s+{key}:\s*"?\S', key)


if __name__ == "__main__":
    unittest.main()
