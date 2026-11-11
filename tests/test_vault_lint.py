"""Behaviour of skills/mimir/scripts/vault_lint.py, and the digest contract.

The weekly review ("przegląd tygodnia") starts from this report, so its
numbers have to be right: stale notes, orphans, broken links, one-sided maps,
the inbox count, open contradictions.

The digest ("przetraw") is done by a model, which a unit test cannot run. What
a test CAN pin is the contract a digest is graded against: a fixture vault
gets three sources, one of them contradicting another, and a hand-written
reference digest. `check_digest` must pass it, and must catch each way a
model could break the rules (rewriting a human note, editing a source,
an assistant note with no sources, a source that vanished, a silent log).
The same grader works on a vault a live model digested:

    python3 vault_lint.py VAULT --snapshot before.json
    ... run "przetraw inbox" in VAULT ...
    python3 vault_lint.py VAULT --check-digest before.json

Run: python3 -m unittest discover -s tests -v
"""
import datetime as dt
import importlib.util
import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "mimir" / "scripts"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vl = _load("vault_lint")
bv = _load("build_vault")

from test_build_vault import make_profile  # noqa: E402  (same folder, run via discover)

TODAY = dt.date(2026, 11, 11)


def write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def note(title, body, **fm):
    head = {"title": title, "status": "active", "tags": "[test]", "horizon": "quarter",
            "created": "2026-11-01", "updated": "2026-11-01"}
    head.update(fm)
    lines = ["---"] + [f"{k}: {v}" for k, v in head.items()] + ["---", "", f"# {title}", "", body]
    return "\n".join(lines) + "\n"


# Three sources for Ola: two on learning a language that disagree, one on
# pricing illustration work.
SOURCES = {
    "inbox/artykul-powtorki.md": (
        "# Fiszki codziennie\n\nAutor twierdzi, że codzienne powtórki rozłożone w czasie "
        "to najskuteczniejszy sposób nauki słówek.\n"
    ),
    "inbox/wywiad-zanurzenie.md": (
        "# Wywiad: zanurzenie\n\nRozmówczyni twierdzi, że fiszki są stratą czasu, a liczy się "
        "wyłącznie kontakt z żywym językiem.\n"
    ),
    "inbox/podcast-wycena.md": (
        "# Podcast o wycenie\n\nIlustratorzy powinni wyceniać licencję, nie godziny pracy.\n"
    ),
}


def reference_digest(vault):
    """What a correct "przetraw inbox" leaves behind, written by hand."""
    for rel in SOURCES:
        src = vault / rel
        dest = vault / "library" / "zrodla" / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))

    write(vault, "library/powtorki-rozlozone.md", note(
        "Powtórki rozłożone w czasie",
        "Codzienne krótkie powtórki utrwalają słówka ([[artykul-powtorki]]).\n\n"
        "> [!warning] Sprzeczność\n"
        "> [[artykul-powtorki]] zaleca fiszki codziennie, a [[wywiad-zanurzenie]] uważa je\n"
        "> za stratę czasu. Rozstrzygnij, co działa u Ciebie przy [[wloski]].\n",
        horizon="evergreen", author="assistant",
        sources='["[[artykul-powtorki]]", "[[wywiad-zanurzenie]]"]',
    ))
    write(vault, "library/wycena-ilustracji.md", note(
        "Wycena ilustracji",
        "Wyceniaj licencję, nie godziny ([[podcast-wycena]]). Dotyczy [[okladka-wydawnictwo]].\n",
        horizon="evergreen", author="assistant", moc='"[[home]]"',
        sources='["[[podcast-wycena]]"]',
    ))

    # the human notes only gain a footer
    for rel, link in (("self/wloski.md", "powtorki-rozlozone"),
                      ("work/zlecenia/okladka-wydawnictwo.md", "wycena-ilustracji")):
        p = vault / rel
        p.write_text(p.read_text(encoding="utf-8").rstrip("\n")
                     + f"\n\n## Zobacz też\n\n- [[{link}]]\n", encoding="utf-8")

    # the map gains a line, both ends at once
    home = vault / "moc" / "home.md"
    home.write_text(home.read_text(encoding="utf-8").replace(
        "## Foldery systemowe",
        "- **`library/`**\n  - [[wycena-ilustracji]] — Wycena ilustracji\n\n## Foldery systemowe"),
        encoding="utf-8")

    write(vault, "moc/dziennik-zmian.md", note(
        "Dziennik zmian",
        "- [2026-11-11] przetrawione: [[artykul-powtorki]], [[wywiad-zanurzenie]] → nowe: "
        "[[powtorki-rozlozone]]; flagi: sprzeczność fiszki vs zanurzenie\n"
        "- [2026-11-11] przetrawione: [[podcast-wycena]] → nowe: [[wycena-ilustracji]]; "
        "zmienione: [[okladka-wydawnictwo]] (zobacz też)\n",
        type="log", horizon="evergreen", author="assistant",
    ))


