"""The mimir.skill bundle for Claude.ai (scripts/build_skill.py).

Claude.ai rejects an upload whose zip root is not the skill folder or whose
description is over 200 characters, and it says so only after the user has
already downloaded the file. These checks move that failure to the push.

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


class SkillBundleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.out = bs.build(Path(cls._tmp.name) / "mimir.skill")
        with zipfile.ZipFile(cls.out) as bundle:
            cls.names = bundle.namelist()
            cls.skill_md = bundle.read("mimir/SKILL.md").decode("utf-8")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_short_description_fits_claude_ai(self):
        self.assertLessEqual(len(bs.SHORT_DESCRIPTION), 200)
        self.assertNotRegex(bs.SHORT_DESCRIPTION, r"[<>]")

    def test_skill_folder_is_the_zip_root(self):
        self.assertIn("mimir/SKILL.md", self.names)
        self.assertTrue(all(n.startswith("mimir/") for n in self.names), self.names)

    def test_bundle_carries_every_skill_file_and_no_cache(self):
        expected = {f"mimir/{p.relative_to(bs.SKILL_DIR).as_posix()}" for p in bs.bundle_files()}
        self.assertEqual(set(self.names), expected)
        self.assertIn("mimir/wizard/hosted.md", self.names)
        self.assertIn("mimir/scripts/build_vault.py", self.names)
        self.assertFalse([n for n in self.names if "__pycache__" in n or n.endswith(".DS_Store")])

    def test_only_the_description_differs_from_the_repo(self):
        repo_head, repo_body = split_frontmatter((bs.SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"))
        head, body = split_frontmatter(self.skill_md)
        self.assertEqual(body, repo_body)
        self.assertRegex(head, r"(?m)^name: mimir$")
        self.assertIn("description: " + '"' + bs.SHORT_DESCRIPTION + '"', head)
        self.assertEqual(head.count("description:"), 1)
        for key in ("license:", "metadata:"):
            self.assertIn(key, head)
        self.assertLess(len(head), len(repo_head))

    @unittest.skipIf(yaml is None, "PyYAML not installed")
    def test_bundled_frontmatter_parses(self):
        head, _ = split_frontmatter(self.skill_md)
        data = yaml.safe_load(head)
        self.assertEqual(data["name"], "mimir")
        self.assertEqual(data["description"], bs.SHORT_DESCRIPTION)

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
