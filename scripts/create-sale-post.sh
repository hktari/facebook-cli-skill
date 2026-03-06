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

click_ref "Sell something button" 'Sell Something|Sell something'

sleep 5

click_ref "Item for sale option" 'Item for sale'

sleep 5

type_ref "Title textbox" 'textbox "Title"' "$post_title"
click_ref "Condition combobox" 'combobox "Condition"'
click_ref "New condition option" 'option "New"'
type_ref "Price textbox" 'textbox "Price"' 1
click_ref "More details button" 'button "More details'
type_ref "Description textbox" 'textbox "Description"' "$post_description"
fill_ref "Location combobox" 'combobox "Location"' "$city"
sleep 2
click_ref "Location option" "option \"${city}.*\\[nth=1\\]"
agent-browser --cdp "$cdp_port" upload 'input[type="file"][accept="image/*,image/heif,image/heic"]' "$marketing_image_abs_path"
sleep 5
click_ref "Next button" 'button "Next"'

sleep 5

click_ref "Post button" 'button "Post"'

sleep 10

get_text_ref "Listing published heading" 'heading "Listing published"'
click_ref "Close button" 'button "Close"'
