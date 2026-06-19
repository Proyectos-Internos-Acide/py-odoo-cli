#!/usr/bin/env python3
"""
Test script to handle POS opening and capture POS screenshots.
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
        
        print("Clicking 'Abrir caja registradora'...")
        page.locator("button:has-text('Abrir caja registradora')").first.click()
        page.wait_for_timeout(3000)
        page.screenshot(path="media/debug_pos_after_click.png")
        
        # Check if there is an opening popup/dialog
        # Typically has class .modal-dialog or button with text "Abrir" or "Abrir sesión" or "Abrir caja" or class "btn-primary"
        print("Checking for opening control dialog...")
        primary_btn = page.locator(".modal-dialog button.btn-primary, .modal-footer button.btn-primary, button:has-text('Abrir caja'), button:has-text('Abrir sesión')").first
        if primary_btn.is_visible():
            print(f"Clicking dialog primary button: '{primary_btn.text_content().strip()}'")
            primary_btn.click()
            page.wait_for_timeout(3000)
            page.screenshot(path="media/debug_pos_after_dialog.png")
            
        # Now wait for POS to load (this might take up to 20 seconds)
        print("Waiting for POS screen to render...")
        page.wait_for_timeout(20000)
        page.screenshot(path="media/debug_pos_loaded.png")
        
        # Check if POS UI is visible
        # Let's take Foto 4
        page.screenshot(path="media/foto4_pos_abierto.png")
        print("✅ Captured Foto 4")
        
        # Add products and go to payment screen
        try:
            # Let's click on a product card
            # In POS, product elements might have class .product-content, .product, or .product-name
            product = page.locator(".product-list .product-name, .product-content, .product").first
            if product.is_visible():
                print(f"Clicking product: '{product.text_content().strip()}'")
                product.click()
                page.wait_for_timeout(1000)
                
                # Check if pay button is visible
                pay_btn = page.locator("button:has-text('Pago'), button:has-text('Payment'), .pay-button, .button.pay").first
                if pay_btn.is_visible():
                    print("Clicking pay button...")
                    pay_btn.click()
                    page.wait_for_timeout(3000)
                    page.screenshot(path="media/foto5_pos_pago.png")
                    print("✅ Captured Foto 5")
                else:
                    print("❌ Pay button not found.")
            else:
                print("❌ Product not found on POS screen.")
        except Exception as ex:
            print(f"❌ Error during POS action: {ex}")
            
        # Try to exit the POS session cleanly
        try:
            print("Attempting to close POS session...")
            close_btn = page.locator("button:has-text('Cerrar'), button:has-text('Close'), .close-button, button[title='Cerrar']").first
            if close_btn.is_visible():
                close_btn.click()
                page.wait_for_timeout(1000)
                confirm_close = page.locator(".modal-dialog button:has-text('Cerrar'), button:has-text('Confirmar'), button:has-text('Close')").first
                if confirm_close.is_visible():
                    confirm_close.click()
                    page.wait_for_timeout(2000)
        except Exception as close_ex:
            print(f"Could not close POS session: {close_ex}")
            
        browser.close()

if __name__ == '__main__':
    main()
