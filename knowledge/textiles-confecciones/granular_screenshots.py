import os
import sys
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")
OUTPUT_DIR = "/home/acide/Descargas/project-reports/TEXTILES-Y-CONFECCIONES-ATLAS/Manual/images"

def draw_red_box_and_save(page, selector, output_name):
    try:
        page.wait_for_selector(selector, timeout=10000)
        page.evaluate(f"""
            const el = document.querySelector("{selector}");
            if (el) {{
                el.style.border = "4px solid red";
                el.style.boxShadow = "0 0 12px red";
            }}
        """)
        time.sleep(1)
        dest_path = os.path.join(OUTPUT_DIR, output_name)
        page.screenshot(path=dest_path)
        print(f"Captura guardada con recuadro: {dest_path}")
    except Exception as e:
        print(f"No se pudo resaltar selector {selector}: {e}")
        dest_path = os.path.join(OUTPUT_DIR, output_name)
        page.screenshot(path=dest_path)

def main():
    if not ODOO_URL or not ODOO_USER or not ODOO_PASSWORD:
        print("Error: Configuración incompleta.")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with sync_playwright() as p:
        print("Iniciando navegador...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # Login
        page.goto(f"{ODOO_URL}/web/login")
        page.wait_for_selector("#login", timeout=15000)
        page.fill("#login", ODOO_USER)
        page.fill("#password", ODOO_PASSWORD)
        page.click("button[type='submit']")
        page.wait_for_url(lambda url: "/web" in url or "/odoo" in url, timeout=30000)
        time.sleep(5)

        # 1. CONTACTOS (Llenar campos e interactuar usando selectores nativos genéricos)
        print("Navegando a Contactos...")
        page.goto(f"{ODOO_URL}/web#action=contacts.action_contacts")
        time.sleep(6)
        
        # En la lista, hacemos clic en el botón Nuevo
        page.click("button.o_list_button_add, button.o-kanban-button-new, button:has-text('Nuevo')")
        time.sleep(5)
        
        # Buscar todos los inputs de tipo texto y rellenar los primeros
        try:
            inputs = page.locator("input[type='text'], input.o_input")
            # El primer input en el formulario de contactos suele ser el Nombre
            inputs.nth(0).fill("TEXTILES ATLAS TEST S.A.C.")
            # Rellenar RUC en el correspondiente
            # Odoo suele usar input.o_field_char o similar. Buscaremos por placeholder o id
            vat_input = page.locator("input[placeholder='e.g. BE0477472701'], input[id='vat'], input[name='vat']")
            if vat_input.count() > 0:
                vat_input.first.fill("20123456789")
            else:
                # Si no lo encuentra, intentamos con el segundo input
                inputs.nth(1).fill("20123456789")
        except Exception as e:
            print("Error rellenando campos en Contactos:", e)
        
        draw_red_box_and_save(page, "input[type='text']", "contactos_crud_fill_name.png")
        draw_red_box_and_save(page, "input[type='text']", "contactos_crud_fill_vat.png")
        draw_red_box_and_save(page, ".o_form_view, body", "contactos_nuevo.png")

        # 2. INVENTARIO (Llenar campos de Producto y capturar)
        print("Navegando a Inventario -> Productos...")
        page.goto(f"{ODOO_URL}/web#action=stock.product_template_action_product")
        time.sleep(6)
        page.click("button.o_list_button_add, button.o-kanban-button-new, button:has-text('Nuevo')")
        time.sleep(5)
        
        try:
            # Rellenar primer campo de texto (Nombre del producto)
            page.locator("input[type='text'], input.o_input").first.fill("Casaca Térmica Impermeable Talla L")
            # Buscar precio
            price_input = page.locator("input[id='lst_price'], input.o_input")
            if price_input.count() > 1:
                price_input.nth(1).fill("120.00")
        except Exception as e:
            print("Error rellenando campos en Productos:", e)
        
        draw_red_box_and_save(page, "input[type='text']", "inventario_crud_fill_name.png")
        draw_red_box_and_save(page, ".o_form_view, body", "inventario_crud_fill_type.png")
        draw_red_box_and_save(page, ".o_form_view, body", "inventario_producto_nuevo.png")

        # 3. VENTAS B2B
        print("Navegando a Ventas B2B...")
        page.goto(f"{ODOO_URL}/web#action=sale.action_orders")
        time.sleep(6)
        page.click("button.o_list_button_add, button:has-text('Nuevo')")
        time.sleep(5)
        
        try:
            # Buscar el campo de selección de cliente (suele ser el primer div o input con autocomplete)
            partner_input = page.locator("input[id='partner_id'], input.o_input").first
            partner_input.click()
            time.sleep(1)
            page.keyboard.press("ArrowDown")
            time.sleep(1)
            page.keyboard.press("Enter")
            time.sleep(1)
        except Exception as e:
            print("Error al seleccionar cliente:", e)
            
        draw_red_box_and_save(page, ".o_form_view, body", "ventas_crud_form.png")

        browser.close()
        print("Todas las capturas detalladas con datos de ejemplo completadas.")

if __name__ == "__main__":
    main()
