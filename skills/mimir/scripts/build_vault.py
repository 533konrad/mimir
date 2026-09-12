#!/usr/bin/env python3
"""Build a SIXPACK vault from a profile the wizard collected.

The wizard talks to the user and writes `profile.json`. This script turns
that profile into folders and files. The split is deliberate: a conversation
needs a model, a folder tree does not, and every structural rule that used to
live in prose (two-way MOC links, frontmatter keys, kebab-case filenames, one
README, people never nested, the credit line exactly once) is enforced here
instead of being re-derived on every run.

Two guarantees, both load-bearing:

* **Create-if-missing.** An existing file is never rewritten. Run the script
  twice on the same folder and the second run only fills gaps. The one
  exception is `.mimir/state.md`, regenerated every time by design.
* **Two-way MOC links by construction.** `moc/home.md` links exactly the
  notes that declare `moc: "[[home]]"`, because both ends come from the same
  list. A one-way link is not possible here.

Usage:
    python3 build_vault.py profile.json                 # build
    python3 build_vault.py profile.json --dry-run       # print the tree, touch nothing
    python3 build_vault.py profile.json --print-schema  # what the profile must contain

Stdlib only, Python 3.8+. Writes nothing outside the vault path in the profile.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import unicodedata
from pathlib import Path

SYSTEM_FOLDERS = ["inbox", "moc", "archive"]
BLOCKS = ["work", "public", "self", "people", "play", "library"]
VALID_STATUS = {"active", "someday", "archive"}
VALID_HORIZON = {"now", "quarter", "year", "someday", "evergreen"}

SCHEMA = """profile.json — what the wizard must collect before calling this script

{
  "language": "pl",                  // pl | en. Drives every generated word.
  "name": "Anna Kowalczyk",          // how the user calls themselves
  "does": "HR Business Partner ...", // one line, from the interview
  "vault_path": "~/Documents/second-brain",
  "scope": "vault+assistant",        // vault | vault+assistant
  "assistant_name": "Sowa",          // null when scope is "vault"
  "people_initials": true,           // people/ notes use initials only
  "capture_today": "telefon i karteczki",   // what the inbox replaces
  "scores": {"work":5,"public":2,"self":4,"people":5,"play":3,"library":4},
  "wants_low_blocks": false,         // keep folders for blocks scored 1-2?
  "subfolders": {"work": ["rekrutacje","onboarding"], "self": ["cele"]},
  "notes": [                         // the seeds. Bodies come from the model.
    {
      "path": "work/rekrutacje/rekrutacja-produkcja-q4.md",
      "title": "Rekrutacja produkcja Q4",
      "tags": ["praca","rekrutacje"],
      "status": "active",            // active | someday | archive
      "horizon": "quarter",          // now | quarter | year | someday | evergreen
      "in_home_map": true,           // gets moc: "[[home]]" AND a line in moc/home.md
      "body": "Trzy stanowiska do konca wrzesnia. Gotowe = podpisane umowy."
    }
  ],
  "open_questions": ["Jakie masz cele na ten rok?"],   // seeds the inbox checklist
  "storage": "local",                // local | github | drive | null
  "first_catch": {                   // optional, from step 6
    "path": "library/artykuly/czterodniowy-tydzien.md",
    "title": "Artykul o czterodniowym tygodniu pracy",
    "tags": ["library"], "status": "active", "horizon": "now",
    "in_home_map": false, "body": "Do przeczytania w weekend."
  }
}

Only "language", "name", "vault_path", "scope" and "scores" are required.
Everything else has a sane default, so a thin interview still produces a
working vault."""

# ---------------------------------------------------------------- text blocks

T = {
    "pl": {
        "block_q": {
            "work": "z czego żyję?",
            "public": "co daję światu?",
            "self": "kim się staję?",
            "people": "z kim żyję?",
            "play": "co mnie cieszy?",
            "library": "co zbieram od innych?",
        },
        "sys_q": {
            "inbox": "wszystko ląduje tu najpierw, bez zastanawiania się",
            "moc": "mapy treści: tematy, które nie mieszczą się w jednym folderze",
            "archive": "skończone i nieaktualne. Nic nie kasujemy, przenosimy",
        },
        "home_title": "Mapa domowa",
        "home_intro": "Drzwi wejściowe do Twojego drugiego mózgu. Nie wiesz, gdzie zacząć? Zacznij tu.",
        "home_blocks": "## Twoje klocki",
        "home_system": "## Foldery systemowe",
        "home_moc_what": """## Czym jest mapa treści

