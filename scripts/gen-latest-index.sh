#!/usr/bin/env bash
# Regenerate LATEST.md — a recency-ordered index of articles.
#
# Article date = the commit date when the file FIRST appeared in git history,
# traced through renames with `git log --follow`. This means a file that was
# only moved during a directory reorganisation keeps its original date.
#
# Usage:  ./scripts/gen-latest-index.sh [N]     (N = how many recent articles to list, default 40)
set -euo pipefail
cd "$(dirname "$0")/.."

TOP="${1:-40}"
OUT="LATEST.md"
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

git -c core.quotepath=false ls-files '*.md' '*.ipynb' \
  | grep -viE '(^|/)README\.md$' \
  | grep -viE '^LATEST\.md$' \
  | while IFS= read -r f; do
      d=$(git log --follow --diff-filter=A --format=%cd --date=short -1 -- "$f" 2>/dev/null || true)
      [ -z "$d" ] && d="0000-00-00"
      t=""
      case "$f" in
        *.md)
          t=$(grep -m1 '^# ' "$f" 2>/dev/null | sed 's/^# *//' || true)
          [ -z "$t" ] && t=$(awk '/^title:/{sub(/^title: *"?/,""); sub(/"$/,""); print; exit}' "$f" 2>/dev/null || true)
          ;;
        *.ipynb) t="" ;;
      esac
      [ -z "$t" ] && t="$(basename "$f")"
      case "$f" in *.ipynb) t="$t (notebook)";; esac
      printf '%s\t%s\t%s\n' "$d" "$f" "$t"
    done | sort -r > "$TMP"

total=$(wc -l < "$TMP" | tr -d ' ')
generated=$(date +%Y-%m-%d)

cat > "$OUT" <<HEADER
# 最近更新 / Latest Articles

按加入仓库的时间倒序排列，最新的在最前面。共 **${total}** 篇文章。

[← 返回总索引](./README.md)

> 本页由 \`scripts/gen-latest-index.sh\` 生成，请勿手工编辑。
> 日期取自该文件**首次进入 git 历史**的提交日期（经 \`--follow\` 追踪重命名），
> 因此仅被目录重组移动过的文件仍保留其原始日期。
> 生成时间：${generated}

## 最新 ${TOP} 篇

HEADER

# --- recent articles, grouped by month ---
head -n "$TOP" "$TMP" | awk -F'\t' -v OFS='' '
  {
    month = substr($1, 1, 7)
    if (month != prev) {
      if (prev != "") print ""
      print "### " month
      print ""
      prev = month
    }
    # category = first path segment (or "root")
    n = split($2, seg, "/")
    cat = (n > 1) ? seg[1] : "root"
    print "- `" $1 "` · **" cat "** — [" $3 "](" $2 ")"
  }
' >> "$OUT"

# --- monthly activity, last 12 months with content ---
{
  printf '\n## 近 12 个月新增数量\n\n'
  printf '| 月份 | 新增文章 |\n|---|---|\n'
  cut -f1 "$TMP" | cut -c1-7 | grep -v '^0000' | sort -r | uniq -c \
    | head -12 | awk '{printf "| %s | %s |\n", $2, $1}'
} >> "$OUT"

# --- per-category totals ---
{
  printf '\n## 各分类文章总数\n\n'
  printf '| 分类 | 文章数 |\n|---|---|\n'
  cut -f2 "$TMP" | awk -F/ '{print (NF>1 ? $1 : "root")}' | sort | uniq -c | sort -rn \
    | awk '{printf "| %s | %s |\n", $2, $1}'
} >> "$OUT"

echo "Wrote $OUT ($total articles, top $TOP listed)"
