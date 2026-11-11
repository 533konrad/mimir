#!/usr/bin/env python3
"""Check a Mimir vault for the drift a model would otherwise have to eyeball.

The vault's assistant runs this before the weekly review ("przegląd
tygodnia" / "weekly review"), so the brief starts from facts instead of a
model skimming hundreds of notes. Everything here is deterministic: same
vault, same date, same report.

What it reports:

* stale        notes with `status: active` not updated for more than N days
               (default 14; `horizon: evergreen` is exempt, it is meant to last)
* orphans      notes in the six blocks that nothing links to
* broken links wikilinks that resolve to no file in the vault
* one-sided    a map in `moc/` links a note that does not point back with
  maps        `moc: "[[map]]"`, or a note points at a map that does not list it
* inbox        how many things wait in `inbox/`
* sources      how many sources sit digested in `library/zrodla/`
               (`library/sources/` in English vaults)
* warnings     open `> [!warning]` callouts: contradictions waiting for a human

It also grades a digest ("odśwież wiedzę" / "digest") against its contract, for
tests and evals: `--snapshot` records the vault before, `--check-digest`
compares after. Human notes may only gain a "see also" footer, sources must
arrive in `library/zrodla/` byte-identical, and every note the assistant
writes must name its sources.

Usage:
    python3 vault_lint.py [VAULT]                    # human-readable report
    python3 vault_lint.py [VAULT] --json             # for the assistant
    python3 vault_lint.py [VAULT] --days 21 --today 2026-11-11
    python3 vault_lint.py [VAULT] --snapshot before.json
    python3 vault_lint.py [VAULT] --check-digest before.json

VAULT defaults to the current folder. Stdlib only, Python 3.8+. Read-only,
except for the snapshot file you ask it to write.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
from pathlib import Path

BLOCKS = ("work", "public", "self", "people", "play", "library")
SKIP_DIRS = {".mimir", ".obsidian", ".git", ".trash", "node_modules"}
# Files that live in inbox/ by design and are not waiting to be sorted.
INBOX_SYSTEM = {"sixpack-do-uzupelnienia.md", ".gitkeep"}
SOURCE_DIRS = ("library/zrodla", "library/sources")
CHANGE_LOGS = ("dziennik-zmian", "change-log")
SEE_ALSO_RE = re.compile(r"(?im)^#{0,6}\s*\**\s*(zobacz te[zż]|see also)\b")

WIKILINK_RE = re.compile(r"!?\[\[([^\]\n]+?)\]\]")
FENCE_RE = re.compile(r"(?ms)^(```|~~~).*?^\1[^\n]*$")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---[ \t]*(?:\n|\Z)", re.DOTALL)
WARNING_RE = re.compile(r"(?im)^\s*>\s*\[!warning\]")
DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


# ---------------------------------------------------------------- parsing


def split_frontmatter(text: str):
    """(frontmatter text, body). Frontmatter is '' when the note has none."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return "", text
    return m.group(1), text[m.end():]


def fm_value(fm: str, key: str):
    """A tiny YAML subset: `key: value`, `key: [a, b]` and a `- item` list.

    Returns a string, a list of strings, or None. Enough for the keys Mimir
    writes; anything fancier is read as a plain string."""
    lines = fm.splitlines()
    for i, line in enumerate(lines):
        if not re.match(rf"^{re.escape(key)}\s*:", line):
            continue
        raw = line.split(":", 1)[1].strip()
        if raw.startswith("[") and raw.endswith("]"):
            items = [x.strip().strip("\"'") for x in _split_flow(raw[1:-1])]
            return [x for x in items if x]
        if raw == "":
            items = []
            for nxt in lines[i + 1:]:
                m = re.match(r"^\s+-\s*(.*)$", nxt)
                if not m:
                    break
                items.append(m.group(1).strip().strip("\"'"))
            return items if items else None
        return raw.strip("\"'")
    return None


def _split_flow(inner: str):
    """Split a YAML flow list on commas outside of [[...]] and quotes."""
    out, buf, depth, quote = [], "", 0, None
    for ch in inner:
        if quote:
            buf += ch
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif ch == "," and depth == 0:
            out.append(buf)
            buf = ""
            continue
        buf += ch
    if buf.strip():
        out.append(buf)
    return out


def as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def strip_code(text: str) -> str:
    """Wikilinks inside code are examples, not links."""
    return INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))


def link_target(inner: str) -> str:
    """`note#heading|alias` -> `note`."""
    target = inner.split("|", 1)[0].rstrip("\\")
    target = target.split("#", 1)[0].split("^", 1)[0]
    return target.strip()


