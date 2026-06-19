#!/usr/bin/env python3
"""
Playwright script to capture all 7 screenshots of Odoo for the Atlas project.
Saves them in the 'media/' folder.
"""

import os
import sys
from playwright.sync_api import sync_playwright

def main():
    # Ensure media directory exists
    os.makedirs("media", exist_ok=True)
    
    login_url = "https://industria-textil-atlas-test1.odoo.com/web/login"
    username = "intex.atlas.eirl@gmail.com"
    password = "tla.in/tex*25"
    
    print("==============================================")
    # Start Playwright
    with sync_playwright() as p:
        print("🚀 Launching browser...")
        browser = p.chromium.launch(headless=True)
        # Large screen size for premium screenshots
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        # Log in
        print("🔑 Logging in to Odoo...")
        page.goto(login_url)
        page.wait_for_timeout(2000)
        page.fill("input#login", username)
        page.fill("input#password", password)
        page.click("button[type='submit']")
        page.wait_for_url("**/odoo**", timeout=20000)
        page.wait_for_timeout(5000)
        print("✅ Logged in successfully.")

        # --- PHOTO 1: Products List View ---
        print("\n📸 [Photo 1] Navigating to Products List View...")
        page.goto("https://industria-textil-atlas-test1.odoo.com/odoo/action-655")
        page.wait_for_timeout(5000)
        
        # Click on List view button
        print("  Switching to List View...")
        list_btn = page.locator("button.o_list").first
        if list_btn.is_visible():
            list_btn.click()
            page.wait_for_timeout(3000)
            
        page.screenshot(path="media/foto1_catalogo_productos.png")
        print("  ✅ Photo 1 saved to 'media/foto1_catalogo_productos.png'")

        # --- PHOTO 2: Product Detail Form ---
        print("\n📸 [Photo 2] Opening first product details...")
        first_row = page.locator(".o_list_table tbody tr.o_data_row").first
        if first_row.is_visible():
            first_row.click()
            page.wait_for_timeout(3000)
            page.screenshot(path="media/foto2_ficha_producto.png")
            print("  ✅ Photo 2 saved to 'media/foto2_ficha_producto.png'")
        else:
            print("  ❌ Could not locate first row in products table.")

        # --- PHOTO 3: Reordering Rules ---
        print("\n📸 [Photo 3] Navigating to Reordering Rules...")
        # Let's try smart button first
        smart_btn = page.locator(".oe_button_box button:has-text('Reglas'), .oe_button_box button:has-text('Reordenar'), .oe_button_box button:has-text('Min/Max'), button.oe_stat_button:has-text('Reglas')").first
        if smart_btn.is_visible():
            print("  Clicking Reordering Rules smart button...")
            smart_btn.click()
            page.wait_for_timeout(3000)
            page.screenshot(path="media/foto3_reglas_stock_minimo.png")
            print("  ✅ Photo 3 saved to 'media/foto3_reglas_stock_minimo.png'")
        else:
            print("  Smart button not found, navigating via top menu...")
            page.goto("https://industria-textil-atlas-test1.odoo.com/odoo/action-655")
            page.wait_for_timeout(3000)
            page.locator(".o_menu_sections button:has-text('Productos'), .o_menu_sections a:has-text('Productos')").click()
            page.wait_for_timeout(1000)
            page.locator(".dropdown-menu a:has-text('Reglas de reabastecimiento'), .dropdown-menu a:has-text('Puntos de reorden')").click()
            page.wait_for_timeout(3000)
            page.screenshot(path="media/foto3_reglas_stock_minimo.png")
            print("  ✅ Photo 3 saved to 'media/foto3_reglas_stock_minimo.png'")

        # --- PHOTO 4 & 5: Point of Sale (POS) ---
        print("\n📸 [Photo 4 & 5] Navigating to POS dashboard...")
        page.goto("https://industria-textil-atlas-test1.odoo.com/odoo/point-of-sale")
        page.wait_for_timeout(5000)
        
        # Click "Seguir vendiendo" or "Abrir caja registradora"
        session_btn = page.locator("button:has-text('Seguir vendiendo'), button:has-text('Abrir caja registradora'), button:has-text('Continuar venta'), button:has-text('Resume')").first
        if session_btn.is_visible():
            print(f"  Clicking POS Session button: '{session_btn.text_content().strip()}'")
            session_btn.click()
            page.wait_for_timeout(3000)
            
            # Check for opening control dialog
            dialog_btn = page.locator(".modal-dialog button.btn-primary, .modal-footer button.btn-primary, button:has-text('Abrir caja'), button:has-text('Abrir sesión'), button:has-text('Abrir caja registradora')").first
            if dialog_btn.is_visible():
                print(f"  Clicking opening dialog button: '{dialog_btn.text_content().strip()}'")
                dialog_btn.click()
                page.wait_for_timeout(3000)
                
            print("  Waiting 20 seconds for POS to load...")
            page.wait_for_timeout(20000)
            
            # Capture Photo 4
            page.screenshot(path="media/foto4_pos_abierto.png")
            print("  ✅ Photo 4 saved to 'media/foto4_pos_abierto.png'")
            
            # Click on a product card to add to cart
            print("  Adding product to cart in POS...")
            product_card = page.locator(".product-list .product-name, .product-content, .product").first
            if product_card.is_visible():
                product_card.click()
                page.wait_for_timeout(2000)
                
                # Check for "Añadir" button in modal dialog
                anadir_btn = page.locator(".modal-dialog button:has-text('Añadir'), button:has-text('Añadir')").first
                if anadir_btn.is_visible():
                    print("  Clicking 'Añadir' in variants dialog...")
                    anadir_btn.click()
                    page.wait_for_timeout(2000)
                
                # Click Pay button (Pagar)
                pay_btn = page.locator("button:has-text('Pagar'), .pay-button, .button.pay").first
                if pay_btn.is_visible():
                    print("  Clicking Pagar button...")
                    pay_btn.click()
                    page.wait_for_timeout(3000)
                    
                    # Capture Photo 5
                    page.screenshot(path="media/foto5_pos_pago.png")
                    print("  ✅ Photo 5 saved to 'media/foto5_pos_pago.png'")
                    
                    # Go back to clean up
                    back_btn = page.locator("button:has-text('Atrás'), button:has-text('Back'), .button.back").first
                    if back_btn.is_visible():
                        back_btn.click()
                        page.wait_for_timeout(1000)
                else:
                    print("  ❌ Pagar button not found.")
            else:
                print("  ❌ No product card found on POS screen.")
                
            # Exit session
            try:
                print("  Closing POS session...")
                close_btn = page.locator("button:has-text('Cerrar'), button:has-text('Close'), .close-button").first
                if close_btn.is_visible():
                    close_btn.click()
                    page.wait_for_timeout(1000)
                    confirm_close = page.locator(".modal-dialog button:has-text('Cerrar'), button:has-text('Confirmar')").first
                    if confirm_close.is_visible():
                        confirm_close.click()
                        page.wait_for_timeout(2000)
            except Exception as e:
                print(f"  Could not close POS cleanly: {e}")
        else:
            print("  ❌ POS Session button not found.")

        # --- PHOTO 6: Purchase Order (PO) ---
        print("\n📸 [Photo 6] Navigating to Purchase Orders...")
        page.goto("https://industria-textil-atlas-test1.odoo.com/odoo/purchase")
        page.wait_for_timeout(5000)
        
        # Click on the first PO in the list
        first_po = page.locator(".o_list_table tbody tr.o_data_row").first
        if first_po.is_visible():
            first_po.click()
            page.wait_for_timeout(3000)
            page.screenshot(path="media/foto6_orden_compra.png")
            print("  ✅ Photo 6 saved to 'media/foto6_orden_compra.png'")
        else:
            print("  ❌ No purchase orders found in list view.")

        # --- PHOTO 7: Inventory Valuation ---
        print("\n📸 [Photo 7] Navigating directly to Inventory Valuation (Action 790)...")
        page.goto("https://industria-textil-atlas-test1.odoo.com/odoo/action-790")
        page.wait_for_timeout(5000)
        page.screenshot(path="media/foto7_valoracion_inventario.png")
        print("  ✅ Photo 7 saved to 'media/foto7_valoracion_inventario.png'")

        print("\n🎉 All screenshot capture tasks completed.")
        browser.close()

if __name__ == '__main__':
    main()