class _VaultCase(unittest.TestCase):
    def setUp(self):
        os.environ["MIMIR_NO_OPEN"] = "1"
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.vault = self.tmp / "drugi-mozg"

    def tearDown(self):
        self._tmp.cleanup()

    def build(self, **overrides):
        path = self.tmp / "profile.json"
        path.write_text(json.dumps(make_profile(self.vault, **overrides), ensure_ascii=False),
                        encoding="utf-8")
        bv.build(bv.load_profile(path))

    def lint(self, days=14, today=TODAY):
        return vl.lint(self.vault, today, days)


class DigestContractTest(_VaultCase):
    def setUp(self):
        super().setUp()
        self.build()
        for rel, text in SOURCES.items():
            write(self.vault, rel, text)
        self.before = vl.snapshot(self.vault)

    def test_reference_digest_passes(self):
        reference_digest(self.vault)
        self.assertEqual(vl.check_digest(self.vault, self.before), [])

    def test_reference_digest_lints_clean(self):
        reference_digest(self.vault)
        report = self.lint()
        self.assertEqual(report["broken_links"], [])
        self.assertEqual(report["one_sided_moc"], [])
        self.assertEqual(report["sources_digested"], 3)
        self.assertEqual(report["inbox"]["files"], ["inbox/welcome.md"])

    def test_contradiction_is_flagged_and_links_both_sides(self):
        reference_digest(self.vault)
        warnings = self.lint()["warnings"]
        self.assertEqual([w["path"] for w in warnings], ["library/powtorki-rozlozone.md"])
        text = (self.vault / "library/powtorki-rozlozone.md").read_text(encoding="utf-8")
        callout = [ln for ln in text.split("> [!warning]", 1)[1].splitlines() if ln.startswith(">")]
        linked = {vl.link_target(m.group(1)) for ln in callout for m in vl.WIKILINK_RE.finditer(ln)}
        self.assertTrue({"artykul-powtorki", "wywiad-zanurzenie"} <= linked, linked)

    def test_human_notes_keep_every_original_byte(self):
        originals = {rel: self.before["notes"][rel]
                     for rel in ("self/wloski.md", "work/zlecenia/okladka-wydawnictwo.md")}
        reference_digest(self.vault)
        for rel, old in originals.items():
            new = (self.vault / rel).read_text(encoding="utf-8")
            self.assertTrue(new.startswith(old.rstrip("\n")), rel)

    def test_rewriting_a_human_note_is_caught(self):
        reference_digest(self.vault)
        p = self.vault / "self/wloski.md"
        p.write_text(p.read_text(encoding="utf-8").replace("A2 do wiosny.", "B1 do wiosny."),
                     encoding="utf-8")
        problems = vl.check_digest(self.vault, self.before)
        self.assertTrue(any("self/wloski.md" in x and "rewritten" in x for x in problems), problems)

    def test_appending_prose_to_a_human_note_is_caught(self):
        reference_digest(self.vault)
        with open(self.vault / "self/wloski.md", "a", encoding="utf-8") as f:
            f.write("\nDopisek asystenta: lepiej zmień plan.\n")
        problems = vl.check_digest(self.vault, self.before)
        self.assertTrue(any("self/wloski.md" in x for x in problems), problems)

    def test_editing_a_digested_source_is_caught(self):
        reference_digest(self.vault)
        before = vl.snapshot(self.vault)
        with open(self.vault / "library/zrodla/podcast-wycena.md", "a", encoding="utf-8") as f:
            f.write("\npoprawka\n")
        problems = vl.check_digest(self.vault, before)
        self.assertTrue(any("read-only" in x for x in problems), problems)

    def test_source_changed_on_the_way_is_caught(self):
        reference_digest(self.vault)
        p = self.vault / "library/zrodla/podcast-wycena.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nstreszczenie\n", encoding="utf-8")
        problems = vl.check_digest(self.vault, self.before)
        self.assertTrue(any("inbox/podcast-wycena.md" in x for x in problems), problems)

    def test_assistant_note_without_sources_is_caught(self):
        reference_digest(self.vault)
        write(self.vault, "library/bez-zrodel.md",
              note("Bez źródeł", "Twierdzenie znikąd.", author="assistant"))
        problems = vl.check_digest(self.vault, self.before)
        self.assertTrue(any("bez-zrodel" in x and "sources" in x for x in problems), problems)

    def test_digest_without_a_log_entry_is_caught(self):
        reference_digest(self.vault)
        (self.vault / "moc/dziennik-zmian.md").unlink()
        problems = vl.check_digest(self.vault, self.before)
        self.assertTrue(any("dziennik-zmian" in x for x in problems), problems)

    def test_rewriting_a_map_line_is_caught(self):
        reference_digest(self.vault)
        home = self.vault / "moc/home.md"
        home.write_text(home.read_text(encoding="utf-8").replace("Mapa domowa", "Mapa"),
                        encoding="utf-8")
        problems = vl.check_digest(self.vault, self.before)
        self.assertTrue(any("moc/home.md" in x for x in problems), problems)

    def test_cli_grades_a_digest(self):
        snap = self.tmp / "before.json"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(vl.main([str(self.vault), "--snapshot", str(snap)]), 0)
        reference_digest(self.vault)
        out = io.StringIO()
        with redirect_stdout(out):
            code = vl.main([str(self.vault), "--check-digest", str(snap), "--json"])
        self.assertEqual(code, 0, out.getvalue())
        self.assertEqual(json.loads(out.getvalue()), {"violations": []})


