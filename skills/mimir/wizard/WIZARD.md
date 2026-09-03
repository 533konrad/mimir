# WIZARD.md — the Mimir flow

This is the single source of truth for the Mimir wizard. Follow the steps in
order. Steps marked *(read file)* tell you which supporting file to read
right before executing that step — don't read everything upfront.

Design principle behind the order: **the user sees their own second brain,
with notes about THEM, within minutes** — before anything gets installed,
before any account, before any cloud. Installs and storage come after the
wow, as upgrades to something that already works.

## Style of the conversation

Model the feel of a great CLI installer (think: PostHog wizard), rendered in
chat:

- Show progress: start each step with a line like `— Krok 3/9: Quiz —` / `— Step 3/9: Quiz —`.
- One question at a time. When offering choices, show a short numbered list with the recommended option first and marked as such.
- Before any action that touches the user's computer or an external service, say in one plain sentence what you're about to do and why. Then do it.
- After each action, confirm what happened in one sentence. No walls of text.
- If your environment has an interactive question tool (e.g. AskUserQuestion), use it for the choice menus and the scale quiz; otherwise ask in plain chat.
- Never show raw error dumps to the user. Translate errors into plain language and offer the next move.

Environment note: you may be running inside Claude Desktop/Cowork, Claude
Code, Codex CLI, or something else. Detect what you can actually do (run
shell commands? read/write local files? fetch web pages?) and adapt. If you
have **no way to write to the user's disk** (e.g. a plain web chat), be
honest about it early: you can still run the interview and generate
everything as a downloadable zip, with instructions where to unpack it.

---

## Step 0/9 — Language

First message: greet in both languages, ask which one to use. Suggest the
language the user already wrote in. Everything user-facing from here on —
conversation, generated notes, vault README — is in the chosen language.
**Top-level folder names always stay English** (`inbox`, `moc`, `archive`,
`work`, `public`, `self`, `people`, `play`, `library`) — short, portable,
tool-friendly. Subfolders inside the blocks are named in the user's language.

## Step 1/9 — Welcome screen

One compact message, in the spirit of an installer splash:

- What Mimir builds: a "second brain" — one folder of plain-text notes,
  organized with the **SIXPACK** structure (six blocks of life + three
  system folders), so both the user and their AI can find anything;
  optionally with a personal AI assistant that knows them.
- The promise, stated plainly: **in about 10 minutes you'll be looking at
  your own second brain, already filled with notes about you.**
- Privacy: everything is created on their machine / their accounts. Mimir
  never asks for passwords; logins happen in their own browser.

End with: `[1] Zaczynamy / Let's go  [2] Najpierw powiedz mi więcej / Tell me more`.
"Tell me more" gets a short explanation of what a second brain is, why plain
markdown files beat closed apps (portable, future-proof, AI-readable), and
the six SIXPACK questions — then back to the menu.

## Step 2/9 — Show me yourself *(read `wizard/interview.md`, Phase A)*

Ask for links: LinkedIn profile, personal blog/website, company page —
whatever exists. Fully skippable. If you can fetch web pages, fetch them and
extract a draft profile (name, what they do, projects, visible interests).
Present it back: "to już o Tobie wiem — zgadza się?" / "here's what I
already know about you — did I get it right?"

**This is the first wow** — the user sees a machine understanding them from
one pasted link, minutes in. If there are no links or no fetch capability,
the user can paste a bio, dictate a messy braindump by voice, or just answer
the quiz in Step 3 — all equally valid inputs.

## Step 3/9 — The Sixpack quiz *(read `wizard/interview.md`, Phase B)*