Temat rzadko mieszka w jednym folderze. Mapa to jedyne miejsce, które widzi
całość. Kiedy jakiś temat rozłazi Ci się na trzy foldery, załóż dla niego
mapę tutaj.

**Zasada dwustronna:** dopisujesz notatkę do mapy, notatka dostaje
`moc: "[[home]]"` we frontmatterze. Zawsze oba końce naraz, inaczej mapa po
cichu gnije.""",
        "welcome_title": "Zacznij tutaj",
        "welcome_body": """To jest Twój inbox. Wszystko, co dziś ląduje w {capture}, od teraz wrzucasz
tutaj: link, myśl, pomysł, zadanie. Bez zastanawiania się, gdzie to powinno
trafić. Decydowanie w momencie zapisu jest kosztowne i to ono sprawia, że
ludzie przestają notować.

Raz w tygodniu, kwadrans: otwórz swoje AI w tym folderze i powiedz
„przejrzyjmy inbox". Przejdziecie przez to, co się nazbierało, i rozłożycie
do klocków.

Ta notatka jest po to, żeby ją skasować. Niech to będzie Twój pierwszy
przegląd inboxa.""",
        "fill_title": "Sixpack do uzupełnienia",
        "fill_intro": """Twój drugi mózg dopyta Cię o te rzeczy po jednym pytaniu na raz, podczas
cotygodniowych przeglądów. Możesz też odpowiedzieć tu, kiedy chcesz.""",
        "fill_empty": "Nic nie zostało. Wywiad objął wszystko, co potrzebne.",
        "readme_title": "Twój drugi mózg",
        "readme_whose": "Drugi mózg: **{name}**. Zbudowany {date}.",
        "readme_struct": "## Struktura: SIXPACK",
        "readme_struct_intro": """Sześć klocków życia plus trzy foldery systemowe. Folder mówi, O CZYM jest
notatka. Frontmatter mówi, co z nią teraz zrobić.""",
        "readme_bounds": """## Gdzie to wrzucić

Cztery pytania rozstrzygają dziewięć na dziesięć przypadków:

- **Czy to zarabia?** Do `work/`. Oddawane za darmo, żeby budować markę
  (podcast, darmowe treści)? Do `public/`, nawet jeśli to produkt.
- **Treść czy kontrakt?** Sam odcinek, post, wystąpienie do `public/`. Umowa,
  faktura, klient do `work/`.
- **Refleksja czy praktyka?** „Czego nauczyło mnie nurkowanie o spokoju" do
  `self/`. „Parametry powietrza na 40 metrach" do `play/`.
- **Cudze czy moje?** Zebrane od innych do `library/`. Wymyślone przeze mnie
  do klocka tematycznego.""",
        "readme_fm": """## Frontmatter

Każda notatka zaczyna się tak:

```yaml
---
title: Tytuł po ludzku
status: active        # active | someday | archive
tags: [krótkie, małą literą]
horizon: quarter      # now | quarter | year | someday | evergreen
created: 2026-01-01
updated: 2026-01-01
moc: "[[home]]"       # tylko jeśli notatka jest na mapie
---
```

