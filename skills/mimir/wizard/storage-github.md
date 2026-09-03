# Storage: GitHub (recommended upgrade)

Runs in Step 8, on a vault that **already exists locally** and already has
the user's notes. End state: a **private** repo on the user's GitHub account
containing that vault, with a first commit pushed. Frame it as "przenoszę
Twój gotowy second brain do chmury" — nothing gets rebuilt.

Why GitHub for a non-technical person (say it in one line, not a lecture):
free backup + a "time machine" for every note, and every AI coding tool
speaks git natively.

## Preflight

Check quietly (don't narrate every command):

1. Can you run shell commands at all? If not (e.g. plain web chat), this
   path is unavailable — say so kindly and fall back to Drive/local/zip.
2. `git --version` — installed?
3. `gh --version` — GitHub CLI installed?
4. `gh auth status` — logged in?

Tell the user the plan based on what's missing. Typical worst case is two
installs + one browser login — frame it as "trzy krótkie kroki, potem
wszystko dzieje się samo".

## Installing what's missing

Prefer the path with the fewest decisions for the user. By OS:

- **macOS**: if Homebrew exists → `brew install git gh` (git usually ships
  with Xcode CLT; `git --version` may itself trigger the CLT install popup —
  warn them a system dialog may appear and that's OK). No Homebrew → download
  gh installer from https://cli.github.com and guide the clicks.
- **Windows**: `winget install --id Git.Git -e` and
  `winget install --id GitHub.cli -e` (winget is preinstalled on Win 10/11).
  No winget → installers from https://git-scm.com and https://cli.github.com.
- **Linux**: they're probably fine, but use the distro package manager.

After installs, a fresh terminal/session may be needed for PATH — if a
command isn't found right after installing, that's the first thing to try.

## Login — the user does this, not you

Run `gh auth login --web --git-protocol https` and tell the user what will
happen **before** it happens: "W przeglądarce otworzy się GitHub i poprosi
o kod, który zobaczysz w terminalu. Wpisz kod, kliknij Authorize."

- **Never** ask for their password, token, or 2FA code. If a prompt asks for
  anything secret, the user types it themselves in their own browser.
- No GitHub account? Send them to https://github.com/signup, tell them the
  free plan is all they need, and wait. Account creation is theirs alone —
  you only wait and cheer.

Verify with `gh auth status`.

## Create the repo

1. Confirm the repo name with the user — suggest `second-brain` (or their
   vault name). Spell out: **private**, meaning only they can see it.
2. In the existing vault folder:

```sh
cd <vault-folder>
git init -b main
git add -A
git commit -m "Mimir: initial second brain"
gh repo create <name> --private --source . --push
```

3. Add a `.gitignore` with at least: `.DS_Store`, `.obsidian/workspace*`
   (Obsidian's window state — churns constantly, worthless in history).

## Ongoing sync (tell them once, at the finish screen)

Their AI can commit + push whenever they ask ("zapisz zmiany do chmury").
If they install the Obsidian **obsidian-git** plugin (see `wizard/obsidian.md`),
it can auto-commit on a timer. Don't set up cron/automation beyond that in v1.

## Fallbacks

- `gh` install or login fails twice → offer the browser route: they create
  the repo by clicking at https://github.com/new (walk them through the
  three fields: name, Private, Create), then you connect it:
  `git remote add origin <url> && git push -u origin main`.
- Still stuck → the vault stays local and fully usable (it already works).
  Leave a note in the vault README that "podłączenie GitHuba" is a 5-minute
  job for a returning session — Mimir can do it later.