Six questions, one per life block, each answered on a 1–5 scale
("kompletnie nieważne" → "bardzo ważne" / "not important at all" → "very
important"), in the spirit of a personality test. Then targeted follow-up
questions ONLY for blocks scored 4–5, and ONLY about what the links didn't
already reveal. Blocks scored 1–2 get no follow-ups and a slim (or no)
folder.

Output: the **profile** — everything from Phase A + scale scores + answers +
the list of unanswered questions (used later for progressive fill).

## Step 4/9 — Scope

Ask what they want built:

1. **Vault + assistant** *(recommended)* — the notes structure **plus** a
   personal AI assistant layer: a persona file with a name they choose,
   `context/me.md` built from the interview, and a decision log. Explain in
   one sentence: "your AI will start every conversation already knowing who
   you are and what you're working on."
2. **Vault only** — just the notes structure. Works perfectly in Obsidian
   without any AI. The assistant can be added later by running Mimir again.

If they pick the assistant, ask them to **name it** — suggest 2–3 playful
options fitting their language and vibe, plus "wpisz własne / type your own".
(Fun fact you may share: Mimir itself was inspired by an assistant called
Sancho Tokenez.)

## Step 5/9 — Build, right now, locally *(read `templates/vault-spec.md`; if assistant chosen, also `templates/assistant-spec.md`; location rules in `wizard/storage-local.md`)*

Announce: "Buduję twój second brain..." / "Building your second brain...".
No accounts, no installs — a plain local folder (default
`~/Documents/second-brain`, see `storage-local.md` for location rules and
the zip fallback when you can't write to disk). Create:

1. The SIXPACK structure **sized by the quiz**: blocks scored 4–5 get
   subfolders (from the interview — *their* subfolders, in their language)
   and seed notes; blocks scored 3 get a flat folder; blocks scored 1–2 get
   a flat folder only if the user wants it ("dodam, gdybyś kiedyś chciał" —
   ask once, briefly). `inbox/`, `moc/`, `archive/` always exist.
2. **Seed notes from the links + interview** — this is the second wow. Real
   notes with real frontmatter about their projects, their goals, their
   interests — content they didn't type, extracted from Step 2.
3. `moc/home.md` — their personal map of the vault.
4. The `inbox/sixpack-do-uzupelnienia.md` checklist — open questions the
   interview skipped, fuel for progressive fill.
5. The vault `README.md` in their language + the `.obsidian/` starter config.
6. If assistant chosen: `CLAUDE.md` + `AGENTS.md`, `context/me.md`,
   `context/goals.md`, `decisions/log.md` with its first real entry.

Show a compact tree of what was created, then **pause and invite them to
open one of the seed notes**. Let them react.

## Step 6/9 — First catch (the inbox demo)

Teach the daily loop by doing it once, while momentum is high:

1. Ask them to throw *anything* at you: a link they've been meaning to read,
   a loose thought, an idea, a to-do that's been rattling around.
2. Create it as a note in `inbox/` with proper frontmatter. Show it.
3. Then, in front of their eyes, categorize it: say which block it belongs
   to and why, move it there (or leave it in inbox if genuinely ambiguous —
   and say that this is fine, that's what inbox is for).
4. Name the loop explicitly: **capture everything into inbox without
   thinking; once a week, sort it — with your AI doing the heavy lifting.**

## Step 7/9 — Obsidian *(read `wizard/obsidian.md`)*

Guide them through installing Obsidian and opening the vault folder. The
vault already exists and already has their notes — Obsidian is the beautiful
window onto it. If they already have Obsidian, skip to "open folder as
vault". If they don't want Obsidian at all, that's fine — the vault is plain
files; point them at the folder and move on.

## Step 8/9 — Storage upgrade (optional)

The vault works. Now offer to protect it — one line each:

1. **GitHub** *(recommended)* — a free private repository: version history
   ("time machine for your notes"), backup, works with AI tools. Requires a
   free account — created in their browser, by themselves.
2. **Google Drive** — move the vault into their synced Drive folder.
   Easiest if they already live in Google's world.
3. **Zostaw lokalnie / keep it local** — completely valid. One gentle
   warning about no-backup (once, never nag), plus: "wrócę i podłączę
   GitHub albo Dysk w 5 minut, kiedy zechcesz."

Then *(read exactly one file)*: `wizard/storage-github.md` or
`wizard/storage-drive.md`, and follow it — both operate on the **existing**
vault folder (connect/move, not create). If the chosen path fails twice,
fall back gracefully to local. Never let storage problems spoil a vault that
already works.

## Step 9/9 — Finish screen

One final compact message:

- ✓-list of everything that was built (vault, seeds, assistant, Obsidian,
  storage).
- **The daily habit**: dump thoughts into `inbox/` (or tell your AI).
- **The weekly ritual** (15 min): open the AI in the vault folder and say
  "przejrzyjmy inbox" / "let's review my inbox". The AI will also ask ONE
  leftover Sixpack question per session — that's how the brain fills itself
  over time instead of demanding a long interview upfront.
- **How to come back**: open their AI tool in the vault folder — the
  assistant persona loads automatically and knows them.
- Credit line, exactly once, warm not salesy:
  PL: `Mimir zbudował Konrad Gładkowski → konradgladkowski.com`
  EN: `Mimir was built by Konrad Gładkowski → konradgladkowski.com`

## If the user returns later

Mimir may also be invoked in an **existing** vault (user says "coś nie
działa", "dodaj asystenta", "przejrzyjmy inbox", "podłącz GitHub"). In that
case skip setup: detect the structure, figure out what they need (repair,
upgrade vault-only → assistant, inbox review, storage upgrade, progressive
fill — see `templates/assistant-spec.md`) and do just that. Never rebuild or
overwrite an existing vault.
