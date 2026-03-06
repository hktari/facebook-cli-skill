#!/bin/bash

set -euo pipefail

cdp_port="${1:-9222}"
profile_dir="${2:-$(pwd)/.chrome-profile}"

find_chrome() {
  local candidates=(
    "google-chrome"
    "chromium"
    "chromium-browser"
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    "/Applications/Chromium.app/Contents/MacOS/Chromium"
  )

  for candidate in "${candidates[@]}"; do
    if command -v "$candidate" >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return 0
    fi
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  return 1
}

chrome_bin="$(find_chrome || true)"
if [ -z "$chrome_bin" ]; then
  echo "Chrome or Chromium executable not found." >&2
  exit 1
fi

mkdir -p "$profile_dir"

"$chrome_bin" \
  --remote-debugging-port="$cdp_port" \
  --user-data-dir="$profile_dir" \
  --no-first-run \
  --no-default-browser-check \
  --disable-extensions \
  about:blank >/dev/null 2>&1 &

echo "Started Chrome with CDP on port $cdp_port using profile $profile_dir"