To dzięki temu vault jest czytelny dla maszyny: Twoje AI odpowie na pytanie
„co mam aktywnego na ten kwartał?", nie czytając każdej notatki po kolei.""",
        "readme_moc": """## Mapy treści

Mapy mieszkają w `moc/`, zaczynasz od `moc/home.md`. Zasada dwustronna: mapa
linkuje notatkę, notatka ma `moc: "[[nazwa-mapy]]"` we frontmatterze. Zawsze
oba końce naraz.""",
        "readme_rhythm": """## Rytm

**Codziennie:** wszystko do `inbox/`, bez sortowania w locie.
**Raz w tygodniu, kwadrans:** otwórz AI w tym folderze i powiedz
„przejrzyjmy inbox". Skończone i nieaktualne idzie do `archive/`. Nic nie
kasujemy.""",
        "readme_rules": """## Zasady

- Zwykłe pliki tekstowe wygrywają z zamkniętymi aplikacjami: przeniesiesz je
  gdziekolwiek, otworzysz za dwadzieścia lat, przeczyta je każde AI.
- Nazwy klocków po angielsku (krótkie i przenośne), treść po Twojemu.
- Hasła trzymaj w menedżerze haseł, nie tutaj.""",
        "readme_people": "- Notatki o osobach w `people/` prowadzisz **tylko na inicjałach**. Vaulty bywają synchronizowane i wyciekają.",
        "credit": "Mimir zbudował Konrad Gładkowski → konradgladkowski.com",
        "assistant_hdr": "# {assistant}",
        "me_title": "Kim jestem",
        "goals_title": "Cele",
        "goals_body": "Zapisz tu, co ma być inaczej za rok. Twój asystent przypomni o tym na początku kwartału.",
        "log_title": "Dziennik decyzji",
        "log_intro": """Tylko dopisywanie, najnowsze na dole. Format:
`[RRRR-MM-DD] DECYZJA: ... | POWÓD: ... | KONTEKST: ...`""",
        "log_first": "[{date}] DECYZJA: Buduję drugi mózg (Mimir, struktura SIXPACK){assistant_part}. | POWÓD: {why} | KONTEKST: Folder: {path}. Przechowywanie: {storage}.",
        "why_default": "Notatki i pomysły rozłażą się po różnych miejscach.",
    },
    "en": {
        "block_q": {
            "work": "what pays for my life?",
            "public": "what do I give the world?",
            "self": "who am I becoming?",
            "people": "who do I share life with?",
            "play": "what makes me happy?",
            "library": "what do I collect from others?",
        },
        "sys_q": {
            "inbox": "everything lands here first, with no thinking",
            "moc": "maps of content: topics too big for a single folder",
            "archive": "done and dead. Nothing gets deleted, it moves here",
        },
        "home_title": "Home map",
        "home_intro": "The front door to your second brain. Not sure where to start? Start here.",
        "home_blocks": "## Your blocks",
        "home_system": "## System folders",
        "home_moc_what": """## What a map of content is

A topic rarely lives in one folder. A map is the one place that sees all of
it. When a topic spreads across three folders, give it a map here.

**The two-way rule:** you add a note to a map, the note gets
`moc: "[[home]]"` in its frontmatter. Both ends, always, at the same time.
A one-way link is how a map quietly rots.""",
        "welcome_title": "Start here",
        "welcome_body": """This is your inbox. Everything that today lands in {capture} goes here
instead: a link, a thought, an idea, a task. No deciding where it belongs.
Deciding at the moment of capture is the expensive part, and it is why people
stop capturing.

Once a week, fifteen minutes: open your AI in this folder and say "let's
review my inbox". You go through what piled up and file it into the blocks.

This note exists to be deleted. Let that be your first inbox review.""",
        "fill_title": "Sixpack still to fill in",
        "fill_intro": """Your second brain will ask you about these one question at a time, during
the weekly reviews. You can also answer them here whenever you like.""",
        "fill_empty": "Nothing left. The interview covered everything it needed.",
        "readme_title": "Your second brain",
        "readme_whose": "Second brain: **{name}**. Built {date}.",
        "readme_struct": "## Structure: SIXPACK",
        "readme_struct_intro": """Six blocks of life plus three system folders. The folder says what a note is
ABOUT. The frontmatter says what to do with it now.""",
        "readme_bounds": """## Where does this go

Four questions settle nine cases out of ten:

- **Does it earn money?** Into `work/`. Given away to build the brand (a
  podcast, free content)? Into `public/`, even when it is a product.
- **Content or contract?** The episode, post or talk goes to `public/`. The
  deal, the invoice, the client go to `work/`.
- **Reflection or practice?** "What diving taught me about staying calm" goes
  to `self/`. "Air parameters at 40 metres" goes to `play/`.
- **Someone else's or mine?** Collected from others goes to `library/`. Made
  by me goes to its topic block.""",
        "readme_fm": """## Frontmatter

Every note starts like this:

```yaml
---
title: A human-readable title
status: active        # active | someday | archive
tags: [short, lowercase]
horizon: quarter      # now | quarter | year | someday | evergreen
created: 2026-01-01
updated: 2026-01-01
moc: "[[home]]"       # only when the note sits on a map
---
```

This is what makes the vault machine-readable: your AI can answer "what is
active this quarter?" without reading every note.""",
        "readme_moc": """## Maps of content

Maps live in `moc/`, and you start at `moc/home.md`. The two-way rule: a map
links a note, the note carries `moc: "[[map-name]]"` in its frontmatter. Both
ends, always, at the same time.""",
        "readme_rhythm": """## The rhythm

**Daily:** everything into `inbox/`, no sorting in the moment.
**Once a week, fifteen minutes:** open your AI in this folder and say "let's
review my inbox". Finished and stale things move to `archive/`. Nothing is
ever deleted.""",
        "readme_rules": """## House rules

- Plain text files beat closed apps: you can move them anywhere, open them in
  twenty years, and any AI can read them.
- Block names stay English (short and portable), the content is yours.
- Keep passwords in a password manager, not here.""",
        "readme_people": "- Notes about people in `people/` use **initials only**. Vaults get synced, and synced things leak.",
        "credit": "Mimir was built by Konrad Gładkowski → konradgladkowski.com",
        "assistant_hdr": "# {assistant}",
        "me_title": "Who I am",
        "goals_title": "Goals",
        "goals_body": "Write down what should be different a year from now. Your assistant will bring it up at the start of each quarter.",
        "log_title": "Decision log",
        "log_intro": """Append only, newest at the bottom. Format:
`[YYYY-MM-DD] DECISION: ... | REASONING: ... | CONTEXT: ...`""",
        "log_first": "[{date}] DECISION: Building a second brain (Mimir, SIXPACK structure){assistant_part}. | REASONING: {why} | CONTEXT: Folder: {path}. Storage: {storage}.",
        "why_default": "Notes and ideas were scattered across too many places.",
    },
}

