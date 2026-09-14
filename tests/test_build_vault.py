"""Behaviour of skills/mimir/scripts/build_vault.py.

These pin the guarantees the wizard's red lines rely on: a rebuild never
rewrites an existing file, MOC links are two-way, people/ is never nested,
the quiz decides which blocks exist, and a bad profile is refused.

Run: python3 -m unittest discover -s tests -v
"""
import importlib.util
import json
import os
import re
import tempfile
import unittest
from pathlib import Path

try:  # optional: CI installs it for the YAML round-trip check
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "mimir" / "scripts" / "build_vault.py"

_spec = importlib.util.spec_from_file_location("build_vault", SCRIPT)
bv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bv)

STATE = ".mimir/state.md"


def make_profile(vault, **overrides):
    """Ola from evals/scenarios.md, sized so every sizing rule is exercised."""
    profile = {
        "language": "pl",
        "name": "Ola Testowa",
        "does": "ilustratorka freelance",
        "vault_path": str(vault),
        "scope": "vault+assistant",
        "assistant_name": "Bazyli",
        "people_initials": True,
        "capture_today": "telefon",
        "scores": {"work": 5, "public": 4, "self": 3, "people": 5, "play": 4, "library": 2},
        "subfolders": {"work": ["zlecenia", "klienci"], "people": ["rodzina"], "play": ["bieganie"]},
        "notes": [
            {"path": "work/zlecenia/okladka-wydawnictwo.md", "title": "Okładka dla wydawnictwa",
             "tags": ["praca"], "status": "active", "horizon": "quarter", "in_home_map": True,
             "body": "Termin koniec października."},
            {"path": "public/newsletter-ilustracja.md", "title": "Newsletter o ilustracji",
             "tags": ["newsletter"], "in_home_map": True, "body": "Co dwa tygodnie."},
            {"path": "self/wloski.md", "title": "Nauka włoskiego", "tags": ["nauka"],
             "horizon": "year", "in_home_map": False, "body": "A2 do wiosny."},
        ],
        "open_questions": ["Jakie masz cele na ten rok?"],
        "storage": "local",
    }
    profile.update(overrides)
    return profile


def snapshot(root, skip=(STATE,)):
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file() and p.relative_to(root).as_posix() not in skip
    }


def home_links(vault):
    """Wikilinks in the map's body. Inline code is prose explaining the rule."""
    text = (vault / "moc" / "home.md").read_text(encoding="utf-8")
    body = text.split("\n---\n", 1)[1]
    body = re.sub(r"`[^`]*`", "", body)
    return set(re.findall(r"\[\[([^\]|#]+)", body))


def notes_pointing_home(vault):
    """Notes whose FRONTMATTER declares the map, not files that mention it."""
    found = set()
    for p in vault.rglob("*.md"):
        text = p.read_text(encoding="utf-8")
        if p.stem != "home" and text.startswith("---\n"):
            head = text.split("\n---\n", 1)[0]
            if re.search(r'(?m)^moc: "\[\[home\]\]"$', head):
                found.add(p.stem)
    return found