def links_in(text: str) -> list:
    """Every wikilink target in a note: frontmatter (where `moc:` and
    `sources:` live, and Obsidian treats them as real links) plus the body
    with code removed."""
    fm, body = split_frontmatter(text)
    found = []
    for chunk in (fm, strip_code(body)):
        for m in WIKILINK_RE.finditer(chunk):
            t = link_target(m.group(1))
            if t:
                found.append(t)
    return found


def parse_date(value):
    if not value or not isinstance(value, str):
        return None
    m = DATE_RE.search(value)
    if not m:
        return None
    try:
        return _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


# ---------------------------------------------------------------- the vault


class Vault:
    def __init__(self, root: Path):
        self.root = root
        self.files = []  # every file, relative posix paths
        self.notes = {}  # rel path -> text, markdown only
        for p in sorted(root.rglob("*")):
            rel = p.relative_to(root)
            if any(part in SKIP_DIRS for part in rel.parts) or not p.is_file():
                continue
            relp = rel.as_posix()
            self.files.append(relp)
            if p.suffix.lower() == ".md":
                self.notes[relp] = p.read_text(encoding="utf-8", errors="replace")
        self._by_stem = {}
        self._by_name = {}
        self._by_path = {}
        for f in self.files:
            low = f.lower()
            self._by_name.setdefault(low.rsplit("/", 1)[-1], f)
            self._by_path.setdefault(low, f)
            if low.endswith(".md"):
                self._by_stem.setdefault(low.rsplit("/", 1)[-1][:-3], f)
                self._by_path.setdefault(low[:-3], f)

    def resolve(self, target: str):
        """Obsidian-style: by path when the link has a folder, else by file
        name (stem for notes, full name for attachments). Case-insensitive."""
        t = target.strip().lstrip("/").lower()
        if "/" in t:
            hit = self._by_path.get(t) or self._by_path.get(t + ".md")
            if hit:
                return hit
            t = t.rsplit("/", 1)[-1]
        if t.endswith(".md"):
            t = t[:-3]
        return self._by_stem.get(t) or self._by_name.get(t)

    def fm(self, rel: str) -> str:
        return split_frontmatter(self.notes[rel])[0]

    @staticmethod
    def stem(rel: str) -> str:
        return rel.rsplit("/", 1)[-1][:-3]


def is_map(rel: str, vault: Vault) -> bool:
    if not rel.startswith("moc/"):
        return False
    if Vault.stem(rel) in CHANGE_LOGS:
        return False
    return fm_value(vault.fm(rel), "type") != "log"


def lint(root: Path, today: _dt.date, days: int = 14) -> dict:
    v = Vault(root)

    inbox = [f for f in v.files
             if f.startswith("inbox/") and f.rsplit("/", 1)[-1] not in INBOX_SYSTEM]

    sources = [f for f in v.files
               if any(f.startswith(d + "/") for d in SOURCE_DIRS) and not f.endswith(".gitkeep")]

    stale = []
    for rel, text in v.notes.items():
        fm = split_frontmatter(text)[0]
        if fm_value(fm, "status") != "active":
            continue
        if fm_value(fm, "horizon") == "evergreen":
            continue
        if rel.startswith(("context/", "decisions/", "inbox/")):
            continue  # the assistant's own files, and inbox has its own count
        updated = parse_date(fm_value(fm, "updated")) or parse_date(fm_value(fm, "created"))
        if updated is None:
            mtime = (root / rel).stat().st_mtime
            updated = _dt.date.fromtimestamp(mtime)
        age = (today - updated).days
        if age > days:
            stale.append({"path": rel, "updated": updated.isoformat(), "days": age})
    stale.sort(key=lambda s: -s["days"])

    broken = []
    incoming = {}
    outgoing = {}
    for rel, text in v.notes.items():
        targets = []
        for t in links_in(text):
            hit = v.resolve(t)
            if hit is None:
                broken.append({"path": rel, "target": t})
                continue
            targets.append(hit)
            if hit != rel:
                incoming.setdefault(hit, set()).add(rel)
        outgoing[rel] = targets

    orphans = [rel for rel in v.notes
               if rel.split("/", 1)[0] in BLOCKS and "/" in rel and not incoming.get(rel)]

    one_sided = []
    maps = [rel for rel in v.notes if is_map(rel, v)]
    for m in maps:
        mstem = Vault.stem(m).lower()
        body_links = set()
        for raw in WIKILINK_RE.finditer(strip_code(split_frontmatter(v.notes[m])[1])):
            hit = v.resolve(link_target(raw.group(1)))
            if hit and hit != m and hit.endswith(".md"):
                body_links.add(hit)
        for note in sorted(body_links):
            back = [link_target(x.strip("[]")).lower()
                    for x in as_list(fm_value(v.fm(note), "moc"))]
            if mstem not in back:
                one_sided.append({"map": m, "note": note, "missing": "note has no moc: back to the map"})
        for rel in v.notes:
            if rel == m or rel in body_links:
                continue
            back = [link_target(x.strip("[]")).lower() for x in as_list(fm_value(v.fm(rel), "moc"))]
            if mstem in back:
                one_sided.append({"map": m, "note": rel, "missing": "map does not list the note"})

    warnings = []
    for rel, text in v.notes.items():
        body = strip_code(split_frontmatter(text)[1])
        for n, line in enumerate(body.splitlines(), 1):
            if WARNING_RE.match(line):
                warnings.append({"path": rel, "line": n})

    return {
        "vault": str(root),
        "today": today.isoformat(),
        "stale_after_days": days,
        "inbox": {"count": len(inbox), "files": inbox},
        "sources_digested": len(sources),
        "stale": stale,
        "orphans": sorted(orphans),
        "broken_links": broken,
        "one_sided_moc": one_sided,
        "warnings": warnings,
    }