# ---------------------------------------------------------------- helpers


class BuildError(Exception):
    pass


def slugify(text: str) -> str:
    """Kebab-case, diacritics folded. Wikilinks resolve by filename, so this
    has to be stable and collision-free across the vault."""
    text = text.replace("ł", "l").replace("Ł", "L")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "notatka"


def today() -> str:
    return _dt.date.today().isoformat()


def frontmatter(note: dict, created: str) -> str:
    tags = note.get("tags") or []
    lines = [
        "---",
        f"title: {note['title']}",
        f"status: {note.get('status', 'active')}",
        "tags: [" + ", ".join(tags) + "]",
        f"horizon: {note.get('horizon', 'quarter')}",
        f"created: {created}",
        f"updated: {created}",
    ]
    if note.get("in_home_map"):
        lines.append('moc: "[[home]]"')
    lines.append("---")
    return "\n".join(lines)


class Vault:
    """Writes only what is missing, and remembers what it did."""

    def __init__(self, root: Path, dry_run: bool = False):
        self.root = root
        self.dry_run = dry_run
        self.created: list[str] = []
        self.skipped: list[str] = []

    def _rel(self, path: Path) -> str:
        return str(path.relative_to(self.root))

    def folder(self, rel: str) -> Path:
        p = self.root / rel
        if not p.is_dir() and not self.dry_run:
            p.mkdir(parents=True, exist_ok=True)
        if not (self.root / rel).exists() or self.dry_run:
            self.created.append(rel + "/")
        return p

    def write(self, rel: str, content: str) -> None:
        """Create-if-missing. An existing file is left byte-identical."""
        p = self.root / rel
        if p.exists():
            self.skipped.append(rel)
            return
        if not self.dry_run:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content.rstrip() + "\n", encoding="utf-8")
        self.created.append(rel)

    def overwrite(self, rel: str, content: str) -> None:
        """Only `.mimir/state.md` uses this: it is the one file Mimir owns."""
        p = self.root / rel
        if not self.dry_run:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content.rstrip() + "\n", encoding="utf-8")
        self.created.append(rel + " (marker)")