class BuildVaultTest(unittest.TestCase):
    def setUp(self):
        os.environ["MIMIR_NO_OPEN"] = "1"
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.vault = self.tmp / "second-brain"

    def tearDown(self):
        self._tmp.cleanup()

    def build(self, profile, dry_run=False):
        path = self.tmp / "profile.json"
        path.write_text(json.dumps(profile, ensure_ascii=False), encoding="utf-8")
        return bv.build(bv.load_profile(path), dry_run=dry_run)

    # ------------------------------------------------ never overwrite

    def test_rebuild_leaves_every_file_byte_identical(self):
        self.build(make_profile(self.vault))
        before = snapshot(self.vault)
        self.build(make_profile(self.vault))
        self.assertEqual(before, snapshot(self.vault))

    def test_user_edits_and_user_files_survive_rebuild(self):
        self.build(make_profile(self.vault))
        (self.vault / "README.md").write_text("moja wersja\n", encoding="utf-8")
        with open(self.vault / "moc" / "home.md", "a", encoding="utf-8") as f:
            f.write("- moja linijka\n")
        (self.vault / "work" / "moja-notatka.md").write_text("tylko moje\n", encoding="utf-8")
        before = snapshot(self.vault)

        self.build(make_profile(self.vault))

        after = snapshot(self.vault)
        for rel in ("README.md", "moc/home.md", "work/moja-notatka.md"):
            self.assertEqual(before[rel], after[rel], rel)

    def test_existing_files_in_target_folder_untouched_on_first_build(self):
        (self.vault / "work").mkdir(parents=True)
        (self.vault / "README.md").write_text("stary README\n", encoding="utf-8")
        (self.vault / "work" / "stara-notatka.md").write_text("stara\n", encoding="utf-8")

        result = self.build(make_profile(self.vault))

        self.assertEqual((self.vault / "README.md").read_text(encoding="utf-8"), "stary README\n")
        self.assertEqual((self.vault / "work" / "stara-notatka.md").read_text(encoding="utf-8"), "stara\n")
        self.assertIn("README.md", result.skipped)

    def test_dry_run_writes_nothing(self):
        result = self.build(make_profile(self.vault), dry_run=True)
        self.assertFalse(self.vault.exists())
        self.assertTrue(result.created)

    # ------------------------------------------------ maps of content

    def test_moc_links_are_two_way(self):
        self.build(make_profile(self.vault))
        self.assertEqual(home_links(self.vault), notes_pointing_home(self.vault))
        self.assertEqual(home_links(self.vault), {"okladka-wydawnictwo", "newsletter-ilustracja"})

    def test_home_map_never_wikilinks_a_folder(self):
        self.build(make_profile(self.vault))
        folders = set(bv.BLOCKS) | set(bv.SYSTEM_FOLDERS)
        self.assertFalse(home_links(self.vault) & folders)

    def test_moc_stays_two_way_when_a_rebuild_adds_a_mapped_note(self):
        """Step 6 re-runs the build with first_catch. A catch with
        in_home_map=true gets moc: "[[home]]"; home.md already exists and
        is skipped by create-if-missing, so build() must append the link
        itself instead of silently leaving it one-way."""
        self.build(make_profile(self.vault))
        catch = {"path": "public/pomysl-na-odcinek.md", "title": "Pomysł na odcinek",
                 "tags": ["public"], "in_home_map": True, "body": "Do rozpisania."}
        self.build(make_profile(self.vault, first_catch=catch))
        self.assertTrue((self.vault / "public" / "pomysl-na-odcinek.md").is_file())
        self.assertEqual(home_links(self.vault), notes_pointing_home(self.vault))

    # ------------------------------------------------ sizing by quiz

    def test_people_never_gets_subfolders(self):
        self.build(make_profile(self.vault))
        people = self.vault / "people"
        self.assertTrue(people.is_dir())
        self.assertEqual([p for p in people.iterdir() if p.is_dir()], [])

    def test_high_score_gets_subfolders_and_score_3_stays_flat(self):
        self.build(make_profile(self.vault))
        self.assertTrue((self.vault / "work" / "zlecenia").is_dir())
        self.assertEqual([p for p in (self.vault / "self").iterdir() if p.is_dir()], [])

    def test_low_score_block_exists_only_when_asked(self):
        self.build(make_profile(self.vault))
        self.assertFalse((self.vault / "library").exists())

        other = self.tmp / "with-low"
        self.build(make_profile(other, wants_low_blocks=True))
        self.assertTrue((other / "library").is_dir())

    def test_note_in_a_declined_block_is_refused(self):
        note = {"path": "library/artykul.md", "title": "Artykuł", "body": "x"}
        with self.assertRaises(bv.BuildError):
            self.build(make_profile(self.vault, notes=[note]))
        self.assertFalse(self.vault.exists())

    # ------------------------------------------------ vault shape

    def test_exactly_one_readme_and_one_credit_line(self):
        self.build(make_profile(self.vault))
        self.assertEqual([p.relative_to(self.vault).as_posix() for p in self.vault.rglob("README.md")],
                         ["README.md"])
        credit = bv.T["pl"]["credit"]
        count = sum(p.read_text(encoding="utf-8").count(credit) for p in self.vault.rglob("*.md"))
        self.assertEqual(count, 1)

    def test_every_note_carries_the_frontmatter_keys(self):
        self.build(make_profile(self.vault))
        keys = ("title", "status", "tags", "horizon", "created", "updated")
        for folder in list(bv.BLOCKS) + ["inbox", "moc", "context"]:
            for note in (self.vault / folder).rglob("*.md") if (self.vault / folder).exists() else []:
                text = note.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"), note)
                head = text.split("\n---\n", 1)[0]
                for key in keys:
                    self.assertRegex(head, rf"(?m)^{key}: ", f"{note}: {key}")

    MUST_QUOTE = ["Rekrutacja: Q4 #pilne", "Sprint #3", "- lista", "2026", "3.5", "yes",
                  "No", "null", "~", "2026-09-14", '"Cytat" na start', "[szkic] okładka"]
    STAYS_PLAIN = ["Plan na 2027", "C# notatki", "100%", "Zwykły tytuł", "Okładka dla wydawnictwa"]

    def test_titles_stay_text_in_valid_yaml(self):
        """Titles are free text from the interview. Unquoted, `Rekrutacja: Q4`
        is invalid YAML, ` #` starts a comment, `- lista` opens a sequence,
        and `2026`, `yes` or `null` stop being text. Only those get quoted."""
        for title in self.MUST_QUOTE + self.STAYS_PLAIN:
            with self.subTest(title=title):
                line = bv.frontmatter({"title": title}, "2026-09-14").splitlines()[1]
                quoted = line.startswith('title: "')
                self.assertEqual(quoted, title in self.MUST_QUOTE, line)
                if yaml is not None:
                    self.assertEqual(yaml.safe_load(line), {"title": title}, line)

    def test_built_note_with_risky_title_has_valid_frontmatter(self):
        note = {"path": "work/rekrutacja-q4.md", "title": "Rekrutacja: Q4 #pilne",
                "in_home_map": False, "body": "x"}
        self.build(make_profile(self.vault, notes=[note]))
        text = (self.vault / "work" / "rekrutacja-q4.md").read_text(encoding="utf-8")
        self.assertIn('title: "Rekrutacja: Q4 #pilne"', text)
        if yaml is not None:
            head = text.split("\n---\n", 1)[0][len("---\n"):]
            self.assertEqual(yaml.safe_load(head)["title"], "Rekrutacja: Q4 #pilne")

    def test_assistant_entry_points_are_identical(self):
        self.build(make_profile(self.vault))
        self.assertEqual((self.vault / "CLAUDE.md").read_bytes(), (self.vault / "AGENTS.md").read_bytes())
        self.assertTrue((self.vault / "context" / "me.md").is_file())
        self.assertTrue((self.vault / "decisions" / "log.md").is_file())

    def test_vault_only_scope_has_no_assistant_layer(self):
        self.build(make_profile(self.vault, scope="vault", assistant_name=None))
        for rel in ("CLAUDE.md", "AGENTS.md", "context", "decisions"):
            self.assertFalse((self.vault / rel).exists(), rel)

    def test_state_marker_records_step_5(self):
        self.build(make_profile(self.vault))
        marker = (self.vault / STATE).read_text(encoding="utf-8")
        self.assertIn("step_completed: 5", marker)
        self.assertIn("status: in-progress", marker)

    def test_english_profile_builds_in_english(self):
        self.build(make_profile(self.vault, language="en", subfolders={}, notes=[]))
        self.assertIn("# Home map", (self.vault / "moc" / "home.md").read_text(encoding="utf-8"))

    # ------------------------------------------------ refusing bad profiles

    def test_bad_profiles_are_refused(self):
        note = {"path": "work/ok.md", "title": "Ok", "body": "x"}
        cases = {
            "filename not kebab-case": {"notes": [dict(note, path="work/Moja Notatka.md")]},
            "duplicate filename": {"notes": [note, dict(note, path="public/ok.md")]},
            "score out of range": {"scores": {"work": 6, "public": 4, "self": 3,
                                              "people": 5, "play": 4, "library": 2}},
            "block missing from scores": {"scores": {"work": 5}},
            "assistant without a name": {"assistant_name": None},
            "note outside the tree": {"notes": [dict(note, path="notatki/ok.md")]},
            "unknown status": {"notes": [dict(note, status="done")]},
            "unknown language": {"language": "de"},
        }
        for label, overrides in cases.items():
            with self.subTest(label):
                with self.assertRaises(bv.BuildError):
                    self.build(make_profile(self.vault, **overrides))


if __name__ == "__main__":
    unittest.main()
