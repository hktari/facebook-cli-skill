---
name: facebook-group-poster
description: Automate Facebook group posting through the maintained Python CLI. Use this skill when you need to make a post in a Facebook group.
---

# Facebook Group Posting Skill

## Requirements

- Python 3.12+
- `agent-browser` must be installed and available on `PATH`
- Chrome or Chromium must be installed and runnable on the machine
- the browser session must be started with CDP before posting
- the sandboxed browser profile must be reused so the Facebook login session can persist

## Install Chrome or Chromium including Playwright

If Chrome or Chromium is not already installed, install one of them before using this skill.

Common Linux package names:

- `google-chrome`
- `chromium`
- `chromium-browser`

The Python CLI auto-detects these executable names when starting the browser.

## Install agent-browser
- check if agent-browser is already installed: `agent-browser --version`
- if not installed, see instructions at: https://github.com/vercel-labs/agent-browser on how to install

## How to use

1. check dependencies are installed:
   1.1 check if agent-browser is installed: `agent-browser --version`
   1.2 check if chrome or chromium is installed: `google-chrome --version` or `chromium --version`
   
   if any is missing you must first install them

2. prepare the Facebook session in a visible browser:
   run `python3 facebook_group_poster.py prepare-facebook-session 9222 ./.chrome-profile`

3. if the command reports that login is still needed, complete the Facebook login manually in that browser window and rerun:
   `python3 facebook_group_poster.py check-facebook-logged-in 9222`

4. for routine automation after setup, you may reuse the same profile in headless mode:
   `python3 facebook_group_poster.py start-browser 9222 ./.chrome-profile --headless`


## Best practices
1. make sure to kill running chrome process after all posts have been made
    - find the Chrome or Chromium process: `ps -ef | grep -E 'chrome|chromium' | grep -- '--remote-debugging-port=9222'`
    - stop it cleanly first: `pkill -f -- '--remote-debugging-port=9222'`
    - if it does not stop, force kill it: `pkill -9 -f -- '--remote-debugging-port=9222'`


## Interface

- `./scripts/facebook_group_poster.py` is the main entrypoint.

### Primary entrypoint

<!-- TODO: add examples -->

```bash
python3 facebook_group_poster.py post-to-facebook-group <post_title> <post_description> <city> <image_path> <group_url> [cdp_port]
```

Use this for the normal user-facing task: make a Facebook group post.

### Setup browser session

```bash
python3 facebook_group_poster.py prepare-facebook-session [cdp_port] [profile_dir]
```

Use this when you need to bootstrap the sandboxed Chrome profile and complete the one-time manual Facebook login.

### Supporting commands

```bash
python3 facebook_group_poster.py check-facebook-logged-in [cdp_port]
```

Use this to verify that the persisted Facebook session is still valid.

```bash
python3 facebook_group_poster.py start-browser [cdp_port] [profile_dir] [--headless]
```

Use this to start or reuse the browser profile directly. Prefer visible mode for first-time setup and `--headless` for routine automated runs after login is already saved.

## Notes

- Initial Facebook login is manual and should happen in a visible browser window.
- Routine posting should reuse the persisted profile and can run in headless mode.
