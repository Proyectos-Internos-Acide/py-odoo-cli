#!/usr/bin/env python3
"""
Diagnostic script to find application links on the Odoo home page.
"""

import sys
import os
from playwright.sync_api import sync_playwright

def main():
    login_url = "https://industria-textil-atlas-test1.odoo.com/web/login"
    username = "intex.atlas.eirl@gmail.com"
    password = "tla.in/tex*25"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        print("Navigating and logging in...")
        page.goto(login_url)
        page.wait_for_timeout(2000)
        
        page.fill("input#login", username)
        page.fill("input#password", password)
        page.click("button[type='submit']")
        
        print("Waiting for /odoo page...")
        page.wait_for_url("**/odoo**", timeout=20000)
        page.wait_for_timeout(5000)
        
        print(f"Logged in. Current URL: {page.url}")
        
        # Take home screenshot
        page.screenshot(path="odoo_apps.png")
        print("Screenshot of Odoo home saved as odoo_apps.png")
        
        # Get all app links
        apps = page.locator("a.o_app, .o_app_icon_container, a[href*='action'], .o_menuitem").all()
        print(f"Found {len(apps)} potential app elements:")
        for idx, app in enumerate(apps):
            text = app.text_content() or ""
            href = app.get_attribute("href") or ""
            inner = app.inner_html() or ""
            print(f"  [{idx}] Text: '{text.strip()}' | Href: '{href}'")
            
        # Let's inspect the page title and body content
        title = page.title()
        print(f"Page Title: {title}")
        
        browser.close()

if __name__ == '__main__':
    main()
