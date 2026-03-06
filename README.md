
# Facebook Marketing Agent

Shell-based Facebook group posting automation built around a CDP-enabled Chrome or Chromium browser and `agent-browser` workflows.

## Current interface

- `scripts/start-facebook-browser.sh [cdp_port] [profile_dir]`
- `scripts/post-to-facebook-group.sh <post_title> <post_description> <city> <image_path> <group_url> [cdp_port]`

## Behavior

- starts or reuses a sandboxed Chrome profile with CDP enabled
- routes posting through a single shell entrypoint
- detects whether the target group exposes `Sell something`
- uses the sales-post flow when that button is present
- falls back to the regular-post flow scaffold otherwise

## Requirements

- `agent-browser` available on `PATH`
- Chrome or Chromium installed
- a sandboxed browser profile with a valid Facebook login session

## Notes

- the sell-item flow is implemented
- the regular post flow remains a scaffold for collaborative completion
- the implementation is Unix-oriented

## Next step

- implement the regular post workflow inside `scripts/create-regular-post.sh`