# ---------------------------------------------------------------- validation


def load_profile(path: Path) -> dict:
    try:
        p = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise BuildError(f"profile.json is not valid JSON: {e}")

    for key in ("language", "name", "vault_path", "scope", "scores"):
        if not p.get(key):
            raise BuildError(f"profile.json is missing a required field: {key}")
    if p["language"] not in T:
        raise BuildError(f"language must be one of {sorted(T)}, got {p['language']!r}")
    if p["scope"] not in ("vault", "vault+assistant"):
        raise BuildError("scope must be 'vault' or 'vault+assistant'")
    if p["scope"] == "vault+assistant" and not p.get("assistant_name"):
        raise BuildError("scope is 'vault+assistant' but assistant_name is empty")

    missing = [b for b in BLOCKS if b not in p["scores"]]
    if missing:
        raise BuildError(f"scores is missing blocks: {', '.join(missing)}")
    for b, s in p["scores"].items():
        if b not in BLOCKS:
            raise BuildError(f"unknown block in scores: {b}")
        if not isinstance(s, int) or not 1 <= s <= 5:
            raise BuildError(f"score for {b} must be an integer 1-5, got {s!r}")

    seen = {}
    for n in p.get("notes", []):
        for key in ("path", "title", "body"):
            if not n.get(key):
                raise BuildError(f"a note is missing '{key}': {n.get('path') or n}")
        if not n["path"].endswith(".md"):
            raise BuildError(f"note path must end with .md: {n['path']}")
        if n.get("status", "active") not in VALID_STATUS:
            raise BuildError(f"{n['path']}: status must be one of {sorted(VALID_STATUS)}")
        if n.get("horizon", "quarter") not in VALID_HORIZON:
            raise BuildError(f"{n['path']}: horizon must be one of {sorted(VALID_HORIZON)}")
        stem = Path(n["path"]).stem
        if stem != slugify(stem):
            raise BuildError(f"filename must be kebab-case: {n['path']} (try {slugify(stem)}.md)")
        if stem in seen:
            raise BuildError(f"duplicate filename {stem}.md: wikilinks resolve by name "
                             f"({seen[stem]} and {n['path']})")
        seen[stem] = n["path"]
        block = n["path"].split("/")[0]
        if block not in BLOCKS + SYSTEM_FOLDERS:
            raise BuildError(f"note sits outside the SIXPACK tree: {n['path']}")
    return p


def folders_for(profile: dict) -> dict:
    """Which block folders exist, and with which subfolders.

    Sizing rules from vault-spec: 4-5 gets subfolders, 3 is flat, 1-2 exists
    only when the user asked for it. `people/` is the exception: it exists by
    the same score rule but never gets subfolders, because a folder tree of
    named people is the opposite of the privacy rule.
    """
    out = {}
    subs = profile.get("subfolders") or {}
    for block, score in profile["scores"].items():
        if score <= 2 and not profile.get("wants_low_blocks"):
            continue
        if block == "people":
            out[block] = []
            continue
        out[block] = [slugify(s) for s in subs.get(block, [])] if score >= 4 else []
    return out


# ---------------------------------------------------------------- generation


def gen_home(profile: dict, tree: dict, notes: list) -> str:
    t = T[profile["language"]]
    mapped = [n for n in notes if n.get("in_home_map")]
    by_block = {}
    for n in mapped:
        by_block.setdefault(n["path"].split("/")[0], []).append(n)

    out = [
        frontmatter(
            {"title": t["home_title"], "tags": ["moc"], "status": "active", "horizon": "evergreen"},
            today(),
        ),
        "",
        f"# {t['home_title']}",
        "",
        t["home_intro"],
        "",
        t["home_blocks"],
        "",
    ]
    for block, subs in tree.items():
        line = f"- **`{block}/`** — {t['block_q'][block]}"
        if subs:
            line += "  \n  " + " · ".join(f"`{block}/{s}/`" for s in subs)
        out.append(line)
        for n in by_block.get(block, []):
            out.append(f"  - [[{Path(n['path']).stem}]] — {n['title']}")
    out += ["", t["home_system"], ""]
    for f in SYSTEM_FOLDERS:
        out.append(f"- **`{f}/`** — {t['sys_q'][f]}")
    out += ["", t["home_moc_what"]]
    return "\n".join(out)


