
# Facebook Marketing Agent

Python-first Facebook group posting automation built around a CDP-enabled Chrome or Chromium browser and `agent-browser` subprocess execution.

## Current interface

- `python3 facebook_group_poster.py start-browser [cdp_port] [profile_dir]`
- `python3 facebook_group_poster.py post-to-facebook-group <post_title> <post_description> <city> <image_path> <group_url> [cdp_port]`
- `python3 facebook_group_poster.py create-sale-post-human-typing-poc <post_title> <post_description> <city> <image_path> <group_url> [cdp_port] [char_delay_ms]`

## Architecture

- `facebook_group_poster.py` contains the browser bootstrap, mode detection, sale-post flow, regular-post flow, and unified routing logic
- `agent-browser` remains the browser automation engine

## Behavior

- starts or reuses a sandboxed Chrome profile with CDP enabled
- routes posting through a single shell entrypoint
- detects whether the target group exposes `Sell something`
- uses the sales-post flow when that button is present
- uses the regular-post flow otherwise

## Requirements

- `agent-browser` available on `PATH`
- Python 3.12+
- Chrome or Chromium installed
- a sandboxed browser profile with a valid Facebook login session

## Runtime

- `uv` is optional
- the current CLI has no external Python package dependencies
- `python3` is enough to run the tool

## Notes

- the sell-item flow is implemented in Python
- the regular post flow is implemented in Python
- the human-typing sales POC is available for comparison and tuning
- the implementation is Unix-oriented

## Suggested validation

- start the browser with `python3 facebook_group_poster.py start-browser 9222 ./.chrome-profile`
- connect with `agent-browser connect 9222`
- exercise both a sell-item group and a regular-post group
- compare `python3 facebook_group_poster.py create-sale-post ...` with `python3 facebook_group_poster.py create-sale-post-human-typing-poc ...` if Facebook input behavior changes
