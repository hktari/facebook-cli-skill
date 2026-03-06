---
name: facebook-group-posting
description: Automate posting to Facebook groups using a CDP-enabled Chrome browser with a logged-in Facebook session. Use this skill to start the browser session and create a group post through a single shell-based interface that detects whether the group supports a sell-item flow.
---

# Facebook Group Posting Skill

## When to use

Use this skill when you need to:
- start a Chrome or Chromium browser with CDP enabled for Facebook automation
- reuse a sandboxed Facebook-authenticated session
- create a Facebook group post through one unified interface

## Requirements

- `agent-browser` must be installed and available on `PATH`
- Chrome or Chromium must be installed
- the browser session must be started with CDP before posting
- the sandboxed browser profile must already contain a valid Facebook login session

## Interface

### 1. Start browser session

```bash
./scripts/start-facebook-browser.sh [cdp_port] [profile_dir]
```

Starts a sandboxed Chrome or Chromium instance with CDP enabled.

### 2. Make a Facebook group post

```bash
./scripts/post-to-facebook-group.sh <post_title> <post_description> <city> <image_path> <group_url> [cdp_port]
```

The script detects whether the group supports the sell-item flow by checking for the `Sell something` button. If present, it routes to the sales-post workflow. Otherwise it routes to the regular-post workflow.

## Notes

- The current regular-post workflow is intentionally left as a scaffold for collaborative completion.
- The sell-item flow is implemented from the existing proof-of-concept shell script.
- This skill is Unix-oriented and does not target Windows support.