def gen_readme(profile: dict, tree: dict) -> str:
    t = T[profile["language"]]
    out = [
        f"# {t['readme_title']}",
        "",
        t["readme_whose"].format(name=profile["name"], date=today()),
        "",
        t["readme_struct"],
        "",
        t["readme_struct_intro"],
        "",
        "```",
    ]
    for f in SYSTEM_FOLDERS:
        out.append(f"{f + '/':<12} {t['sys_q'][f]}")
    out.append("")
    for block, subs in tree.items():
        out.append(f"{block + '/':<12} {t['block_q'][block]}")
        for s in subs:
            out.append(f"  {s}/")
    out += ["```", "", t["readme_bounds"], "", t["readme_fm"], "", t["readme_moc"], ""]
    rules = t["readme_rules"]
    if profile.get("people_initials") and "people" in tree:
        rules += "\n" + t["readme_people"]
    out += [rules, "", "---", "", t["credit"]]
    return "\n".join(out)


def gen_welcome(profile: dict) -> str:
    t = T[profile["language"]]
    capture = profile.get("capture_today") or ("głowie" if profile["language"] == "pl" else "your head")
    return "\n".join([
        frontmatter({"title": t["welcome_title"], "tags": ["inbox"], "status": "active",
                     "horizon": "now"}, today()),
        "",
        f"# {t['welcome_title']}",
        "",
        t["welcome_body"].format(capture=capture),
    ])


def gen_fill(profile: dict) -> str:
    t = T[profile["language"]]
    qs = profile.get("open_questions") or []
    body = "\n".join(f"- [ ] {q}" for q in qs) if qs else t["fill_empty"]
    return "\n".join([
        frontmatter({"title": t["fill_title"], "tags": ["inbox", "sixpack"], "status": "active",
                     "horizon": "someday"}, today()),
        "",
        f"# {t['fill_title']}",
        "",
        t["fill_intro"],
        "",
        body,
    ])


def gen_note(note: dict) -> str:
    return "\n".join([frontmatter(note, today()), "", f"# {note['title']}", "", note["body"].strip()])


def gen_assistant(profile: dict) -> str:
    t = T[profile["language"]]
    name = profile["assistant_name"]
    pl = profile["language"] == "pl"
    lines = [t["assistant_hdr"].format(assistant=name), ""]
    if pl:
        lines += [
            f"Masz na imię **{name}**. Jesteś osobistym asystentem, który zna tego",
            "człowieka i jego drugi mózg.",
            "",
            "## Na starcie każdej rozmowy",
            "",
            "Przeczytaj `context/me.md` i `context/goals.md`. To one mówią, z kim",
            "rozmawiasz i na czym mu teraz zależy.",
            "",
            "## Jak pracujesz",
            "",
            "- Nowa notatka zawsze z pełnym frontmatterem (wzór w `README.md`).",
            "- Notatka trafia na mapę, dostaje `moc: \"[[home]]\"`. Oba końce naraz.",
            "- Skończone i nieaktualne przenosisz do `archive/`. Nie kasujesz.",
            "- Ważne decyzje dopisujesz do `decisions/log.md`.",
        ]
        if profile.get("people_initials"):
            lines.append("- Notatki o osobach w `people/` tylko na inicjałach, nigdy pełne imiona.")
        lines += [
            "",
            "## Cotygodniowy przegląd",
            "",
            "Na hasło „przejrzyjmy inbox\" przechodzisz przez `inbox/`, proponujesz",
            "klocek i tagi, przenosisz po akceptacji. Na koniec zadajesz JEDNO",
            "pytanie z `inbox/sixpack-do-uzupelnienia.md`. Jedno, nie więcej: ten",
            "mózg wypełnia się tygodniami, nie w jednym przesłuchaniu.",
        ]
    else:
        lines += [
            f"Your name is **{name}**. You are a personal assistant who knows this",
            "person and their second brain.",
            "",
            "## At the start of every conversation",
            "",
            "Read `context/me.md` and `context/goals.md`. They tell you who you are",
            "talking to and what they care about right now.",
            "",
            "## How you work",
            "",
            "- Every new note carries full frontmatter (the shape is in `README.md`).",
            "- A note that goes on a map gets `moc: \"[[home]]\"`. Both ends at once.",
            "- Finished and stale things move to `archive/`. You never delete.",
            "- Important decisions get appended to `decisions/log.md`.",
        ]
        if profile.get("people_initials"):
            lines.append("- Notes about people in `people/` use initials only, never full names.")
        lines += [
            "",
            "## The weekly review",
            "",
            'On "let\'s review my inbox" you walk through `inbox/`, propose a block',
            "and tags, and move things once they agree. At the end you ask ONE",
            "question from `inbox/sixpack-do-uzupelnienia.md`. One, not more: this",
            "brain fills over weeks, not in a single interrogation.",
        ]
    return "\n".join(lines)


