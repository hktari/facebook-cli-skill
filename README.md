# Facebook Marketing Agent

Python-first Facebook group posting automation built around a CDP-enabled Chrome or Chromium browser and `agent-browser` subprocess execution.

## Current interface

- `python3 facebook_group_poster.py start-browser [cdp_port] [profile_dir] [--headless]`
- `python3 facebook_group_poster.py prepare-facebook-session [cdp_port] [profile_dir]`
- `python3 facebook_group_poster.py check-facebook-logged-in [cdp_port]`
- `python3 facebook_group_poster.py post-to-facebook-group <post_title> <post_description> <city> <image_path> <group_url> [cdp_port]`

## Architecture

- `facebook_group_poster.py` contains the browser bootstrap, mode detection, sale-post flow, regular-post flow, and unified routing logic
- `agent-browser` remains the browser automation engine

## Behavior

- starts or reuses a sandboxed Chrome profile with CDP enabled
- supports visible browser startup for initial Facebook login and headless startup for routine automation
- routes posting through a single shell entrypoint
- validates that a Facebook session is ready before posting
- detects whether the target group exposes `Sell something`
- uses the sales-post flow when that button is present
- uses the regular-post flow otherwise

## Requirements

- `agent-browser` available on `PATH`
- Python 3.12+
- Chrome or Chromium installed
- a sandboxed browser profile that can persist a valid Facebook login session

## Runtime

- `uv` is optional
- the current CLI has no external Python package dependencies
- `python3` is enough to run the tool

## Notes

- the sell-item flow is implemented in Python
- the regular post flow is implemented in Python
- initial Facebook login is a manual step in a visible browser window
- routine posting can reuse the saved browser profile in headless mode
- the implementation is Unix-oriented

## Suggested validation

- prepare a reusable Facebook session with `python3 facebook_group_poster.py prepare-facebook-session 9222 ./.chrome-profile`
- verify the saved session with `python3 facebook_group_poster.py check-facebook-logged-in 9222`
- if you need a headless browser for automation, start it with `python3 facebook_group_poster.py start-browser 9222 ./.chrome-profile --headless`
- connect with `agent-browser connect 9222`
- exercise both a sell-item group and a regular-post group
