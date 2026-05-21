#!/usr/bin/env bash
# Budtags status line: directory, branch, diff stats, model, and context /
# 5-hour / weekly usage. Bundled with the plugin so it travels across machines.
input=$(cat)

# Extract status fields in a single python3 pass. python3 is used instead of
# `grep -oP` because macOS ships BSD grep, which has no Perl-regex -P flag --
# the grep approach renders the bar blank on macOS. python3 is cross-platform
# and the plugin already depends on it for its hooks.
eval "$(printf '%s' "$input" | python3 -c '
import json, shlex, sys

try:
    data = json.load(sys.stdin)
except Exception:
    data = {}


def get(*keys):
    value = data
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return ""
    return "" if value is None else str(value)


fields = [
    ("cwd", ("workspace", "current_dir")),
    ("model", ("model", "display_name")),
    ("used", ("context_window", "used_percentage")),
    ("rate_5h", ("rate_limits", "five_hour", "used_percentage")),
    ("rate_7d", ("rate_limits", "seven_day", "used_percentage")),
]
for name, path in fields:
    print("%s=%s" % (name, shlex.quote(get(*path))))
' 2>/dev/null)"

# Color a percentage value: green < 50, yellow 50-80, red 80+
color_pct() {
  local label="$1" val="$2"
  local val_int
  val_int=$(printf '%.0f' "$val" 2>/dev/null) || return
  [ "$val_int" -eq 0 ] 2>/dev/null && return
  local color
  if [ "$val_int" -ge 80 ]; then
    color='\033[0;31m'
  elif [ "$val_int" -ge 50 ]; then
    color='\033[0;33m'
  else
    color='\033[0;32m'
  fi
  printf "${color}%s:%s%%\033[0m" "$label" "$val_int"
}

# Parse insertions/deletions from git shortstat output
parse_shortstat() {
  local stat="$1"
  local ins del
  ins=$(echo "$stat" | sed -n 's/.* \([0-9]*\) insertion.*/\1/p')
  del=$(echo "$stat" | sed -n 's/.* \([0-9]*\) deletion.*/\1/p')
  echo "${ins:-0} ${del:-0}"
}

# Format number with k suffix for thousands
format_num() {
  local n=$1
  if [ "$n" -ge 1000 ] 2>/dev/null; then
    awk "BEGIN {printf \"%.1fk\", $n/1000}"
  else
    echo "$n"
  fi
}

# Abbreviate relative time (e.g. "5 minutes ago" -> "5m")
shorten_age() {
  echo "$1" | sed -E \
    's/ seconds? ago/s/;
     s/ minutes? ago/m/;
     s/ hours? ago/h/;
     s/ days? ago/d/;
     s/ weeks? ago/w/;
     s/ months? ago/mo/;
     s/ years? ago/y/'
}

# Shorten model name (strip "Claude " prefix)
model="${model#Claude }"
# Strip context size suffix like " (1M context)"
model=$(echo "$model" | sed 's/ ([^)]*context)$//')

# Git info with 5-second file cache
CACHE_FILE="/tmp/statusline-git-cache"
CACHE_MAX_AGE=5

cache_is_stale() {
  [ ! -f "$CACHE_FILE" ] || \
  [ $(($(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || stat -f %m "$CACHE_FILE" 2>/dev/null || echo 0))) -gt $CACHE_MAX_AGE ]
}

branch=""
total_ins=0
total_del=0
today_ins=0
today_del=0
last_commit=""

if [ -n "$cwd" ] && [ -d "$cwd/.git" ]; then
  if cache_is_stale; then
    _branch=$(git -C "$cwd" --no-optional-locks branch --show-current 2>/dev/null)

    # Uncommitted changes (working tree + staged)
    _unstaged=$(git -C "$cwd" --no-optional-locks diff --shortstat 2>/dev/null)
    _staged=$(git -C "$cwd" --no-optional-locks diff --cached --shortstat 2>/dev/null)

    read _u_ins _u_del <<< "$(parse_shortstat "$_unstaged")"
    read _s_ins _s_del <<< "$(parse_shortstat "$_staged")"
    _total_ins=$((_u_ins + _s_ins))
    _total_del=$((_u_del + _s_del))

    # Today's commit stats
    _today_stats=$(git -C "$cwd" --no-optional-locks log --author="Jason" --since="midnight" --shortstat --format="" 2>/dev/null \
      | awk '{ins+=$4; del+=$6} END {print ins+0, del+0}')
    _today_ins=$(echo "$_today_stats" | awk '{print $1}')
    _today_del=$(echo "$_today_stats" | awk '{print $2}')

    # Last commit age
    _last_commit=$(git -C "$cwd" --no-optional-locks log -1 --format="%cr" 2>/dev/null)

    # Write cache
    printf '%s\n%s\n%s\n%s\n%s\n%s\n' \
      "$_branch" "$_total_ins" "$_total_del" "$_today_ins" "$_today_del" "$_last_commit" \
      > "$CACHE_FILE"
  fi

  # Read from cache
  { read -r branch; read -r total_ins; read -r total_del; read -r today_ins; read -r today_del; read -r last_commit; } < "$CACHE_FILE"
fi

# Build status line
parts=()

# Directory (blue)
if [ -n "$cwd" ]; then
  parts+=("$(printf '\033[0;34m%s\033[0m' "$(basename "$cwd")")")
fi

# Branch (magenta)
if [ -n "$branch" ]; then
  parts+=("$(printf '\033[0;35m(%s)\033[0m' "$branch")")
fi

# Uncommitted changes (green +N / red -N)
if [ "$total_ins" -gt 0 ] || [ "$total_del" -gt 0 ]; then
  diff_str=""
  if [ "$total_ins" -gt 0 ]; then
    diff_str="$(printf '\033[0;32m+%s\033[0m' "$total_ins")"
  fi
  if [ "$total_del" -gt 0 ]; then
    [ -n "$diff_str" ] && diff_str="$diff_str "
    diff_str="${diff_str}$(printf '\033[0;31m-%s\033[0m' "$total_del")"
  fi
  parts+=("$diff_str")
fi

# Today's commit stats (dim label, green/red values)
if [ "$today_ins" -gt 0 ] || [ "$today_del" -gt 0 ]; then
  t_ins=$(format_num "$today_ins")
  t_del=$(format_num "$today_del")
  parts+=("$(printf '\033[0;90mtoday:\033[0;32m+%s\033[0;90m/\033[0;31m-%s\033[0m' "$t_ins" "$t_del")")
fi

# Last commit age (dim gray)
if [ -n "$last_commit" ]; then
  parts+=("$(printf '\033[0;90m%s\033[0m' "$(shorten_age "$last_commit")")")
fi

# Model (cyan)
if [ -n "$model" ]; then
  parts+=("$(printf '\033[0;36m%s\033[0m' "$model")")
fi

# Context usage (green / yellow / red)
if [ -n "$used" ]; then
  ctx_str=$(color_pct "ctx" "$used")
  [ -n "$ctx_str" ] && parts+=("$ctx_str")
fi

# Rate limits (green / yellow / red, hidden when 0%)
if [ -n "$rate_5h" ]; then
  r5_str=$(color_pct "5h" "$rate_5h")
  [ -n "$r5_str" ] && parts+=("$r5_str")
fi

if [ -n "$rate_7d" ]; then
  r7_str=$(color_pct "7d" "$rate_7d")
  [ -n "$r7_str" ] && parts+=("$r7_str")
fi

printf '%s' "${parts[*]}"
