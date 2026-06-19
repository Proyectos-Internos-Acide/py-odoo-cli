#!/usr/bin/env python3
"""
Test script to log in to Odoo using Playwright and verify success.
"""

import sys
import os
from playwright.sync_api import sync_playwright

def main():
    login_url = "https://industria-textil-atlas-test1.odoo.com/web/login"
    username = "intex.atlas.eirl@gmail.com"
    password = "tla.in/tex*25"
    
    print(f"URL: {login_url}")
    print(f"User: {username}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create a browser context with a large screen size for beautiful screenshots
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        print("Navigating to Odoo login page...")
        page.goto(login_url)
        page.wait_for_timeout(2000) # Wait 2 seconds
        
        # Check if database selector is visible
        if page.locator("select[name='db']").is_visible():
            print("Database selector found, selecting 'industria-textil-atlas-test1'...")
            page.select_option("select[name='db']", value="industria-textil-atlas-test1")
            
        print("Filling credentials...")
        page.fill("input#login", username)
        page.fill("input#password", password)
        
        print("Clicking login button...")
        page.click("button[type='submit']")
        
        print("Waiting for page to load after login...")
        page.wait_for_url("**/web**", timeout=15000)
        page.wait_for_timeout(5000) # Wait for page rendering
        
        print(f"Current URL: {page.url}")
        page.screenshot(path="odoo_home.png")
        print("✅ Logged in successfully. Screenshot saved as odoo_home.png")
        
        browser.close()

if __name__ == '__main__':
    main()
