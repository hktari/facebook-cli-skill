from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


class AgentBrowserError(RuntimeError):
    pass


@dataclass(frozen=True)
class PostRequest:
    post_title: str
    post_description: str
    city: str
    marketing_image_abs_path: str
    fb_group_url: str
    cdp_port: int = 9222


class AgentBrowserClient:
    def __init__(self, cdp_port: int) -> None:
        self.cdp_port = cdp_port

    def run(self, *args: str, capture_output: bool = False) -> str:
        command = ["agent-browser", "--cdp", str(self.cdp_port), *args]
        result = subprocess.run(
            command,
            check=True,
            text=True,
            capture_output=capture_output,
        )
        return result.stdout if capture_output else ""

    def open(self, url: str) -> None:
        self.run("open", url)

    def snapshot(self) -> str:
        return self.run("snapshot", capture_output=True)

    def click(self, selector: str) -> None:
        self.run("click", selector)

    def type(self, selector: str, value: str) -> None:
        self.run("type", selector, value)

    def fill(self, selector: str, value: str) -> None:
        self.run("fill", selector, value)

    def focus(self, selector: str) -> None:
        self.run("focus", selector)

    def keyboard_type(self, value: str) -> None:
        self.run("keyboard", "type", value)

    def upload(self, selector: str, value: str) -> None:
        self.run("upload", selector, value)

    def get_text(self, selector: str) -> str:
        return self.run("get", "text", selector, capture_output=True)


class FacebookGroupPoster:
    def __init__(self, request: PostRequest, char_delay_ms: int = 90) -> None:
        self.request = request
        self.char_delay_ms = char_delay_ms
        self.browser = AgentBrowserClient(request.cdp_port)

    def open_group(self) -> None:
        self.browser.open(self.request.fb_group_url)

    def wait(self, seconds: float) -> None:
        time.sleep(seconds)

    def snapshot(self) -> str:
        return self.browser.snapshot()

    def find_ref(self, label: str, pattern: str) -> str:
        for line in self.snapshot().splitlines():
            if re.search(pattern, line):
                ref_match = re.search(r"\[ref=([^\]]+)\]", line)
                if ref_match:
                    return ref_match.group(1)
                raise AgentBrowserError(f"Could not extract ref for: {label}")
        raise AgentBrowserError(f"Could not find selector for: {label}")

    def click_ref(self, label: str, pattern: str) -> None:
        self.browser.click(self.find_ref(label, pattern))

    def type_ref(self, label: str, pattern: str, value: str) -> None:
        self.browser.type(self.find_ref(label, pattern), value)

    def fill_ref(self, label: str, pattern: str, value: str) -> None:
        self.browser.fill(self.find_ref(label, pattern), value)

    def focus_ref(self, label: str, pattern: str) -> None:
        self.browser.focus(self.find_ref(label, pattern))

    def get_text_ref(self, label: str, pattern: str) -> str:
        return self.browser.get_text(self.find_ref(label, pattern))

    def human_type_text(self, value: str) -> None:
        for character in value:
            self.browser.keyboard_type(character)
            time.sleep(self.char_delay_ms / 1000)

    def human_type_ref(self, label: str, pattern: str, value: str) -> None:
        self.focus_ref(label, pattern)
        self.human_type_text(value)

    def detect_mode(self) -> str:
        self.open_group()
        self.wait(5)
        snapshot = self.snapshot()
        if re.search(r"Sell Something|Sell something", snapshot):
            return "sell"
        return "regular"

    def create_sale_post(self, human_typing: bool = False) -> None:
        self.open_group()
        self.click_ref("Sell something button", r"Sell Something|Sell something")
        self.wait(5)
        self.click_ref("Item for sale option", r"Item for sale")
        self.wait(5)

        if human_typing:
            self.human_type_ref(
                "Title textbox", r'textbox "Title"', self.request.post_title
            )
        else:
            self.type_ref("Title textbox", r'textbox "Title"', self.request.post_title)

        self.click_ref("Condition combobox", r'combobox "Condition"')
        self.click_ref("New condition option", r'option "New"')

        if human_typing:
            self.human_type_ref("Price textbox", r'textbox "Price"', "1")
        else:
            self.type_ref("Price textbox", r'textbox "Price"', "1")

        self.click_ref("More details button", r'button "More details')

        if human_typing:
            self.human_type_ref(
                "Description textbox",
                r'textbox "Description"',
                self.request.post_description,
            )
        else:
            self.type_ref(
                "Description textbox",
                r'textbox "Description"',
                self.request.post_description,
            )

        self.fill_ref("Location combobox", r'combobox "Location"', self.request.city)
        self.wait(2)
        self.click_ref(
            "Location option", rf'option "{re.escape(self.request.city)}.*\[nth=1\]'
        )
        self.browser.upload(
            'input[type="file"][accept="image/*,image/heif,image/heic"]',
            self.request.marketing_image_abs_path,
        )
        self.wait(5)
        self.click_ref("Next button", r'button "Next"')
        self.wait(5)
        self.click_ref("Post button", r'button "Post"')
        self.wait(10)
        print(
            self.get_text_ref(
                "Listing published heading", r'heading "Listing published"'
            ).strip()
        )
        self.click_ref("Close button", r'button "Close"')

    def create_regular_post(self) -> None:
        self.open_group()
        self.click_ref("Write post button", r'button "Write something\.\.\."')
        self.wait(5)
        post_content = f"{self.request.post_title}\n{self.request.post_description}"
        self.type_ref("Post input field", r"textbox", post_content)
        self.click_ref("Add to your post", r'button "Add to your post"')
        self.wait(3)
        self.browser.upload(
            'div[role="dialog"] + div input[type="file"][accept^="image/"]',
            self.request.marketing_image_abs_path,
        )
        self.wait(10)
        self.click_ref("Post", r'button "Post"')
        self.wait(10)
        self.get_text_ref("Write post button", r'button "Write something\.\.\."')
        print("Post created successfully")

    def post_to_group(self, human_typing: bool = False) -> None:
        mode = self.detect_mode()
        if mode == "sell":
            self.create_sale_post(human_typing=human_typing)
            return
        self.create_regular_post()


