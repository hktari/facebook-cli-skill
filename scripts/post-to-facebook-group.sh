#!/bin/bash

set -euo pipefail

post_title="${1:?post_title is required}"
post_description="${2:?post_description is required}"
city="${3:?city is required}"
marketing_image_abs_path="${4:?image path is required}"
fb_group_url="${5:?group url is required}"
cdp_port="${6:-9222}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mode="$($script_dir/detect-facebook-post-mode.sh "$fb_group_url" "$cdp_port")"

if [ "$mode" = "sell" ]; then
  exec "$script_dir/create-sale-post.sh" "$post_title" "$post_description" "$city" "$marketing_image_abs_path" "$fb_group_url" "$cdp_port"
fi

exec "$script_dir/create-regular-post.sh" "$post_title" "$post_description" "$city" "$marketing_image_abs_path" "$fb_group_url" "$cdp_port"
