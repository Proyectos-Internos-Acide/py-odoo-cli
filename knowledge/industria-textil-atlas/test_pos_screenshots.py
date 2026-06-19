#!/usr/bin/env python3
"""
Test script to open Point of Sale and capture Photos 4 and 5.
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
        
        # Navigate to POS
        print("Navigating to POS...")
        page.goto("https://industria-textil-atlas-test1.odoo.com/odoo/point-of-sale")
        page.wait_for_timeout(5000)
        page.screenshot(path="media/debug_pos_home.png")
        print("Saved debug_pos_home.png")
        
        # Find POS Session Button
        # In Odoo, it could be a button with class "btn-primary" or text like "Nueva sesión", "Continuar venta", "Resume", "New Session"
        print("Looking for POS Session Button...")
        session_btn = page.locator("button:has-text('Nueva sesión'), button:has-text('Continuar venta'), button:has-text('Resume'), button:has-text('New Session'), button:has-text('Nueva Sesión')").first
        
        if session_btn.is_visible():
            print(f"Clicking session button: '{session_btn.text_content().strip()}'")
            session_btn.click()
            
            # Wait for POS interface to load
            print("Waiting for POS screen (15 seconds)...")
            page.wait_for_timeout(15000)
            page.screenshot(path="media/debug_pos_loading.png")
            
            # Check if POS interface is loaded
            # Typical POS elements in Odoo 17/18: .pos, .pos-content, .product-list, .order-container, etc.
            print("Capturing Foto 4: POS Abierto...")
            page.screenshot(path="media/foto4_pos_abierto.png")
            print("✅ Captured Foto 4")
            
            # Let's try to add a product to cart and click payment
            try:
                # Click on the first product in the POS screen
                # In Odoo 17/18, product elements in POS have classes like .product-content, .product, or .product-name
                product_item = page.locator(".product-content, .product, .product-list .product-name").first
                if product_item.is_visible():
                    print("Clicking product in POS...")
                    product_item.click()
                    page.wait_for_timeout(1000)
                    
                    # Click Payment button
                    # Typically .pay-button, .button.pay, text "Pago", text "Payment"
                    print("Clicking Payment button...")
                    pay_btn = page.locator("button:has-text('Pago'), button:has-text('Payment'), .pay-button, .button.pay").first
                    if pay_btn.is_visible():
                        pay_btn.click()
                        page.wait_for_timeout(3000)
                        
                        print("Capturing Foto 5: Pantalla de Pago...")
                        page.screenshot(path="media/foto5_pos_pago.png")
                        print("✅ Captured Foto 5")
                        
                        # Go back and close to leave it clean
                        back_btn = page.locator("button:has-text('Atrás'), button:has-text('Back'), .button.back").first
                        if back_btn.is_visible():
                            back_btn.click()
                            page.wait_for_timeout(1000)
                    else:
                        print("❌ Payment button not found.")
                else:
                    print("❌ No product item found in POS.")
            except Exception as pos_ex:
                print(f"❌ Error during POS interaction: {pos_ex}")
        else:
            print("❌ POS Session button not found.")
            
        browser.close()

if __name__ == '__main__':
    main()
