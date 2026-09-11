#!/usr/bin/env python3
"""Regenerate LATEST.md — the repo's recency index.

Two sections, answering two different questions:

  1. 最近改动 / Recently added or updated — "what have I touched lately?"
     Most recent add-or-update per file, newest first, tagged NEW or UPD.
  2. 全部文章 · 按加入时间 / All articles by date added — "when did I write this?"
     Every article dated by when it FIRST entered git history, traced through
     renames with `git log --follow`, grouped by month.

Usage:  python3 scripts/gen-latest.py [--recent N] [--collapse N]

Deliberately excluded from section 1 so it stays a shortcut, not a changelog:
generated README.md / index.md churn, and pure renames (a file moved without
content changes is not a doc event).
"""
import argparse
import os
import re
import subprocess
import sys
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_NAMES = {"README.md", "index.md", "LATEST.md"}
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
    if path.endswith(".ipynb"):
        return os.path.basename(path) + " (notebook)"
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


def top_level(path):
    return path.split("/")[0] if "/" in path else "root"


def category_of(path):
    if "/" not in path:
        return "Root"
    parts = path.split("/")
    label = CATEGORY_LABELS.get(parts[0], parts[0])
    return f"{label} / {parts[1]}" if len(parts) > 2 else label


def is_content(path):
    return (os.path.splitext(path)[1] in CONTENT_EXT
            and os.path.basename(path) not in SKIP_NAMES)


# --------------------------------------------------------------------------
# Section 1 — recent activity
# --------------------------------------------------------------------------
def recent_events():
    raw = git("log", "--date=short", "--pretty=format:C|%ad|%h|%s",
              "--name-status", "--diff-filter=AMR", "-M")
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
        if not is_content(path) or status == "R100":
            continue                # R100 = pure move: the doc did not change
        if not os.path.exists(os.path.join(REPO, path)) or path in events:
            continue                # deleted/renamed away, or newer event kept
        d, sha, subj = cur
        events[path] = (d, "NEW" if status.startswith("A") else "UPD", sha, subj)
    return events


# --------------------------------------------------------------------------
# Section 2 — full catalogue by date added
# --------------------------------------------------------------------------
def added_date(path):
    out = git("log", "--follow", "--diff-filter=A", "--format=%cd",
              "--date=short", "-1", "--", path).strip()
    return out.splitlines()[0] if out else "0000-00-00"


def catalogue():
    files = [f for f in git("-c", "core.quotepath=false", "ls-files",
                            "*.md", "*.ipynb").splitlines() if is_content(f)]
    with ThreadPoolExecutor(max_workers=8) as pool:
        dates = list(pool.map(added_date, files))
    rows = sorted(zip(dates, files), key=lambda r: (r[0], r[1]), reverse=True)
    return rows


# --------------------------------------------------------------------------
def render(events, rows, recent_limit, collapse):
    listed = list(events.items())[:recent_limit]
    omitted = len(events) - len(listed)
    by_date = OrderedDict()
    for path, (d, status, sha, subj) in listed:
        by_date.setdefault(d, OrderedDict()).setdefault(sha, (subj, []))[1].append((status, path))

    head_sha = git("rev-parse", "--short", "HEAD").strip()
    o = []
    o.append("# 最近更新 / Latest Articles")
    o.append("")
    o.append("[← 返回总索引](./README.md)")
    o.append("")
    o.append("> 本页由 `scripts/gen-latest.py` 生成，请勿手工编辑。")
    o.append(f"> 生成时间：{date.today().isoformat()}（HEAD `{head_sha}`）")
    o.append("")

    # ---- Section 1 ----
    o.append("## 最近改动 / Recently added or updated")
    o.append("")
    o.append("回答「我最近动过什么」。`NEW` = 新增，`UPD` = 修改；按改动时间倒序。")
    o.append("已忽略 `README.md`/`index.md` 索引更新与纯目录移动，只列真正的文章改动。")
    o.append("")
    o.append("| 日期 | | 文档 | 分类 |")
    o.append("|---|---|---|---|")
    flat = [(d, st, p) for d, commits in by_date.items()
            for _s, items in commits.values() for st, p in items]
    for d, status, path in flat[:10]:
        o.append(f"| {d} | `{status}` | [{title_of(path)}]({path}) | {category_of(path)} |")
    o.append("")
    for d, commits in by_date.items():
        total = sum(len(items) for _s, items in commits.values())
        o.append(f"### {d} — {total} 篇")
        o.append("")
        for sha, (subj, items) in commits.items():
            o.append(f"**{subj}** (`{sha}`)")
            o.append("")
            for status, path in items[:collapse]:
                o.append(f"- `{status}` [{title_of(path)}]({path}) — *{category_of(path)}*")
            extra = len(items) - collapse
            if extra > 0:
                o.append(f"- *…此次提交还有 {extra} 篇 — `git show --stat {sha}`*")
            o.append("")
    if omitted > 0:
        o.append(f"*另有 {omitted} 条更早的改动未列出（见下方完整目录）。*")
        o.append("")

    # ---- Section 2 ----
    o.append(f"## 全部文章 · 按加入时间 / All articles by date added（共 {len(rows)} 篇）")
    o.append("")
    o.append("回答「这篇是什么时候写的」。日期取自该文件**首次进入 git 历史**的提交")
    o.append("（经 `--follow` 追踪重命名），因此仅被目录重组移动过的文件仍保留原始日期。")
    o.append("")
    cur_month = None
    for d, path in rows:
        month = d[:7]
        if month != cur_month:
            cur_month = month
            o.append("")
            o.append(f"### {month}")
            o.append("")
        o.append(f"- `{d}` · **{top_level(path)}** — [{title_of(path)}]({path})")
    o.append("")

    o.append("---")
    o.append("")
    o.append("## 重新生成 / Regenerating")
    o.append("")
    o.append("```bash")
    o.append("python3 scripts/gen-latest.py                # 默认：最近 30 条改动 + 完整目录")
    o.append("python3 scripts/gen-latest.py --recent 60    # 列出更多改动")
    o.append("```")
    o.append("")
    o.append("生成器读取的是**已提交**的 git 历史，因此请在文章提交落地之后再运行。")
    return "\n".join(o) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recent", type=int, default=30,
                    help="max entries in the recent-activity section (default 30)")
    ap.add_argument("--collapse", type=int, default=8,
                    help="max files shown per commit before collapsing (default 8)")
    args = ap.parse_args()

    events, rows = recent_events(), catalogue()
    with open(os.path.join(REPO, "LATEST.md"), "w", encoding="utf-8") as fh:
        fh.write(render(events, rows, args.recent, args.collapse))
    print(f"wrote LATEST.md — {min(len(events), args.recent)} recent changes, "
          f"{len(rows)} articles catalogued")


if __name__ == "__main__":
    sys.exit(main())
