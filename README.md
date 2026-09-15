# 🧠 Mimir

**Twój second brain w 15 minut. Za darmo, po ludzku, z pomocą AI.**
*Your second brain in 15 minutes. Free, human-friendly, AI-guided.*

[🇵🇱 Polski](#-po-polsku) · [🇬🇧 English](#-in-english)

---

## 🇵🇱 Po polsku

Mimir to wizard, który rozmawia z Tobą przez 15 minut i buduje Ci
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
claude plugin marketplace add 533konrad/mimir
claude plugin install mimir@533konrad
```

Potem w swoim AI napisz: **„Uruchom Mimira"** i odpowiadaj na pytania. Tyle.
Chcesz, żeby nowe wersje Mimira dociągały się same? W Claude Code wpisz
`/plugin`, wejdź w **Marketplaces**, wybierz `533konrad` i kliknij
**Enable auto-update**. Bez tego zostajesz na wersji z dnia instalacji.

Nie masz Claude Code? Ta sama rzecz przez instalator, na Codexa i resztę agentów:

```
npx skills add 533konrad/mimir
```

Wybierz jedną z dwóch dróg. Obie naraz = Mimir zainstalowany dwa razy.

**Sposób 2 — w aplikacji AI, bez terminala:**

Wgrywasz Mimira jako skill, a na końcu rozmowy pobierasz gotowy second brain
jako jeden plik zip.

- **Claude** (claude.ai i aplikacja, każdy plan, także darmowy):
  1. Pobierz [`mimir.skill`](https://github.com/533konrad/mimir/releases/latest/download/mimir.skill).
  2. **Settings → Capabilities**: włącz **Code execution and file creation**
     (na planie Team lub Enterprise włącza to administrator).
  3. **Customize → Skills → + → Create skill → Upload a skill** i wskaż plik.
- **ChatGPT** (plany Business, Enterprise i Edu; Free i Plus nie mają
  skilli): pobierz [`mimir.skill`](https://github.com/533konrad/mimir/releases/latest/download/mimir.skill),
  potem **Plugins → Skills → Create → Upload from your computer**.
- **Microsoft 365 Copilot** (licencja Copilot i organizacja w programie
  Frontier, funkcja w podglądzie): pobierz [`mimir-m365.zip`](https://github.com/533konrad/mimir/releases/latest/download/mimir-m365.zip),
  potem **Agents & Skills → New agent → Configure → Skills → Add** i wgraj plik.

Potem w nowej rozmowie napisz: **„Uruchom Mimira"**. Sprawdzone na żywo
w Claude; w ChatGPT i Copilocie zgodnie z dokumentacją producentów. Gdyby coś
nie zadziałało po drodze, Mimir sam zaproponuje obejście.

**Sposób 3 — magiczny prompt (dowolne AI z dostępem do internetu):**

Wklej do swojego AI:

> Przeczytaj plik https://raw.githubusercontent.com/533konrad/mimir/main/skills/mimir/wizard/WIZARD.md
> i poprowadź mnie przez niego jako wizard Mimir. Pozostałe pliki repo
> znajdziesz pod https://raw.githubusercontent.com/533konrad/mimir/main/skills/mimir/

**Sposób 4 — pobrany folder (AI na Twoim komputerze):**

1. Pobierz to repo: zielony przycisk **Code → Download ZIP**, rozpakuj.
2. Otwórz swoje AI w rozpakowanym folderze (albo dodaj folder do rozmowy).
3. Napisz: **„Uruchom Mimira"**.

### Prywatność

Wszystko powstaje na **Twoim** komputerze i **Twoich** kontach. Mimir nigdy
nie prosi o hasła — logowania (GitHub, Google) klikasz sam(a) w swojej
przeglądarce. Repozytorium z notatkami jest domyślnie **prywatne**.

---

## 🇬🇧 In English

Mimir is a wizard that talks with you for 15 minutes and builds your
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
claude plugin marketplace add 533konrad/mimir
claude plugin install mimir@533konrad
```

Then tell your AI: **"Run Mimir"** and answer the questions. That's it.
Want new Mimir versions to arrive on their own? In Claude Code type
`/plugin`, open **Marketplaces**, pick `533konrad` and choose
**Enable auto-update**. Without it you stay on the version you installed.

Not on Claude Code? The same thing via the installer, for Codex and other agents:

```
npx skills add 533konrad/mimir
```

Pick one route. Both at once leaves you with Mimir installed twice.

**Option 2 — in an AI app, no terminal:**

You upload Mimir as a skill, and at the end of the chat you download your
second brain as a single zip file.

- **Claude** (claude.ai and the app, every plan including Free):
  1. Download [`mimir.skill`](https://github.com/533konrad/mimir/releases/latest/download/mimir.skill).
  2. **Settings → Capabilities**: turn on **Code execution and file creation**
     (on Team or Enterprise plans an admin does this).
  3. **Customize → Skills → + → Create skill → Upload a skill** and pick the file.
- **ChatGPT** (Business, Enterprise and Edu plans; Free and Plus have no
  skills): download [`mimir.skill`](https://github.com/533konrad/mimir/releases/latest/download/mimir.skill),
  then **Plugins → Skills → Create → Upload from your computer**.
- **Microsoft 365 Copilot** (a Copilot licence and an organization in the
  Frontier program, preview feature): download [`mimir-m365.zip`](https://github.com/533konrad/mimir/releases/latest/download/mimir-m365.zip),
  then **Agents & Skills → New agent → Configure → Skills → Add** and upload it.

Then say in a new chat: **"Run Mimir"**. Tested live in Claude; in ChatGPT and
Copilot it follows the vendors' documentation. If something fails along the
way, Mimir proposes a workaround itself.

**Option 3 — magic prompt (any AI with internet access):**

> Read https://raw.githubusercontent.com/533konrad/mimir/main/skills/mimir/wizard/WIZARD.md
> and guide me through it as the Mimir wizard. Other repo files live under
> https://raw.githubusercontent.com/533konrad/mimir/main/skills/mimir/

**Option 4 — downloaded folder (an AI on your computer):**

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
evals/                 # trigger evals (run-triggers.py) + manual dry-run scenarios
CHANGELOG.md           # what changed in each version
scripts/build_skill.py # packs mimir.skill + mimir-m365.zip (attached to every release)
tests/                 # repo checks, vault builder and bundle tests, run on every push
```

---

[![Install with skills CLI](https://skills.sh/b/533konrad/mimir)](https://skills.sh/533konrad/mimir)

Mimir zbudował / built by **[Konrad Gładkowski](https://konradgladkowski.com/?utm_source=github&utm_medium=readme&utm_campaign=mimir)** ·
inspirowane systemem, na którym pracuje na co dzień / inspired by the system
he runs his own life on. Strona / Homepage:
[konradgladkowski.com/mimir](https://konradgladkowski.com/mimir?utm_source=github&utm_medium=readme&utm_campaign=mimir).
Licencja / License: MIT.
