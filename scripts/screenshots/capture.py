#!/usr/bin/env python3
"""
Capture OpenShift web console screenshots using Playwright.

Usage:
    export CONSOLE_URL=https://console-openshift-console.apps.example.com
    export CONSOLE_TOKEN=$(oc whoami -t)
    python scripts/screenshots/capture.py [--config captures.yaml] [--name <name>]

Options:
    --config   Path to captures YAML config (default: scripts/screenshots/captures.yaml)
    --name     Capture only the screenshot with this name (default: all)
    --headed   Run with a visible browser window (default: headless)
"""

import argparse
import os
import sys
from pathlib import Path

import yaml
from playwright.sync_api import sync_playwright


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def get_env():
    """Read required environment variables."""
    console_url = os.environ.get("CONSOLE_URL")
    user = os.environ.get("CONSOLE_USER", "kubeadmin")
    password = os.environ.get("CONSOLE_PASS")
    if not console_url or not password:
        print("Set CONSOLE_URL and CONSOLE_PASS environment variables.", file=sys.stderr)
        sys.exit(1)
    return console_url.rstrip("/"), user, password


def login(page, context, console_url, user, password):
    """Log in to the OpenShift web console."""
    page.goto(console_url, wait_until="networkidle")
    page.wait_for_timeout(2000)

    if "login" in page.url or "oauth" in page.url:
        # Click identity provider link if present
        idp_link = page.locator("a").filter(has_text="kubeadmin")
        if idp_link.count() > 0:
            idp_link.first.click()
            page.wait_for_load_state("networkidle")

        page.locator("input[type='text']:visible").first.fill(user)
        page.locator("input[type='password']:visible").first.fill(password)
        page.locator("button:visible:has-text('Log in')").click()

        # Wait for redirect chain to complete
        for _ in range(30):
            page.wait_for_timeout(2000)
            if "console-openshift-console" in page.url and "callback" not in page.url:
                break

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(5000)
    print(f"  Logged in. URL: {page.url}")


def highlight_element(page, selector):
    """Add a red outline around an element using Playwright locator."""
    el = page.locator(selector).first
    el.evaluate("el => { el.style.outline = '3px solid red'; el.style.outlineOffset = '2px'; }")


def clear_highlight(page, selector):
    """Remove highlight from an element."""
    el = page.locator(selector).first
    el.evaluate("el => { el.style.outline = ''; el.style.outlineOffset = ''; }")


def take_screenshot(page, console_url, entry):
    """Navigate and capture a single screenshot."""
    name = entry["name"]
    url = console_url + entry["path"]
    output_dir = REPO_ROOT / entry["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / entry["filename"]

    print(f"  Capturing: {name}")
    page.goto(url, wait_until="networkidle")

    # Wait for a specific element or let the page settle
    wait_for = entry.get("wait_for")
    if wait_for:
        page.wait_for_selector(wait_for, timeout=30000)
    else:
        page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    # Highlight an element if configured
    highlight = entry.get("highlight")
    if highlight:
        highlight_element(page, highlight)
        page.wait_for_timeout(300)

    # Capture: clip to element or full page
    clip_selector = entry.get("clip")
    if clip_selector:
        element = page.query_selector(clip_selector)
        if element:
            element.screenshot(path=str(output_path))
        else:
            print(f"    Warning: clip selector '{clip_selector}' not found, taking full page.")
            page.screenshot(path=str(output_path), full_page=False)
    else:
        page.screenshot(path=str(output_path), full_page=False)

    # Clear highlight
    if highlight:
        clear_highlight(page, highlight)

    print(f"    Saved: {output_path.relative_to(REPO_ROOT)}")


def main():
    parser = argparse.ArgumentParser(description="Capture OpenShift console screenshots.")
    parser.add_argument("--config", default=str(REPO_ROOT / "scripts/screenshots/captures.yaml"))
    parser.add_argument("--name", default=None, help="Capture only this named screenshot.")
    parser.add_argument("--headed", action="store_true", help="Run with visible browser.")
    args = parser.parse_args()

    console_url, user, password = get_env()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    entries = config.get("screenshots", [])
    if args.name:
        entries = [e for e in entries if e["name"] == args.name]
        if not entries:
            print(f"No screenshot named '{args.name}' in config.", file=sys.stderr)
            sys.exit(1)

    print(f"Console: {console_url}")
    print(f"Screenshots to capture: {len(entries)}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=not args.headed,
            args=["--ignore-certificate-errors"],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=True,
        )
        page = context.new_page()

        login(page, context, console_url, user, password)

        for entry in entries:
            try:
                take_screenshot(page, console_url, entry)
            except Exception as e:
                print(f"    Error capturing {entry['name']}: {e}", file=sys.stderr)

        browser.close()

    print("Done.")


if __name__ == "__main__":
    main()
