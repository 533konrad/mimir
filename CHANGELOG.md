# Changelog

All notable changes to Mimir are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and the project adheres to
[Semantic Versioning](https://semver.org/).

New changes land under **Unreleased**. A version is cut only when the
maintainer decides to release: the heading gets a number and a date, and the
`version` in `.claude-plugin/plugin.json` moves with it.

## [Unreleased]

### Changed

- The six SIXPACK parts are called "obszary" in Polish everywhere a user
  reads: the README, the wizard's line about a declined area, the assistant
  spec, and the text the build script writes into the vault (README, the
  home map heading, the inbox note). "Klocki" was the author's own jargon.
  A test now fails if it comes back.

## [2.2.1] - 2026-09-15

### Added

- ChatGPT and Microsoft 365 Copilot. A second package, `mimir-m365.zip`, with
  `SKILL.md` at the zip root as Microsoft's Agent Builder requires, is
  attached to every release beside `mimir.skill` (skill folder at the root,
  for Claude and ChatGPT). The build refuses a package over Microsoft's
  preview limits: 350 files, folder depth 3, accepted file types, `SKILL.md`
  under 20,000 characters.
- "When something goes wrong" in `WIZARD.md`, plus a table for chat apps in
  `hosted.md`: every failure gets one plain sentence, a recommended move and
  an alternative, never a dead end. The last rung hands the collected answers
  over as a `Mimir profile:` block to paste where Mimir works, and a pasted
  block skips the interview.

### Changed

- Hosted mode no longer assumes Claude. It finds its build script in the
  sandbox, puts the zip where each app offers downloads (Claude
  `/mnt/user-data/outputs`, ChatGPT `/mnt/data`, otherwise the app's own
  output folder), and opens links only through the app's browsing tool,
  since code in these sandboxes has no internet.
- Upload packages carry a frontmatter of only `name` and `description` for
  the widest compatibility, and their `agents/openai.yaml` shows a Polish
  short description in the skills list.
- README: route 2 covers Claude, ChatGPT and Microsoft 365 Copilot, with
  plan requirements and which one is tested live.

## [2.2.0] - 2026-09-14

### Added

- Claude.ai route with no terminal, on every plan including Free: a
  `mimir.skill` file attached to each GitHub Release
  (`releases/latest/download/mimir.skill`), uploaded in Customize → Skills.
  `scripts/build_skill.py` builds it with a short Polish description within
  Claude.ai's 200-character limit (it is what users see in their Skills
  list); the repo `SKILL.md` keeps the long one for Claude Code.
- Hosted mode, `wizard/hosted.md`: when Mimir runs in a sandbox that cannot
  reach the user's disk, it builds the vault there and hands it over as a zip,
  with its own privacy line, unpack and Obsidian steps, storage options, and
  a way to continue later by attaching the zip. The environment is read from
  what the model already knows, never by calling connector tools, so no
  permission pop-up appears before the welcome screen.
- `build_vault.py --pack VAULT ZIP` zips a vault with the vault folder at the
  root, refusing a zip path inside the vault.
- Release workflow: pushing a `v*` tag runs the tests, builds `mimir.skill`
  and publishes a GitHub Release with notes taken from this changelog.

### Changed

- One promise everywhere: 15 minutes. The README said "~10 minutes" and the
  welcome screen "in 10 minutes" while the title, the skill description and
  the landing page said 15. A test now fails on any other advertised duration.

## [2.1.1] - 2026-09-14

### Fixed

- Note titles that YAML reads as something other than text are now quoted
  too: a leading `- ` (opened a list and broke the frontmatter), numbers
  (`2026`), dates, and `yes` / `no` / `null` (became a number, a boolean or
  nothing). 2.1.0 covered only `: ` and ` #`.
- The README promised that plugin updates arrive automatically. Claude Code
  keeps auto-update off for third-party marketplaces, so it now says how to
  switch it on (`/plugin` → Marketplaces → `533konrad` → Enable auto-update).

### Changed

- The test suite round-trips generated titles through a real YAML parser
  (PyYAML, installed in CI only; the builder stays stdlib-only).

## [2.1.0] - 2026-09-14

### Added

- Claude Code plugin: the repo is its own single-plugin marketplace
  (`claude plugin marketplace add 533konrad/mimir`, then
  `claude plugin install mimir@533konrad`). The README documents both install
  routes and says to pick one, since installing both leaves Mimir in place twice.
