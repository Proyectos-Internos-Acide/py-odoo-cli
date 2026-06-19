#!/usr/bin/env python3
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
        
        page.goto(login_url)
        page.wait_for_timeout(2000)
        page.fill("input#login", username)
        page.fill("input#password", password)
        page.click("button[type='submit']")
        page.wait_for_url("**/odoo**", timeout=20000)
        page.wait_for_timeout(5000)
        
        # Navigate to Inventory
        page.goto("https://industria-textil-atlas-test1.odoo.com/odoo/inventory")
        page.wait_for_timeout(5000)
        
        # Click on "Productos" menu
        page.locator(".o_menu_sections button:has-text('Productos'), .o_menu_sections a:has-text('Productos')").click()
        page.wait_for_timeout(1000)
        page.locator(".dropdown-menu a:has-text('Productos')").click()
        page.wait_for_timeout(5000)
        
        print("Current URL:", page.url)
        
        # List all buttons with their attributes
        buttons = page.locator("button").all()
        print(f"Found {len(buttons)} buttons:")
        for idx, btn in enumerate(buttons):
            attr_class = btn.get_attribute("class") or ""
            attr_title = btn.get_attribute("title") or ""
            attr_aria = btn.get_attribute("aria-label") or ""
            text = btn.text_content() or ""
            if any(x in attr_class or x in attr_title or x in attr_aria or x in text for x in ['list', 'kanban', 'Lista', 'vista', 'switch', 'view']):
                print(f"  [{idx}] Class: '{attr_class}' | Title: '{attr_title}' | Aria: '{attr_aria}' | Text: '{text.strip()}'")
                
        browser.close()

if __name__ == '__main__':
    main()
