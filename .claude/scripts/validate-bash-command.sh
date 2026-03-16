#!/usr/bin/env bash
set -euo pipefail

cmd="${1:-}"

if [[ -z "$cmd" ]]; then
  exit 0
fi

blocked_patterns=(
  "rm -rf /"
  "curl .*\\| sh"
  "wget .*\\| sh"
  "drop table"
  "truncate table"
  "git push --force"
)

for pattern in "${blocked_patterns[@]}"; do
  if [[ "$cmd" =~ $pattern ]]; then
    echo "Blocked unsafe command pattern: $pattern" >&2
    exit 1
  fi
done

exit 0
