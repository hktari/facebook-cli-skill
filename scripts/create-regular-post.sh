#!/bin/bash

set -euo pipefail

post_title="${1:?post_title is required}"
post_description="${2:?post_description is required}"
city="${3:?city is required}"
marketing_image_abs_path="${4:?image path is required}"
fb_group_url="${5:?group url is required}"
cdp_port="${6:-9222}"

snapshot() {
  agent-browser --cdp "$cdp_port" snapshot
}

find_ref() {
  local label="$1"
  local pattern="$2"
  local ref

  ref="$(snapshot | grep -E "$pattern" | head -n 1 | grep -oP '\[ref=\K[^\]]+' || true)"

  if [ -z "$ref" ]; then
    echo "Could not find selector for: $label" >&2
    return 1
  fi

  printf '%s\n' "$ref"
}

click_ref() {
  local label="$1"
  local pattern="$2"
  local ref

  ref="$(find_ref "$label" "$pattern")"
  agent-browser --cdp "$cdp_port" click "$ref"
}

type_ref() {
  local label="$1"
  local pattern="$2"
  local value="$3"
  local ref

  ref="$(find_ref "$label" "$pattern")"
  agent-browser --cdp "$cdp_port" type "$ref" "$value"
}

fill_ref() {
  local label="$1"
  local pattern="$2"
  local value="$3"
  local ref

  ref="$(find_ref "$label" "$pattern")"
  agent-browser --cdp "$cdp_port" fill "$ref" "$value"
}

get_text_ref() {
  local label="$1"
  local pattern="$2"
  local ref

  ref="$(find_ref "$label" "$pattern")"
  agent-browser --cdp "$cdp_port" get text "$ref"
}

agent-browser --cdp "$cdp_port" open "$fb_group_url"

click_ref "Write post button" 'button "Write something..."'

sleep 5

post_content="$post_title"
post_content+=$'\n'
post_content+="$post_description"
type_ref "Post input field" "textbox" "$post_content"

click_ref "Add to your post" "button \"Add to your post\""

sleep 3

agent-browser --cdp "$cdp_port" upload 'div[role="dialog"] + div input[type="file"][accept^="image/"]' "$marketing_image_abs_path"

sleep 10

click_ref "Post" "button \"Post\""

sleep 10

get_text_ref "Write post button" 'button "Write something..."' && echo "Post created successfully" || echo "Failed to create post"

