#!/usr/bin/env python3
"""Regenerate RECENT.md — a shortcut index of recently added/updated docs.

Usage:  python3 scripts/gen-recent.py [--days N] [--limit N] [--collapse N]

Reads git history, keeps the most recent event per file, and writes RECENT.md
grouped by date (newest first).

Deliberately excluded so the list stays a shortcut rather than a changelog:
  * generated index files (README.md, index.md);
  * pure renames — a file moved without content changes is not a doc event;
  * the tail beyond --limit, and the bulk of any single oversized commit.
"""
import argparse
import os
import re
import subprocess
import sys
from collections import OrderedDict
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_NAMES = {"README.md", "index.md", "RECENT.md"}
CONTENT_EXT = {".md", ".ipynb"}

CATEGORY_LABELS = {
    "ai": "AI", "cloud": "Cloud", "devops": "DevOps", "languages": "Languages",
    "mobile": "Mobile", "web": "Web", "data-ml": "Data & ML",
    "security": "Security", "tools": "Tools", "docs": "Docs", "raw": "Raw notes",
}


def git(*args):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True,
                          text=True, check=True).stdout


def title_of(path):
    """First H1, or frontmatter title, or a humanised filename."""
    full = os.path.join(REPO, path)
    if not os.path.exists(full):
        return os.path.basename(path)
    try:
        with open(full, encoding="utf-8") as fh:
            head = [next(fh, "") for _ in range(40)]
    except (OSError, UnicodeDecodeError):
        return os.path.basename(path)
    for line in head:
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m:
            return m.group(1).strip().strip("`")
    for line in head:
        m = re.match(r'^title:\s*"?(.+?)"?\s*$', line)
        if m:
            return m.group(1).strip()
    return os.path.splitext(os.path.basename(path))[0].replace("-", " ").replace("_", " ")


def category_of(path):
    top = path.split("/")[0]
    if "/" not in path:
        return "Root"
    label = CATEGORY_LABELS.get(top, top)
    parts = path.split("/")
    if len(parts) > 2:
        return f"{label} / {parts[1]}"
    return label


def collect(days):
    raw = git("log", f"--since={days} days ago", "--date=short",
              "--pretty=format:C|%ad|%h|%s", "--name-status", "--diff-filter=AMR", "-M")
    events = OrderedDict()          # path -> (date, status, sha, subject)
    cur = None
    for line in raw.splitlines():
        if line.startswith("C|"):
            _, d, sha, subj = line.split("|", 3)
            cur = (d, sha, subj)
            continue
        if not line.strip() or cur is None:
            continue
        parts = line.split("\t")
        status, path = parts[0], parts[-1]
        if os.path.splitext(path)[1] not in CONTENT_EXT:
            continue
        if os.path.basename(path) in SKIP_NAMES:
            continue
        if status == "R100":
            continue                # pure move: the doc did not change
        if not os.path.exists(os.path.join(REPO, path)):
            continue                # deleted or since renamed away
        if path in events:
            continue                # git log is newest-first; keep the newest
        d, sha, subj = cur
        events[path] = (d, "NEW" if status.startswith("A") else "UPD", sha, subj)
    return events


def render(events, days, limit, collapse):
    listed = list(events.items())[:limit]
    omitted = len(events) - len(listed)
    by_date = OrderedDict()          # date -> commit sha -> (subject, [entries])
    for path, (d, status, sha, subj) in listed:
        commits = by_date.setdefault(d, OrderedDict())
        commits.setdefault(sha, (subj, []))[1].append((status, path))

    head_sha = git("rev-parse", "--short", "HEAD").strip()
    out = []
    out.append("# Recent Docs")
    out.append("")
    out.append("Shortcut index of the most recently added or updated documents, newest first. "
               "Use this to jump back into whatever you were last working on; use "
               "[README.md](README.md) when you want the full tree by category.")
    out.append("")
    out.append(f"*Generated from git history on {date.today().isoformat()} "
               f"(HEAD `{head_sha}`), covering the last {days} days. "
               "`NEW` = added in that commit, `UPD` = updated.*")
    out.append("")

    flat = [(d, st, p) for d, commits in by_date.items()
            for _subj, items in commits.values() for st, p in items]
    out.append("## At a glance — 10 most recent")
    out.append("")
    out.append("| Date | | Document | Category |")
    out.append("|---|---|---|---|")
    for d, status, path in flat[:10]:
        out.append(f"| {d} | `{status}` | [{title_of(path)}]({path}) | {category_of(path)} |")
    out.append("")

    out.append("## Full timeline")
    out.append("")
    for d, commits in by_date.items():
        total = sum(len(items) for _subj, items in commits.values())
        plural = "doc" if total == 1 else "docs"
        out.append(f"### {d} — {total} {plural}")
        out.append("")
        for sha, (subj, items) in commits.items():
            out.append(f"**{subj}** (`{sha}`)")
            out.append("")
            for status, path in items[:collapse]:
                out.append(f"- `{status}` [{title_of(path)}]({path}) — *{category_of(path)}*")
            extra = len(items) - collapse
            if extra > 0:
                out.append(f"- *…and {extra} more in this commit — "
                           f"`git show --stat {sha}`*")
            out.append("")
    if omitted > 0:
        out.append(f"*{omitted} older entries not shown. "
                   f"Run `python3 scripts/gen-recent.py --limit {len(events)}` for the full list, "
                   "or browse [README.md](README.md) by category.*")
        out.append("")

    out.append("---")
    out.append("")
    out.append("## Regenerating this file")
    out.append("")
    out.append("This file is generated — do not edit it by hand.")
    out.append("")
    out.append("```bash")
    out.append("python3 scripts/gen-recent.py              # newest 60 docs")
    out.append("python3 scripts/gen-recent.py --limit 200  # go further back")
    out.append("```")
    out.append("")
    out.append("Index `README.md` files and pure file moves are deliberately excluded, so this "
               "lists real authoring activity rather than index churn or directory reshuffles.")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--limit", type=int, default=60,
                    help="maximum documents to list (default 60)")
    ap.add_argument("--collapse", type=int, default=8,
                    help="max files shown per commit before collapsing (default 8)")
    ap.add_argument("--min", type=int, default=25,
                    help="widen the window until at least this many docs are listed")
    args = ap.parse_args()

    days = args.days
    events = collect(days)
    while len(events) < args.min and days < 2000:
        days *= 2
        events = collect(days)

    target = os.path.join(REPO, "RECENT.md")
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(render(events, days, args.limit, args.collapse))
    print(f"wrote RECENT.md — {min(len(events), args.limit)} of {len(events)} documents over the last {days} days")


if __name__ == "__main__":
    sys.exit(main())