def find_chrome_executable() -> str:
    candidates = [
        "google-chrome",
        "chromium",
        "chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
        if Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    raise AgentBrowserError("Chrome or Chromium executable not found.")


def wait_for_cdp(port: int, timeout_seconds: int = 20) -> None:
    deadline = time.time() + timeout_seconds
    url = f"http://localhost:{port}/json/version"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except urllib.error.URLError:
            pass
        time.sleep(1)
    raise AgentBrowserError("Chrome failed to start with CDP")


def start_browser(cdp_port: int, profile_dir: str) -> None:
    chrome_bin = find_chrome_executable()
    Path(profile_dir).mkdir(parents=True, exist_ok=True)
    subprocess.Popen(
        [
            chrome_bin,
            f"--remote-debugging-port={cdp_port}",
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    wait_for_cdp(cdp_port)
    print(f"Chrome started with CDP on port {cdp_port}")


def build_request(args: argparse.Namespace) -> PostRequest:
    return PostRequest(
        post_title=args.post_title,
        post_description=args.post_description,
        city=args.city,
        marketing_image_abs_path=args.image_path,
        fb_group_url=args.group_url,
        cdp_port=args.cdp_port,
    )


def add_post_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("post_title")
    parser.add_argument("post_description")
    parser.add_argument("city")
    parser.add_argument("image_path")
    parser.add_argument("group_url")
    parser.add_argument("cdp_port", nargs="?", type=int, default=9222)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_browser_parser = subparsers.add_parser("start-browser")
    start_browser_parser.add_argument("cdp_port", nargs="?", type=int, default=9222)
    start_browser_parser.add_argument(
        "profile_dir", nargs="?", default=str(Path.cwd() / ".chrome-profile")
    )

    detect_mode_parser = subparsers.add_parser("detect-mode")
    detect_mode_parser.add_argument("group_url")
    detect_mode_parser.add_argument("cdp_port", nargs="?", type=int, default=9222)

    sale_parser = subparsers.add_parser("create-sale-post")
    add_post_arguments(sale_parser)

    sale_human_parser = subparsers.add_parser("create-sale-post-human-typing-poc")
    add_post_arguments(sale_human_parser)
    sale_human_parser.add_argument("char_delay_ms", nargs="?", type=int, default=90)

    regular_parser = subparsers.add_parser("create-regular-post")
    add_post_arguments(regular_parser)

    post_parser = subparsers.add_parser("post-to-facebook-group")
    add_post_arguments(post_parser)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "start-browser":
            start_browser(args.cdp_port, args.profile_dir)
            return 0

        if args.command == "detect-mode":
            request = PostRequest("", "", "", "", args.group_url, args.cdp_port)
            poster = FacebookGroupPoster(request)
            print(poster.detect_mode())
            return 0

        if args.command == "create-sale-post":
            FacebookGroupPoster(build_request(args)).create_sale_post(
                human_typing=False
            )
            return 0

        if args.command == "create-sale-post-human-typing-poc":
            FacebookGroupPoster(
                build_request(args), char_delay_ms=args.char_delay_ms
            ).create_sale_post(human_typing=True)
            return 0

        if args.command == "create-regular-post":
            FacebookGroupPoster(build_request(args)).create_regular_post()
            return 0

        if args.command == "post-to-facebook-group":
            FacebookGroupPoster(build_request(args)).post_to_group(human_typing=False)
            return 0
    except (AgentBrowserError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