def gen_me(profile: dict) -> str:
    t = T[profile["language"]]
    pl = profile["language"] == "pl"
    hot = [b for b, s in profile["scores"].items() if s >= 4]
    lines = [
        frontmatter({"title": t["me_title"], "tags": ["kontekst" if pl else "context"],
                     "status": "active", "horizon": "evergreen"}, today()),
        "",
        f"# {t['me_title']}",
        "",
        f"- **{'Imię' if pl else 'Name'}:** {profile['name']}",
    ]
    if profile.get("does"):
        lines.append(f"- **{'Czym się zajmuję' if pl else 'What I do'}:** {profile['does']}")
    if hot:
        label = "Co jest dla mnie teraz ważne" if pl else "What matters to me now"
        lines.append(f"- **{label}:** " + ", ".join(f"`{b}/`" for b in hot))
    if profile.get("capture_today"):
        label = "Gdzie dotąd lądowały moje notatki" if pl else "Where my notes used to land"
        lines.append(f"- **{label}:** {profile['capture_today']}")
    lines += [
        "",
        ("Ten plik rośnie razem z Tobą. Dopisuj, gdy coś się zmieni."
         if pl else
         "This file grows with you. Add to it whenever something changes."),
    ]
    return "\n".join(lines)


def gen_goals(profile: dict) -> str:
    t = T[profile["language"]]
    return "\n".join([
        frontmatter({"title": t["goals_title"], "tags": ["cele" if profile["language"] == "pl" else "goals"],
                     "status": "active", "horizon": "year"}, today()),
        "",
        f"# {t['goals_title']}",
        "",
        t["goals_body"],
    ])


def gen_log(profile: dict) -> str:
    t = T[profile["language"]]
    assistant_part = ""
    if profile.get("assistant_name"):
        assistant_part = (f" z asystentem {profile['assistant_name']}"
                          if profile["language"] == "pl"
                          else f" with an assistant named {profile['assistant_name']}")
    first = t["log_first"].format(
        date=today(),
        assistant_part=assistant_part,
        why=profile.get("why") or t["why_default"],
        path=profile["vault_path"],
        storage=profile.get("storage") or "local",
    )
    return "\n".join([f"# {t['log_title']}", "", t["log_intro"], "", first])


