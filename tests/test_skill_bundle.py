"""The upload packages for chat apps (scripts/build_skill.py).

mimir.skill (Claude, ChatGPT) needs the skill folder at the zip root;
mimir-m365.zip (Microsoft 365 Copilot) needs SKILL.md itself at the root and
stays within Microsoft's preview limits. An app rejects a wrong package only
after the user has downloaded it, so these checks move that failure to the push.

Run: python3 -m unittest discover -s tests -v
"""
import importlib.util
import re
import tempfile
import unittest
import zipfile
from pathlib import Path

try:  # optional: CI installs it
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("build_skill", ROOT / "scripts" / "build_skill.py")
bs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bs)


def split_frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    return match.group(1), text[match.end():]


def read_zip(path):
    with zipfile.ZipFile(path) as bundle:
        return {name: bundle.read(name) for name in bundle.namelist()}


class PackagesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls._tmp.name)
        cls.skill = read_zip(bs.build(tmp / "mimir.skill"))
        cls.m365 = read_zip(bs.build_m365(tmp / "mimir-m365.zip"))
        cls.repo_files = {p.relative_to(bs.SKILL_DIR).as_posix() for p in bs.bundle_files()}

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def packages(self):
        return {
            "mimir.skill": {name[len("mimir/"):]: data for name, data in self.skill.items()},
            "mimir-m365.zip": self.m365,
        }

    # ------------------------------------------------ layout per app

    def test_skill_folder_is_the_root_of_mimir_skill(self):
        self.assertIn("mimir/SKILL.md", self.skill)
        self.assertTrue(all(n.startswith("mimir/") for n in self.skill), sorted(self.skill))

    def test_skill_md_is_the_root_of_the_m365_package(self):
        self.assertIn("SKILL.md", self.m365)
        self.assertFalse([n for n in self.m365 if n.startswith("mimir/")])

    def test_both_packages_carry_every_skill_file_and_no_cache(self):
        for label, files in self.packages().items():
            with self.subTest(label):
                self.assertEqual(set(files), self.repo_files)
                self.assertIn("wizard/hosted.md", files)
                self.assertIn("scripts/build_vault.py", files)
                self.assertFalse([n for n in files if "__pycache__" in n or n.endswith(".DS_Store")])

    # ------------------------------------------------ what the user sees

    def test_short_description_fits_every_app(self):
        self.assertLessEqual(len(bs.SHORT_DESCRIPTION), bs.DESCRIPTION_LIMIT)
        self.assertNotRegex(bs.SHORT_DESCRIPTION, r"[<>]")

    def test_frontmatter_is_name_and_description_only_body_unchanged(self):
        _, repo_body = split_frontmatter((bs.SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"))
        for label, files in self.packages().items():
            with self.subTest(label):
                head, body = split_frontmatter(files["SKILL.md"].decode("utf-8"))
                self.assertEqual(body, repo_body)
                self.assertEqual(head.splitlines(), ["name: mimir", f'description: "{bs.SHORT_DESCRIPTION}"'])
                if yaml is not None:
                    self.assertEqual(yaml.safe_load(head),
                                     {"name": "mimir", "description": bs.SHORT_DESCRIPTION})

    def test_skills_list_label_is_polish_in_bundles_only(self):
        repo_yaml = (bs.SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
        for label, files in self.packages().items():
            with self.subTest(label):
                bundled = files["agents/openai.yaml"].decode("utf-8")
                self.assertIn(f'short_description: "{bs.SHORT_DISPLAY}"', bundled)
                self.assertIn("display_name:", bundled)
        self.assertNotIn(bs.SHORT_DISPLAY, repo_yaml)

    # ------------------------------------------------ Microsoft 365 limits

    def test_m365_package_is_within_microsoft_limits(self):
        self.assertEqual(bs.m365_problems(), [])
        self.assertLessEqual(len(self.m365), bs.M365_MAX_FILES)
        self.assertLess(len(self.m365["SKILL.md"].decode("utf-8")), bs.M365_INSTRUCTIONS_LIMIT)
        for name in self.m365:
            self.assertLessEqual(len(Path(name).parts) - 1, bs.M365_MAX_DEPTH, name)
            self.assertIn(Path(name).suffix.lower(), bs.M365_ALLOWED_SUFFIXES, name)

    def test_m365_build_refuses_a_package_over_the_limits(self):
        original = bs.M365_MAX_FILES
        bs.M365_MAX_FILES = 1
        try:
            with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
                bs.build_m365(Path(tmp) / "x.zip")
        finally:
            bs.M365_MAX_FILES = original

    # ------------------------------------------------ release notes

    def test_release_notes_come_from_the_changelog(self):
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        newest = re.search(r"(?m)^## \[(\d+\.\d+\.\d+)\]", changelog).group(1)
        notes = bs.changelog_section(newest)
        self.assertTrue(notes.strip())
        self.assertNotIn("## [", notes)
        with self.assertRaises(ValueError):
            bs.changelog_section("9.9.9")


if __name__ == "__main__":
    unittest.main()