# ---------------------------------------------------------------- digest contract


def snapshot(root: Path) -> dict:
    v = Vault(root)
    return {
        "notes": v.notes,
        "hashes": {f: hashlib.sha256((root / f).read_bytes()).hexdigest() for f in v.files},
    }


def _is_see_also_footer(added: str) -> bool:
    """A heading "Zobacz też" / "See also", then list items with links, and
    nothing else. Two digests may each append one."""
    lines = [ln.strip() for ln in added.splitlines() if ln.strip()]
    if not lines:
        return True
    for ln in lines:
        if SEE_ALSO_RE.match(ln):
            continue
        if not (ln[:1] in "-*" and WIKILINK_RE.search(ln)):
            return False
    return bool(SEE_ALSO_RE.match(lines[0]))


def _is_subsequence(needles: list, haystack: list) -> bool:
    it = iter(haystack)
    return all(any(n == h for h in it) for n in needles)


def _is_assistant(text: str) -> bool:
    return fm_value(split_frontmatter(text)[0], "author") == "assistant"


def check_digest(root: Path, before: dict) -> list:
    """Violations of the digest contract between a snapshot and now.

    1. Human notes (no `author: assistant`) are untouched, or gain only a
       "zobacz też" / "see also" section at the bottom. Moving one is fine
       for sources leaving inbox/; anything else that vanishes is a violation.
    2. Every source that left `inbox/` sits in `library/zrodla/` (or
       `library/sources/`) byte-identical.
    3. Every new or changed assistant note names its sources, and they resolve.
    4. Something digested means the change log mentions it.
    """
    v = Vault(root)
    old_notes = before["notes"]
    old_hashes = before["hashes"]
    now_hashes = {f: hashlib.sha256((root / f).read_bytes()).hexdigest() for f in v.files}
    by_hash = {}
    for f, h in now_hashes.items():
        by_hash.setdefault(h, []).append(f)
    problems = []

    digested = []
    for f, h in old_hashes.items():
        if not f.startswith("inbox/") or f in now_hashes:
            continue
        if f.rsplit("/", 1)[-1] in INBOX_SYSTEM:
            continue
        homes = [g for g in by_hash.get(h, []) if any(g.startswith(d + "/") for d in SOURCE_DIRS)]
        others = by_hash.get(h, [])
        if homes:
            digested.append(homes[0])
        elif not others:
            problems.append(f"{f}: left inbox/ but no byte-identical copy exists anywhere")

    for f, h in old_hashes.items():
        if any(f.startswith(d + "/") for d in SOURCE_DIRS) and now_hashes.get(f) not in (None, h):
            problems.append(f"{f}: a digested source was edited; sources are read-only")

    for rel, old in old_notes.items():
        if _is_assistant(old) or rel.startswith(("inbox/", ".mimir/")):
            continue
        if any(rel.startswith(d + "/") for d in SOURCE_DIRS):
            continue
        if rel.startswith("moc/"):
            # maps grow by inserted lines (a link under its section); an
            # existing line may not change or disappear
            new = v.notes.get(rel)
            if new is not None and not _is_subsequence(
                    [ln for ln in old.splitlines() if ln.strip()], new.splitlines()):
                problems.append(f"{rel}: map lines were changed or removed, only additions allowed")
            continue
        new = v.notes.get(rel)
        if new is None:
            if rel in old_hashes and old_hashes[rel] in now_hashes.values():
                continue  # moved, not lost
            problems.append(f"{rel}: a human note disappeared")
            continue
        if new == old:
            continue
        base = old.rstrip("\n")
        if not new.startswith(base):
            problems.append(f"{rel}: a human note was rewritten; only a 'see also' footer may be appended")
            continue
        if not _is_see_also_footer(new[len(base):]):
            problems.append(f"{rel}: something other than a 'see also' footer of links "
                            "was appended to a human note")

    for rel, text in v.notes.items():
        if not _is_assistant(text) or old_notes.get(rel) == text:
            continue
        if rel.startswith("moc/") and not is_map(rel, v):
            continue  # the change log cites sources line by line, not in frontmatter
        srcs = as_list(fm_value(split_frontmatter(text)[0], "sources"))
        if not srcs:
            problems.append(f"{rel}: assistant note without `sources:`")
            continue
        for s in srcs:
            if v.resolve(link_target(s.strip("[]"))) is None:
                problems.append(f"{rel}: source {s} does not resolve")

    if digested:
        logs = [rel for rel in v.notes if rel.startswith("moc/") and Vault.stem(rel) in CHANGE_LOGS]
        if not logs:
            problems.append("sources were digested but moc/dziennik-zmian.md (or moc/change-log.md) is missing")
        else:
            log_text = "\n".join(v.notes[r] for r in logs).lower()
            for src in digested:
                if Vault.stem(src).lower() not in log_text:
                    problems.append(f"{src}: digested but not mentioned in the change log")

    return problems