def gen_marker(profile: dict, tree: dict, notes: list, step: int) -> str:
    subs = [f"{b}/{s}" for b, ss in tree.items() for s in ss]
    sixpack = " · ".join(f"{b} {s}" for b, s in profile["scores"].items())
    lines = [
        "---",
        "mimir_version: 2",
        f"status: {'complete' if step >= 9 else 'in-progress'}",
        f"step_completed: {step}",
        f"language: {profile['language']}",
        f"scope: {profile['scope']}",
        f"assistant_name: {profile.get('assistant_name') or '~'}",
        f"storage: {profile.get('storage') or '~'}",
        f"created: {today()}",
        f"updated: {today()}",
        "---",
        "# Profile summary (enough to resume without a second interview)",
        f"- name: {profile['name']}",
        f"- does: {profile.get('does') or '~'}",
        f"- sixpack: {sixpack}",
        f"- subfolders: {', '.join(subs) if subs else '~'}",
        f"- notes: {', '.join(Path(n['path']).stem for n in notes) if notes else '~'}",
        "- open questions: see inbox/sixpack-do-uzupelnienia.md",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------- build


def build(profile: dict, dry_run: bool = False) -> Vault:
    root = Path(profile["vault_path"]).expanduser()
    v = Vault(root, dry_run=dry_run)
    tree = folders_for(profile)
    notes = profile.get("notes") or []
    if profile.get("first_catch"):
        notes = notes + [profile["first_catch"]]

    for n in notes:
        block = n["path"].split("/")[0]
        if block in BLOCKS and block not in tree:
            raise BuildError(f"note {n['path']} sits in `{block}/`, which the quiz did not create")

    if not dry_run:
        root.mkdir(parents=True, exist_ok=True)

    # 0. marker first, so an interrupted build is always in a known state.
    # Written again at the end, once the tree it describes actually exists.
    v.overwrite(".mimir/state.md", gen_marker(profile, tree, notes, step=5))
    v.created.pop()

    # 1. structure
    for f in SYSTEM_FOLDERS:
        v.folder(f)
    for block, subs in tree.items():
        v.folder(block)
        for s in subs:
            v.folder(f"{block}/{s}")

    # 2. Obsidian starter config + README
    v.write(".obsidian/app.json", json.dumps({
        "newFileLocation": "folder",
        "newFileFolderPath": "inbox",
        "attachmentFolderPath": "attachments",
        "alwaysUpdateLinks": True,
        "useMarkdownLinks": True,
        "showUnsupportedFiles": True,
    }, indent=2))
    v.write(".obsidian/appearance.json", json.dumps({"accentColor": "#7c5cff"}, indent=2))
    v.write("README.md", gen_readme(profile, tree))

    # 3. the map, then 4. the inbox seeds
    v.write("moc/home.md", gen_home(profile, tree, notes))
    v.write("inbox/welcome.md", gen_welcome(profile))
    v.write("inbox/sixpack-do-uzupelnienia.md", gen_fill(profile))

    # 5. seeds from the interview
    for n in notes:
        v.write(n["path"], gen_note(n))

    # 6. assistant layer last, so a persona only exists on a complete vault
    if profile["scope"] == "vault+assistant":
        v.write("context/me.md", gen_me(profile))
        v.write("context/goals.md", gen_goals(profile))
        v.write("decisions/log.md", gen_log(profile))
        persona = gen_assistant(profile)
        v.write("CLAUDE.md", persona)
        v.write("AGENTS.md", persona)

    # keep empty folders alive in git
    if not dry_run:
        for d in [root / f for f in SYSTEM_FOLDERS] + [root / b for b in tree]:
            if d.is_dir() and not any(d.iterdir()):
                (d / ".gitkeep").write_text("", encoding="utf-8")

    v.overwrite(".mimir/state.md", gen_marker(profile, tree, notes, step=5))
    return v


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a SIXPACK vault from profile.json")
    ap.add_argument("profile", nargs="?", help="path to profile.json")
    ap.add_argument("--dry-run", action="store_true", help="print what would be written, touch nothing")
    ap.add_argument("--print-schema", action="store_true", help="print the profile schema and exit")
    args = ap.parse_args()

    if args.print_schema:
        print(SCHEMA)
        return 0
    if not args.profile:
        ap.error("profile.json is required (or use --print-schema)")

    try:
        profile = load_profile(Path(args.profile))
        v = build(profile, dry_run=args.dry_run)
    except BuildError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    head = "would create" if args.dry_run else "created"
    print(f"{head}: {len(v.created)}")
    for c in v.created:
        print(f"  + {c}")
    if v.skipped:
        print(f"left untouched (already there): {len(v.skipped)}")
        for s in v.skipped:
            print(f"  = {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