class LintTest(_VaultCase):
    def test_fresh_vault_has_no_broken_links_or_one_sided_maps(self):
        for lang in ("pl", "en"):
            with self.subTest(lang):
                shutil.rmtree(self.vault, ignore_errors=True)
                self.build(language=lang)
                report = self.lint()
                self.assertEqual(report["broken_links"], [])
                self.assertEqual(report["one_sided_moc"], [])
                self.assertEqual(report["warnings"], [])

    def test_stale_active_notes_after_the_threshold(self):
        self.build()
        report = self.lint(today=TODAY + dt.timedelta(days=30))
        stale = {s["path"] for s in report["stale"]}
        self.assertIn("work/zlecenia/okladka-wydawnictwo.md", stale)
        self.assertNotIn("moc/home.md", stale, "evergreen never goes stale")
        self.assertNotIn("context/me.md", stale)
        self.assertFalse(any(p.startswith("inbox/") for p in stale))
        self.assertEqual(self.lint()["stale"], [], "nothing is stale on build day")

    def test_threshold_is_configurable(self):
        self.build()
        later = TODAY + dt.timedelta(days=20)
        self.assertTrue(self.lint(today=later)["stale"])
        self.assertEqual(self.lint(days=30, today=later)["stale"], [])

    def test_orphans_are_block_notes_nothing_links_to(self):
        self.build()
        orphans = self.lint()["orphans"]
        self.assertIn("self/wloski.md", orphans)  # in_home_map: False in the profile
        self.assertNotIn("work/zlecenia/okladka-wydawnictwo.md", orphans)

    def test_broken_links_ignore_code(self):
        self.build()
        write(self.vault, "play/bieganie/plan.md", note(
            "Plan", "Zobacz [[nie-ma-takiej]] i [[okladka-wydawnictwo|okładka]], "
            "[[wloski#cele]], ![[zdjecie.png]].\n\n`[[w-kodzie]]`\n\n```\n[[w-bloku]]\n```\n"))
        write(self.vault, "attachments/zdjecie.png", "")
        broken = [b["target"] for b in self.lint()["broken_links"]]
        self.assertEqual(broken, ["nie-ma-takiej"])

    def test_one_sided_maps_both_directions(self):
        self.build()
        write(self.vault, "moc/bieganie.md", note("Bieganie", "- [[plan-treningowy]]\n"))
        write(self.vault, "play/bieganie/plan-treningowy.md", note("Plan treningowy", "Trzy razy w tygodniu."))
        write(self.vault, "play/bieganie/zawody.md", note("Zawody", "Wiosna.", moc='"[[bieganie]]"'))
        found = {(m["map"], m["note"]) for m in self.lint()["one_sided_moc"]}
        self.assertEqual(found, {
            ("moc/bieganie.md", "play/bieganie/plan-treningowy.md"),
            ("moc/bieganie.md", "play/bieganie/zawody.md"),
        })

    def test_change_log_is_not_a_map(self):
        self.build()
        write(self.vault, "moc/dziennik-zmian.md", note("Dziennik", "- [[okladka-wydawnictwo]]\n"))
        write(self.vault, "moc/historia.md", note("Historia", "- [[wloski]]\n", type="log"))
        self.assertEqual(self.lint()["one_sided_moc"], [])

    def test_inbox_counts_what_waits(self):
        self.build()
        write(self.vault, "inbox/link.md", "https://example.com\n")
        report = self.lint()
        self.assertEqual(report["inbox"]["count"], 2)  # welcome.md + link.md
        self.assertNotIn("inbox/sixpack-do-uzupelnienia.md", report["inbox"]["files"])

    def test_human_report_speaks_the_vault_language(self):
        self.build()
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(vl.main([str(self.vault), "--today", "2026-11-11"]), 0)
        self.assertIn("W inboxie czeka: 1", out.getvalue())

    def test_json_report_is_stable(self):
        self.build()
        out = io.StringIO()
        with redirect_stdout(out):
            vl.main([str(self.vault), "--json", "--today", "2026-11-11"])
        report = json.loads(out.getvalue())
        for key in ("inbox", "sources_digested", "stale", "orphans",
                    "broken_links", "one_sided_moc", "warnings"):
            self.assertIn(key, report)

    def test_missing_vault_exits_2(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(vl.main([str(self.tmp / "nie-ma")]), 2)


class PersonaCarriesTheProtocolTest(_VaultCase):
    def test_assistant_vault_gets_the_protocol_and_the_lint(self):
        self.build()
        persona = (self.vault / "CLAUDE.md").read_text(encoding="utf-8")
        for phrase in ("przetraw inbox", "author: assistant", "library/zrodla/",
                       "moc/dziennik-zmian.md", "[!warning]", "Zobacz też",
                       "przegląd tygodnia", ".mimir/vault_lint.py"):
            self.assertIn(phrase, persona)
        self.assertEqual((self.vault / ".mimir/vault_lint.py").read_bytes(),
                         (SCRIPTS / "vault_lint.py").read_bytes())

    def test_english_persona(self):
        self.build(language="en")
        persona = (self.vault / "AGENTS.md").read_text(encoding="utf-8")
        for phrase in ("digest my inbox", "library/sources/", "moc/change-log.md", "weekly review"):
            self.assertIn(phrase, persona)

    def test_vault_only_gets_neither(self):
        self.build(scope="vault", assistant_name=None)
        self.assertFalse((self.vault / ".mimir/vault_lint.py").exists())
        self.assertFalse((self.vault / "CLAUDE.md").exists())


if __name__ == "__main__":
    unittest.main()
