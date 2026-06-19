#!/usr/bin/env python3
"""
Inspect POS buttons and Inventory Report dropdown items.
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
        
        # Log in
        page.goto(login_url)
        page.wait_for_timeout(2000)
        page.fill("input#login", username)
        page.fill("input#password", password)
        page.click("button[type='submit']")
        page.wait_for_url("**/odoo**", timeout=20000)
        page.wait_for_timeout(5000)
        
        # 1. Inspect POS
        print("Checking POS dashboard buttons...")
        page.goto("https://industria-textil-atlas-test1.odoo.com/odoo/point-of-sale")
        page.wait_for_timeout(5000)
        page.screenshot(path="media/debug_pos_dashboard_now.png")
        
        buttons = page.locator("button, a.btn").all()
        for idx, btn in enumerate(buttons):
            text = btn.text_content() or ""
            print(f"  POS Button [{idx}]: '{text.strip()}' | Class: '{btn.get_attribute('class')}'")
            
        # 2. Inspect Inventory Reportes Dropdown
        print("\nChecking Inventory Reportes dropdown...")
        page.goto("https://industria-textil-atlas-test1.odoo.com/odoo/inventory")
        page.wait_for_timeout(5000)
        
        reportes_btn = page.locator(".o_menu_sections button:has-text('Reportes'), .o_menu_sections a:has-text('Reportes')").first
        if reportes_btn.is_visible():
            reportes_btn.click()
            page.wait_for_timeout(2000)
            page.screenshot(path="media/debug_inventory_reportes_open.png")
            
            # List dropdown items
            items = page.locator(".dropdown-menu a, .dropdown-menu button").all()
            print(f"  Dropdown items:")
            for idx, item in enumerate(items):
                print(f"    [{idx}] Text: '{item.text_content().strip()}' | Href: '{item.get_attribute('href')}'")
        else:
            print("  ❌ 'Reportes' top menu item not found.")
            
        browser.close()

if __name__ == '__main__':
    main()