# ---------------------------------------------------------------- output


TEXT = {
    "pl": {
        "title": "Przegląd vaulta",
        "inbox": "W inboxie czeka: {n}",
        "sources": "Źródła wpięte w wiedzę: {n}",
        "stale": "Aktywne, ale nieruszane od ponad {d} dni",
        "orphans": "Sieroty (nic do nich nie linkuje)",
        "broken": "Zerwane linki",
        "moc": "Jednostronne mapy",
        "warn": "Otwarte sprzeczności ([!warning])",
        "none": "brak",
        "days": "dni",
    },
    "en": {
        "title": "Vault check",
        "inbox": "Waiting in inbox: {n}",
        "sources": "Sources digested: {n}",
        "stale": "Active but untouched for more than {d} days",
        "orphans": "Orphans (nothing links to them)",
        "broken": "Broken links",
        "moc": "One-sided maps",
        "warn": "Open contradictions ([!warning])",
        "none": "none",
        "days": "days",
    },
}


def vault_language(root: Path) -> str:
    state = root / ".mimir" / "state.md"
    if state.is_file():
        m = re.search(r"(?m)^language:\s*(\w+)", state.read_text(encoding="utf-8", errors="replace"))
        if m and m.group(1) in TEXT:
            return m.group(1)
    return "en"


def render(report: dict, lang: str) -> str:
    t = TEXT[lang]
    out = [f"# {t['title']} ({report['today']})", "",
           t["inbox"].format(n=report["inbox"]["count"]),
           t["sources"].format(n=report["sources_digested"]), ""]

    def section(title, items):
        out.append(f"## {title}: {len(items) if items else t['none']}")
        out.extend(f"- {i}" for i in items)
        out.append("")

    section(t["stale"].format(d=report["stale_after_days"]),
            [f"{s['path']} ({s['days']} {t['days']})" for s in report["stale"]])
    section(t["orphans"], report["orphans"])
    section(t["broken"], [f"{b['path']} -> [[{b['target']}]]" for b in report["broken_links"]])
    section(t["moc"], [f"{m['map']} <-> {m['note']}: {m['missing']}" for m in report["one_sided_moc"]])
    section(t["warn"], [f"{w['path']}:{w['line']}" for w in report["warnings"]])
    return "\n".join(out).rstrip() + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check a Mimir vault for drift.")
    ap.add_argument("vault", nargs="?", default=".", help="vault folder (default: current folder)")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    ap.add_argument("--days", type=int, default=14, help="active notes older than this are stale (default 14)")
    ap.add_argument("--today", help="YYYY-MM-DD, for reproducible reports")
    ap.add_argument("--lang", choices=sorted(TEXT), help="report language (default: the vault's)")
    ap.add_argument("--snapshot", metavar="FILE", help="record the vault before a digest")
    ap.add_argument("--check-digest", metavar="FILE", help="grade a digest against a snapshot")
    args = ap.parse_args(argv)

    root = Path(args.vault).expanduser()
    if not root.is_dir():
        print(f"No vault folder at {root}", file=sys.stderr)
        return 2

    if args.snapshot:
        Path(args.snapshot).write_text(json.dumps(snapshot(root), ensure_ascii=False), encoding="utf-8")
        print(f"snapshot: {args.snapshot}")
        return 0
    if args.check_digest:
        before = json.loads(Path(args.check_digest).read_text(encoding="utf-8"))
        problems = check_digest(root, before)
        if args.json:
            print(json.dumps({"violations": problems}, ensure_ascii=False, indent=2))
        else:
            print("\n".join(problems) if problems else "digest contract: OK")
        return 1 if problems else 0

    today = parse_date(args.today) if args.today else _dt.date.today()
    if today is None:
        print("--today must be YYYY-MM-DD", file=sys.stderr)
        return 2
    report = lint(root, today, args.days)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render(report, args.lang or vault_language(root)), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
