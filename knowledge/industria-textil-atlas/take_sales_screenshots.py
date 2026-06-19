#!/usr/bin/env python3
"""
Playwright script to capture the 4 new Sales-related screenshots for the Atlas project.
Saves them to the 'media/' folder.
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
    print("📸 CAPTURING SALES SCREENSHOTS FOR ATLAS 📸")
    print("==============================================")
    
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

        # --- PHOTO 1: Home page showing the Ventas icon ---
        print("\n📸 [Photo 1] Capturing home page dashboard...")
        # Make sure the home screen is fully loaded
        page.goto("https://industria-textil-atlas-test1.odoo.com/odoo")
        page.wait_for_timeout(5000)
        
        # Save screenshot
        page.screenshot(path="odoo_apps.png")
        page.screenshot(path="media/foto_home_con_ventas.png")
        print("  ✅ Saved to 'odoo_apps.png' and 'media/foto_home_con_ventas.png'")

        # --- PHOTO 2: Ventas List View ---
        print("\n📸 [Photo 2] Navigating to Ventas module...")
        # Let's try clicking the Ventas icon first, or direct URL navigation if click fails.
        ventas_app = page.locator(".o_app:has-text('Ventas'), .o_app:has-text('Sales'), a:has-text('Ventas'), a:has-text('Sales')").first
        if ventas_app.is_visible():
            print("  Clicking Ventas app icon...")
            ventas_app.click()
            page.wait_for_timeout(5000)
        else:
            print("  App icon not found. Navigating directly to action-907...")
            page.goto("https://industria-textil-atlas-test1.odoo.com/odoo/action-907")
            page.wait_for_timeout(5000)
            
        # Ensure we are in list view
        list_btn = page.locator("button.o_list").first
        if list_btn.is_visible():
            list_btn.click()
            page.wait_for_timeout(2000)
            
        page.screenshot(path="media/foto_listado_ventas.png")
        print("  ✅ Saved to 'media/foto_listado_ventas.png'")

        # --- PHOTO 3: Detail Form View ---
        print("\n📸 [Photo 3] Opening the first Sales Order detail view...")
        first_row = page.locator(".o_list_table tbody tr.o_data_row").first
        if first_row.is_visible():
            print("  Clicking first sales order...")
            first_row.click()
            page.wait_for_timeout(5000)
            page.screenshot(path="media/foto_detalle_venta.png")
            print("  ✅ Saved to 'media/foto_detalle_venta.png'")
        else:
            print("  ❌ No row found in the table. Let's try navigating to a direct sales order view.")
            # If the list was empty or couldn't load, let's navigate directly to action-907 and click again
            page.goto("https://industria-textil-atlas-test1.odoo.com/odoo/action-907")
            page.wait_for_timeout(5000)
            first_row = page.locator(".o_list_table tbody tr.o_data_row").first
            if first_row.is_visible():
                first_row.click()
                page.wait_for_timeout(5000)
                page.screenshot(path="media/foto_detalle_venta.png")
                print("  ✅ Saved to 'media/foto_detalle_venta.png'")
            else:
                print("  ❌ Still no row found. Capturing current screen anyway.")
                page.screenshot(path="media/foto_detalle_venta.png")

        # --- PHOTO 4: Customer Preview / PDF ---
        print("\n📸 [Photo 4] Opening Customer Preview...")
        # In Odoo, the Customer Preview button is usually named "Vista previa" or "Customer Preview" or "Vista previa cliente".
        preview_btn = page.locator("button:has-text('Vista previa'), button:has-text('Customer Preview'), button:has-text('Vista previa cliente'), a:has-text('Vista previa'), a:has-text('Customer Preview'), a:has-text('Vista previa cliente')").first
        if preview_btn.is_visible():
            print(f"  Clicking Preview button: '{preview_btn.text_content().strip()}'")
            try:
                # We expect a new page, but let's set a shorter timeout (5000ms)
                with context.expect_page(timeout=5000) as new_page_info:
                    preview_btn.click()
                preview_page = new_page_info.value
                preview_page.wait_for_load_state("networkidle")
                preview_page.wait_for_timeout(5000)
                preview_page.screenshot(path="media/foto_pdf_cotizacion.png")
                print("  ✅ Customer Preview screenshot saved from new tab.")
            except Exception as e:
                print(f"  No new tab opened ({e}). Checking if page navigated or has inline preview...")
                page.wait_for_timeout(5000)
                page.screenshot(path="media/foto_pdf_cotizacion.png")
                print("  ✅ Customer Preview screenshot saved from current page/fallback.")
        else:
            print("  Preview button not found. Let's try searching for alternative ways, or capture the print PDF view if possible.")
            # Try to look for action buttons or dropdown
            action_btn = page.locator("button:has-text('Acción'), button:has-text('Action'), button.o_cp_action_menus").first
            if action_btn.is_visible():
                action_btn.click()
                page.wait_for_timeout(1000)
            
            # Print button
            print_btn = page.locator("button:has-text('Imprimir'), button:has-text('Print')").first
            if print_btn.is_visible():
                print_btn.click()
                page.wait_for_timeout(1000)
                pdf_option = page.locator("a:has-text('Presupuesto / Pedido'), a:has-text('Quotation / Order')").first
                if pdf_option.is_visible():
                    print("  Found 'Presupuesto / Pedido' print option, click it.")
                    pdf_option.click()
                    page.wait_for_timeout(5000)
            
            # As a fallback, we'll try navigating to `/my/orders` or similar if we can find the sales order ID,
            # or just take a screenshot of the detail page.
            # Let's save a fallback screenshot
            print("  ⚠️ Fallback: Taking screenshot of the detail page as the document layout.")
            page.screenshot(path="media/foto_pdf_cotizacion.png")

        print("\n🎉 Screenshot task completed successfully!")
        browser.close()

if __name__ == '__main__':
    main()
