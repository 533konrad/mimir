# Trigger evals — does the `mimir` skill fire when it should, and only then?

The skill's `description` is the only thing the agent sees before deciding to
load Mimir. This table is the contract for that decision. `fire` = the agent
should invoke the `mimir` skill; `no-fire` = it should answer directly (a
paragraph, a file edit, a search) and never start the wizard.

Run: `python3 evals/run-triggers.py` (needs Claude Code CLI; uses a temp
folder with the skill symlinked, writes nothing else). Add a row, rerun.

| id | expected | prompt |
|----|----------|--------|
| T01 | fire | Uruchom Mimira |
| T02 | fire | Zbuduj mi second brain |
| T03 | fire | Chcę system notatek w Obsidianie, pomożesz mi go postawić? |
| T04 | fire | Set up a second brain for me |
| T05 | fire | I pasted this: https://github.com/533konrad/mimir — set this up for me |
| T06 | fire | Mam vault z Mimira w ~/Documents/second-brain, dodaj mi do niego asystenta |
| T07 | fire | Dokończ Mimira |
| N01 | no-fire | Co to jest PARA? |
| N02 | no-fire | Czym różni się SIXPACK od PARA? Krótko. |
| N03 | no-fire | Uporządkuj mi ten plik: nagłówki, listy, bez zmiany treści. |
| N04 | no-fire | Pomóż mi ogarnąć te notatki ze spotkania: klient chce demo w piątek, budżet 20k, decyzja po wakacjach. |
| N05 | no-fire | Znajdź w moim vaulcie notatkę o nurkowaniu |
| N06 | no-fire | Jak nazwać folder na notatki z podcastu: public/podcast czy work/podcast? |
| N07 | no-fire | Napisz mi notatkę z tego linku do library: https://example.com/artykul |
| N08 | no-fire | Przejrzyjmy inbox |
| N09 | no-fire | What's the best way to organize my notes with AI? |

Notes on the borderline rows:

- **N06 / N09** are the closest calls: they are *about* organizing notes, but
  the honest answer is one paragraph. If these fire, the description is too
  broad again.
- **N08** is the vault's own assistant's job (weekly housekeeping), not the
  wizard's — Mimir's persona file handles it. Firing here means a 15-minute
  wizard on a 5-minute task.
- **T06 / T07** are the "coming back" cases from `WIZARD.md`; they must fire
  even though nothing new is being built from scratch.

## Last run

Kept here so the numbers are in the repo, not in someone's terminal history.

| date | build | skill version | pass / total | failures |
|------|-------|---------------|--------------|----------|
| 2026-09-07 | Claude Code 2.1.246 | old description (commit 8e0d84a), N03/N04/N06/N08/N09 only | 4/5 | N09 fired the wizard |
| 2026-09-07 | Claude Code 2.1.246 | narrowed description + "Not a Mimir job" | 16/16 | none |

Single run per prompt (`--runs 1`); use `--runs 3` before trusting a
borderline row.
