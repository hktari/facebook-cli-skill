#!/bin/bash

set -euo pipefail

group_url="${1:?group_url is required}"
cdp_port="${2:-9222}"

agent-browser --cdp "$cdp_port" open "$group_url" >/dev/null
sleep 5

snapshot="$(agent-browser --cdp "$cdp_port" snapshot)"

if printf '%s\n' "$snapshot" | grep -q 'Sell Something\|Sell something'; then
  echo "sell"
  exit 0
fi

echo "regular"
