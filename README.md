# 🧠 Mimir

**Twój second brain w 15 minut. Za darmo, po ludzku, z pomocą AI.**
*Your second brain in 15 minutes. Free, human-friendly, AI-guided.*

[🇵🇱 Polski](#-po-polsku) · [🇬🇧 English](#-in-english)

---

## 🇵🇱 Po polsku

Mimir to wizard, który rozmawia z Tobą przez ~10 minut i buduje Ci
**second brain** — jeden folder zwykłych plików tekstowych w strukturze
**SIXPACK**: sześć klocków życia, z których każdy odpowiada na jedno pytanie:

- 💼 **work** — z czego żyję?
- 📣 **public** — co daję światu?
- 🌱 **self** — kim się staję?
- 👥 **people** — z kim żyję?
- ⛵ **play** — co mnie cieszy?
- 📚 **library** — co zbieram od innych?

Do tego trzy foldery systemowe: 📥 **inbox** (wrzucasz bez zastanawiania),
🗺️ **moc** (mapy łączące tematy), 🗄️ **archive** (nic nie ginie).

Mimir nie przesłuchuje: wklejasz link do LinkedIna albo bloga, odpowiadasz
na sześć pytań ze skalą 1–5 — i **po kilku minutach patrzysz na swój second
brain z gotowymi notatkami o Tobie**. Resztę mózg dopyta sam, po jednym
pytaniu na raz.

Do tego, jeśli chcesz: **własny asystent AI z imieniem**, który zna Cię
z rozmowy wstępnej i wita się z Tobą przy każdym otwarciu folderu.

Notatki mogą mieszkać na **GitHubie** (darmowa prywatna kopia + historia
zmian — Mimir wszystko skonfiguruje), na **Dysku Google**, albo **tylko na
Twoim komputerze**. Na koniec Mimir pomoże Ci zainstalować
[Obsidian](https://obsidian.md) — piękne, darmowe okno na Twoje notatki.

### Jak zacząć

Potrzebujesz AI, które umie działać na Twoim komputerze — np. **Claude**
(aplikacja desktop lub Claude Code) albo **Codex**.

**Sposób 1 — jedna komenda (masz Claude Code, Codex lub podobnego agenta):**

```
npx skills add 533konrad/mimir
```

Potem w swoim AI napisz: **„Uruchom Mimira"** — i odpowiadaj na pytania. Tyle.

**Sposób 2 — magiczny prompt (dowolne AI z dostępem do internetu):**

Wklej do swojego AI:

> Przeczytaj plik https://raw.githubusercontent.com/533konrad/mimir/main/skills/mimir/wizard/WIZARD.md
> i poprowadź mnie przez niego jako wizard Mimir. Pozostałe pliki repo
> znajdziesz pod https://raw.githubusercontent.com/533konrad/mimir/main/skills/mimir/

**Sposób 3 — bez terminala:**

1. Pobierz to repo: zielony przycisk **Code → Download ZIP**, rozpakuj.
2. Otwórz swoje AI w rozpakowanym folderze (albo dodaj folder do rozmowy).
3. Napisz: **„Uruchom Mimira"**.

### Prywatność

Wszystko powstaje na **Twoim** komputerze i **Twoich** kontach. Mimir nigdy
nie prosi o hasła — logowania (GitHub, Google) klikasz sam(a) w swojej
przeglądarce. Repozytorium z notatkami jest domyślnie **prywatne**.

---

## 🇬🇧 In English

Mimir is a wizard that talks with you for ~10 minutes and builds your
**second brain** — one folder of plain text files in the **SIXPACK**
structure: six blocks of life, each answering one question (**work** — what
do I live off? · **public** — what do I give the world? · **self** — who am
I becoming? · **people** — who do I live with? · **play** — what brings me
joy? · **library** — what do I collect?), plus an **inbox**, **maps of
content**, and an **archive** where nothing ever gets deleted.

Mimir doesn't interrogate: paste your LinkedIn or blog link, answer six
1–5 scale questions — and **within minutes you're looking at your second
brain, already seeded with notes about you**. The rest fills itself in over
time, one question at a time.

Optionally, it also sets up **your own named AI assistant** that knows you
from the intake interview and greets you every time you open the folder.

Your notes can live on **GitHub** (free private backup + version history —
Mimir configures everything), in **Google Drive**, or **just on your
computer**. At the end, Mimir helps you install
[Obsidian](https://obsidian.md) — a beautiful, free window into your notes.

### Getting started

You need an AI that can work on your computer — e.g. **Claude** (desktop
app or Claude Code) or **Codex**.

**Option 1 — one command (you have Claude Code, Codex or a similar agent):**

```
npx skills add 533konrad/mimir
```

Then tell your AI: **"Run Mimir"** — and answer the questions. That's it.

**Option 2 — magic prompt (any AI with internet access):**

> Read https://raw.githubusercontent.com/533konrad/mimir/main/skills/mimir/wizard/WIZARD.md
> and guide me through it as the Mimir wizard. Other repo files live under
> https://raw.githubusercontent.com/533konrad/mimir/main/skills/mimir/

**Option 3 — no terminal:**

1. Download this repo: green **Code → Download ZIP** button, unpack it.
2. Open your AI in the unpacked folder (or add the folder to a chat).
3. Say: **"Run Mimir"**.

### Privacy

Everything is created on **your** machine and **your** accounts. Mimir never
asks for passwords — logins happen in your own browser. Your notes repo is
**private by default**.

---

## Co jest w tym repo / What's in this repo

```
skills/mimir/
├── SKILL.md           # entry point for Claude & skills-compatible agents
├── wizard/            # the wizard flow + storage & Obsidian guides
└── templates/         # vault structure spec + assistant layer spec
AGENTS.md              # entry point for Codex & other agents
CLAUDE.md              # entry point for Claude Code opened in this folder
```

---

[![Install with skills CLI](https://skills.sh/b/533konrad/mimir)](https://skills.sh/533konrad/mimir)

Mimir zbudował / built by **[Konrad Gładkowski](https://konradgladkowski.com)** ·
inspirowane systemem, na którym pracuje na co dzień / inspired by the system
he runs his own life on. Strona / Homepage:
[konradgladkowski.com/mimir](https://konradgladkowski.com/mimir).
Licencja / License: MIT.
