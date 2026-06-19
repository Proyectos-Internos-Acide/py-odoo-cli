#!/usr/bin/env python3
"""
Test script to navigate Odoo Inventory and capture Photos 1, 2, and 3.
"""

import os
from playwright.sync_api import sync_playwright

def main():
    os.makedirs("media", exist_ok=True)
    
    login_url = "https://industria-textil-atlas-test1.odoo.com/web/login"
    username = "intex.atlas.eirl@gmail.com"
    password = "tla.in/tex*25"
    
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        # Log in
        print("Logging in...")
        page.goto(login_url)
        page.wait_for_timeout(2000)
        page.fill("input#login", username)
        page.fill("input#password", password)
        page.click("button[type='submit']")
        page.wait_for_url("**/odoo**", timeout=20000)
        page.wait_for_timeout(5000)
        
        # Navigate to Inventory
        print("Navigating to Inventory...")
        page.goto("https://industria-textil-atlas-test1.odoo.com/odoo/inventory")
        page.wait_for_timeout(5000)
        page.screenshot(path="media/debug_inventory_home.png")
        print("Saved debug_inventory_home.png")
        
        # Click on "Productos" menu
        print("Clicking 'Productos' in top menu...")
        # Let's locate the menu items
        try:
            page.locator(".o_menu_sections button:has-text('Productos'), .o_menu_sections a:has-text('Productos')").click()
            page.wait_for_timeout(1000)
            
            # Click on sub-menu "Productos"
            print("Clicking sub-menu 'Productos'...")
            page.locator(".dropdown-menu a:has-text('Productos')").click()
            page.wait_for_timeout(3000)
            
            # Verify if in list view, if not click list view button
            print("Ensuring List View...")
            list_btn = page.locator("button[aria-label='Vista lista'], button[title='Lista']")
            if list_btn.is_visible():
                list_btn.click()
                page.wait_for_timeout(2000)
                
            # Take Foto 1
            print("Capturing Foto 1: Catálogo de productos...")
            page.screenshot(path="media/foto1_catalogo_productos.png")
            print("✅ Captured Foto 1")
            
            # Click on a product (e.g. Polo Camisero Piqué)
            print("Opening a product detail...")
            product_row = page.locator("td:has-text('Polo Camisero Piqué'), td:has-text('Camisa de Vestir Oxford')").first
            if product_row.is_visible():
                product_row.click()
                page.wait_for_timeout(3000)
                
                # Take Foto 2
                print("Capturing Foto 2: Ficha de producto...")
                page.screenshot(path="media/foto2_ficha_producto.png")
                print("✅ Captured Foto 2")
                
                # Click on Reordering Rules (Reglas de reabastecimiento) smart button if visible
                # Let's find smart buttons
                print("Looking for Reordering Rules smart button...")
                smart_btn = page.locator("button:has-text('Reglas de'), button:has-text('Reordenar'), button:has-text('Min/Max')")
                if smart_btn.is_visible():
                    smart_btn.click()
                    page.wait_for_timeout(3000)
                    page.screenshot(path="media/foto3_reglas_stock_minimo.png")
                    print("✅ Captured Foto 3")
                else:
                    print("Smart button not found, navigating to rules from top menu...")
                    # Let's try top menu "Productos" -> "Reglas de reabastecimiento"
                    page.locator(".o_menu_sections button:has-text('Productos'), .o_menu_sections a:has-text('Productos')").click()
                    page.wait_for_timeout(1000)
                    page.locator(".dropdown-menu a:has-text('Reglas de reabastecimiento'), .dropdown-menu a:has-text('Puntos de reorden')").click()
                    page.wait_for_timeout(3000)
                    page.screenshot(path="media/foto3_reglas_stock_minimo.png")
                    print("✅ Captured Foto 3")
            else:
                print("❌ No product row found in list view.")
        except Exception as e:
            print(f"❌ Error during inventory screenshots: {e}")
            page.screenshot(path="media/error_inventory.png")
            
        browser.close()

if __name__ == '__main__':
    main()