- Codex skill picker metadata in `skills/mimir/agents/openai.yaml`.
- `scripts/build_vault.py`: a deterministic vault builder. The wizard writes a
  `profile.json` and the script builds the structure (sizing by quiz,
  frontmatter, Obsidian config, one README, `moc/home.md` with both ends of
  every link, inbox seeds, assistant layer, state marker). Stdlib only, with
  `--dry-run`, `--print-schema` and `--open`; `MIMIR_NO_OPEN` suppresses the
  file manager window. It refuses an invalid profile instead of guessing.
- Every interview question carries a recommended answer.
- Resume after interruption: the `.mimir/state.md` state marker and a
  "coming back to an existing folder" flow with five cases.
- Trigger evals (`evals/run-triggers.py`, `evals/triggers.md`) and manual
  dry-run scenarios (`evals/scenarios.md`).
- Automated checks on every push (GitHub Actions, Python 3.9 and 3.13, stdlib
  only): `python3 -m unittest discover -s tests`.
  - `tests/test_repo.py`: SKILL.md name and description limit, every referenced
    file and raw GitHub URL exists, the red lines in `SKILL.md` and `AGENTS.md`
    stay in sync, `plugin.json` matches the newest `CHANGELOG.md` version.
  - `tests/test_build_vault.py`: rebuilds leave existing files byte-identical,
    two-way MOC links, `people/` never nested, quiz sizing, refused profiles.

### Changed

- The skill description is limited to build, finish and upgrade intent, with
  an explicit "do not use for" clause and a "Not a Mimir job" section.
- Step 0 detects the user's language instead of asking for it.
- Step 1 welcome, Step 2 link request and Step 6 opening line rewritten for a
  first-time user; the demo note is no longer called a "catch".
- Step 3 quiz asks one question at a time and explains the 1-5 scale first by
  what it changes (a 5 gets subfolders and seed notes, a 1 is not created).
- Step 5 builds through the script, with a hand-build fallback for
  environments without a shell. Step 6 re-runs the build for the first note.
- README links to konradgladkowski.com carry campaign UTM parameters.

### Fixed

- Existing files stay byte-identical: create-if-missing everywhere, append
  only, and "delete it all" renames the old folder to `<name>-backup-<date>`.
- Requests other than build, finish, add the assistant or connect storage no
  longer start or propose a build.
- The GitHub storage path stops after the second failure and runs
  `gh auth login` only in an interactive terminal.
- MOCs wikilink real notes only, every linked note gets `moc:` in the same
  write, exactly one README at the root, and `people/` never gets subfolders.
- The first note no longer resurrects a block the user declined in the quiz.
- `AGENTS.md` carried the old red lines, so Codex users got outdated rules. It
  now matches `SKILL.md` and names it as the source of truth.
- The language red line in `SKILL.md` and `AGENTS.md` still said to offer
  Polish and English at the start, contradicting Step 0 (detect, never ask).
- A mapped note added on a rebuild (Step 6's first catch, after `moc/home.md`
  already exists from Step 5) was never linked back from the map, silently
  breaking the two-way MOC guarantee. `build_vault.py` now appends the
  missing link under a small "Dopisane później / Added later" heading
  instead of leaving it one-way.
- A title containing `: ` or a `#` (e.g. `Rekrutacja: Q4 #pilne`) produced
  invalid YAML frontmatter; Obsidian showed it in red and dropped the
  properties. Titles needing it are now quoted.

## [2.0.0] - 2026-09-03

### Added

- Mimir v2: the second brain wizard building a SIXPACK vault (six life blocks,
  inbox, maps of content, archive) with an optional AI assistant layer.
- `skills/mimir/` layout for `npx skills add 533konrad/mimir`.
- Three install routes: skills CLI, magic prompt, ZIP download.

[Unreleased]: https://github.com/533konrad/mimir/compare/v2.2.1...HEAD
[2.2.1]: https://github.com/533konrad/mimir/compare/v2.2.0...v2.2.1
[2.2.0]: https://github.com/533konrad/mimir/compare/v2.1.1...v2.2.0
[2.1.1]: https://github.com/533konrad/mimir/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/533konrad/mimir/compare/8e0d84a...v2.1.0
[2.0.0]: https://github.com/533konrad/mimir/commit/8e0d84a
