# Instructions on using `agent-browser` to perform common workflows

## Setup browser session
1. run `./scripts/start-facebook-browser.sh 9222 ./.chrome-profile`
2. log into Facebook inside that sandboxed browser profile if the session is not already present
3. run `agent-browser connect 9222`. Should print `done`.

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
./scripts/create-sale-post.sh "${post_title}" "${post_description}" "${city}" "${marketing_image_abs_path}" "${fb_group_url}" 9222
```

### unified group posting entrypoint

```bash
./scripts/post-to-facebook-group.sh "${post_title}" "${post_description}" "${city}" "${marketing_image_abs_path}" "${fb_group_url}" 9222
```

This entrypoint checks whether the group exposes `Sell something` and routes accordingly.
