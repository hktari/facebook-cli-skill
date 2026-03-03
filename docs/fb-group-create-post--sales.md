# Instructions on using `agent-browser` to perform common workflows

## Setup browser session
1. run "uv run export-auth.py" to get facebook cookies
2. run "uv run start-chrome-with-user-profile.py" to start a chrome browser with CDP debug port, and set cookies
3. run "agent-browser connect 9222". Should print "done". Browser with user's cookies is ready for workflow executions.

## Best practices
*TODO*:review this 
1. make sure to cleanup and kill chrome process

## Workflows
**IMPORTANT**: make sure you've setup the browser session before executing workflows

### create a sales post inside a facebook group
#### About
certain facebook groups allow make sales posts only. This requires special handling when making posts. 

#### Step by step instructions
```bash
 # 1. First page
 agent-browser click e53
 
 # 2. Create new listing modal
 agent-browser click e15

 # 3. Item for sale modal
 agent-browser --cdp 9222 type e20 "${post_title}"
 agent-browser --cdp 9222 click e22
 agent-browser --cdp 9222 click e26
 agent-browser --cdp 9222 click e27
 agent-browser --cdp 9222 click e23
 agent-browser --cdp 9222 type e24 "${post_description}"
 agent-browser --cdp 9222 type e26 "Maribor"
 agent-browser --cdp 9222 type e26 "Maribor" --clear
 agent-browser --cdp 9222 clear e26
 agent-browser --cdp 9222 fill e26 "${city}"
 agent-browser --cdp 9222 click e37
 agent-browser upload 'input[type="file"][accept="image/*,image/heif,image/heic"]' ${marketing_image_abs_path}
 agent-browser --cdp 9222 click e34
 
 # 4. share to more places dialog
 agent-browser --cdp 9222 click e25

 # 5. listing published dialog
 agent-browser --cdp 9222 get text e13 # Should print "Listing published"
 agent-browser --cdp 9222 click e14
 ```
