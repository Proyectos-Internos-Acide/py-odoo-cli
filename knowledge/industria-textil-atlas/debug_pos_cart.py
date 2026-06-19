#!/usr/bin/env python3
"""
Debug script to inspect POS screen after adding a product.
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
        
        # Navigate to POS
        page.goto("https://industria-textil-atlas-test1.odoo.com/odoo/point-of-sale")
        page.wait_for_timeout(5000)
        
        # Click Seguir vendiendo
        page.locator("button:has-text('Seguir vendiendo')").first.click()
        print("Waiting for POS screen...")
        page.wait_for_timeout(20000)
        
        # Click product card
        print("Clicking product card...")
        page.locator(".product-list .product-name, .product-content, .product").first.click()
        page.wait_for_timeout(3000)
        
        # Take screenshot
        page.screenshot(path="media/debug_pos_cart_added.png")
        print("Saved debug_pos_cart_added.png")
        
        # List all buttons on the page
        buttons = page.locator("button, a.btn, .button").all()
        print(f"Found {len(buttons)} elements:")
        for idx, btn in enumerate(buttons):
            text = btn.text_content() or ""
            attr_class = btn.get_attribute("class") or ""
            print(f"  [{idx}] Class: '{attr_class}' | Text: '{text.strip()}'")
            
        browser.close()

if __name__ == '__main__':
    main()
