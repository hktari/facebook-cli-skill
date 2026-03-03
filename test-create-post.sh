#!/bin/bash

# Exit on any command failure
set -e

# Configuration
post_title="${1:-Your Post Title}"
post_description="${2:-Your Post Description}"
city="${3:-Maribor}"
marketing_image_abs_path="${4:-/path/to/your/image.jpg}"
fb_group_url="${5:-https://www.facebook.com/groups/autooglasinis}"
cdp_port="${6:-9222}"

agent-browser --cdp ${cdp_port} open "${fb_group_url}"

# 1. First page
agent-browser --cdp ${cdp_port} click  $(agent-browser --cdp ${cdp_port} snapshot | grep "Sell Something" | grep -oP '\[ref=\K[^\]]+')

sleep 5

# 2. Create new listing modal
agent-browser --cdp ${cdp_port} click $(agent-browser --cdp ${cdp_port} snapshot | grep "Item for sale" | grep -oP '\[ref=\K[^\]]+')

sleep 5

# 3. Item for sale modal
agent-browser --cdp ${cdp_port} type $(agent-browser --cdp ${cdp_port} snapshot | grep 'textbox "Title"' | grep -oP '\[ref=\K[^\]]+') "${post_title}"
agent-browser --cdp ${cdp_port} click $(agent-browser --cdp ${cdp_port} snapshot | grep 'combobox "Condition"' | grep -oP '\[ref=\K[^\]]+')
agent-browser --cdp ${cdp_port} click $(agent-browser --cdp ${cdp_port} snapshot | grep 'option "New"' | grep -oP '\[ref=\K[^\]]+')
agent-browser --cdp ${cdp_port} type $(agent-browser --cdp ${cdp_port} snapshot | grep 'textbox "Price"' | grep -oP '\[ref=\K[^\]]+') 1
agent-browser --cdp ${cdp_port} click $(agent-browser --cdp ${cdp_port} snapshot | grep 'button "More details' | grep -oP '\[ref=\K[^\]]+')
agent-browser --cdp ${cdp_port} type $(agent-browser --cdp ${cdp_port} snapshot | grep 'textbox "Description"' | grep -oP '\[ref=\K[^\]]+') "${post_description}"
agent-browser --cdp ${cdp_port} type $(agent-browser --cdp ${cdp_port} snapshot | grep 'combobox "Location"' | grep -oP '\[ref=\K[^\]]+') "${city}"
sleep 2 # Wait for dropdown
agent-browser --cdp ${cdp_port} click $(agent-browser --cdp ${cdp_port} snapshot | grep "option \"${city}" | grep "\[nth=1\]" | grep -oP '\[ref=\K[^\]]+')
agent-browser --cdp ${cdp_port} upload 'input[type="file"][accept="image/*,image/heif,image/heic"]' "${marketing_image_abs_path}"
sleep 5 # Wait for upload
agent-browser --cdp ${cdp_port} click $(agent-browser --cdp ${cdp_port} snapshot | grep 'button "Next"' | grep -oP '\[ref=\K[^\]]+')

sleep 5

# 4. share to more places dialog
agent-browser --cdp ${cdp_port} click $(agent-browser --cdp ${cdp_port} snapshot | grep 'button "Post"' | grep -oP '\[ref=\K[^\]]+')

sleep 10

# 5. listing published dialog
agent-browser --cdp ${cdp_port} get text $(agent-browser --cdp ${cdp_port} snapshot | grep 'heading "Listing published"' | grep -oP '\[ref=\K[^\]]+')
agent-browser --cdp ${cdp_port} click $(agent-browser --cdp ${cdp_port} snapshot | grep 'button "Close"' | grep -oP '\[ref=\K[^\]]+')