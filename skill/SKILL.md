---
name: facebook-group-posting
description: Automate Facebook group posting through the maintained Python CLI. Use this skill when you need to make a post in a Facebook group.
---

# Facebook Group Posting Skill

## Requirements

- Python 3.12+
- `agent-browser` must be installed and available on `PATH`
- Chrome or Chromium must be installed and runnable on the machine
- the browser session must be started with CDP before posting
- the sandboxed browser profile must already contain a valid Facebook login session

## Install Chrome or Chromium

If Chrome or Chromium is not already installed, install one of them before using this skill.

Common Linux package names:

- `google-chrome`
- `chromium`
- `chromium-browser`

The Python CLI auto-detects these executable names when starting the browser.

## Install agent-browser
- check if agent-browser is already installed: `agent-browser --version`
- if not installed, see instructions at: https://github.com/vercel-labs/agent-browser on how to install

<!-- 1. run `python3 facebook_group_poster.py start-browser 9222 ./.chrome-profile`
2. log into Facebook inside that sandboxed browser profile if the session is not already present
3. run `agent-browser connect 9222`. Should print `done`.

`facebook_group_poster.py` contains the maintained workflow logic. -->

## Best practices
*TODO*:review this 
1. make sure to cleanup and kill chrome process

## How to use

1. check dependencies are installed:
   1.1 check if agent-browser is installed: `agent-browser --version`
   1.2 check if chrome or chromium is installed: `google-chrome --version` or `chromium --version`
   
   if any is missing you must first install them

2. check if a chrome browser instance with CDP is running: 
   run `agent-browser connect 9222`. Should print `done`. If not, start chrome browser and prompt the user to log into Facebook account. 

## Interface

### Primary entrypoint

```bash
python3 facebook_group_poster.py post-to-facebook-group <post_title> <post_description> <city> <image_path> <group_url> [cdp_port]
```

Use this for the normal user-facing task: make a Facebook group post. The script will detect whether the group exposes the `Sell something` flow and route to the correct implementation.

### Setup browser session

```bash
python3 facebook_group_poster.py start-browser [cdp_port] [profile_dir]
```

Use this when you need to bootstrap or reuse the sandboxed Chrome profile.

### Optional debugging commands

```bash
python3 facebook_group_poster.py detect-mode <group_url> [cdp_port]
```

Use this only when you need to inspect whether the group resolves to the sell-item flow or the regular-post flow.

```bash
python3 facebook_group_poster.py create-sale-post-human-typing-poc <post_title> <post_description> <city> <image_path> <group_url> [cdp_port] [char_delay_ms]
```

Use this only when Facebook behaves differently with character-by-character input and you need to compare it against the default sale-post flow.

## Notes

- `facebook_group_poster.py` is the authoritative implementation.
- Both the sell-item flow and the regular-post flow are implemented.
- `uv` is not required for runtime because the current Python CLI has no external Python dependencies.
- This skill is Unix-oriented and does not target Windows support.
