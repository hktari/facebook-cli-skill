

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

# 2. Create new listing modal
agent-browser --cdp ${cdp_port} click $(agent-browser --cdp ${cdp_port} snapshot | grep "Item for sale" | grep -oP '\[ref=\K[^\]]+')

 # 3. Item for sale modal
 agent-browser --cdp ${cdp_port} type e20 "${post_title}"
 agent-browser --cdp ${cdp_port} click e22
 agent-browser --cdp ${cdp_port} click e26
 agent-browser --cdp ${cdp_port} click e27
 agent-browser --cdp ${cdp_port} click e23
 agent-browser --cdp ${cdp_port} type e24 "${post_description}"
 agent-browser --cdp ${cdp_port} fill e26 "${city}"
 sleep 2 # Wait for dropdown
 agent-browser --cdp ${cdp_port} click e37
 agent-browser --cdp ${cdp_port} upload 'input[type="file"][accept="image/*,image/heif,image/heic"]' "${marketing_image_abs_path}"
 sleep 5 # Wait for upload
 agent-browser --cdp ${cdp_port} click e34
 
 # 4. share to more places dialog
 agent-browser --cdp ${cdp_port} click e25

 # 5. listing published dialog
 agent-browser --cdp ${cdp_port} get text e13 # Should print "Listing published"
 agent-browser --cdp ${cdp_port} click e14