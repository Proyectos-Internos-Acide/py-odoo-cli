#!/usr/bin/env python3
import sys
from playwright.sync_api import sync_playwright

def main():
    try:
        with sync_playwright() as p:
            print("Launching browser...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            print("Navigating to Google...")
            page.goto("https://www.google.com")
            page.screenshot(path="google_screenshot.png")
            browser.close()
            print("✅ Browser test successful. Screenshot saved as google_screenshot.png")
    except Exception as e:
        print(f"❌ Browser test failed: {e}")

if __name__ == '__main__':
    main()
