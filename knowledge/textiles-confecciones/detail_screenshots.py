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
        page.wait_for_selector(selector, timeout=15000)
        page.evaluate(f"""
            const el = document.querySelector("{selector}");
            if (el) {{
                el.style.border = "4px solid red";
                el.style.boxShadow = "0 0 10px red";
            }}
        """)
        time.sleep(1)
        dest_path = os.path.join(OUTPUT_DIR, output_name)
        page.screenshot(path=dest_path)
        print(f"Captura guardada con recuadro: {dest_path}")
    except Exception as e:
        print(f"No se pudo resaltar el selector {selector}: {e}")
        dest_path = os.path.join(OUTPUT_DIR, output_name)
        page.screenshot(path=dest_path)
        print(f"Captura de respaldo guardada: {dest_path}")

def main():
    if not ODOO_URL or not ODOO_USER or not ODOO_PASSWORD:
        print("Error: Configuración de .env incompleta.")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with sync_playwright() as p:
        print("Iniciando Chromium...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        login_url = f"{ODOO_URL}/web/login"
        print(f"Navegando a login: {login_url}")
        page.goto(login_url)
        page.wait_for_selector("#login", timeout=15000)
        page.fill("#login", ODOO_USER)
        page.fill("#password", ODOO_PASSWORD)
        page.click("button[type='submit']")
        
        print("Esperando login...")
        page.wait_for_url(lambda url: "/web" in url or "/odoo" in url, timeout=30000)
        time.sleep(5)

        # --- CONTACTOS CRUD ---
        print("Módulo Contactos: Capturando CRUD...")
        page.goto(f"{ODOO_URL}/web#action=contacts.action_contacts")
        time.sleep(5)
        # 1. Lista de Contactos
        draw_red_box_and_save(page, ".o_kanban_view", "contactos_listado.png")
        
        # 2. Formulario de creación
        page.click(".o-kanban-button-new, .o_list_button_add")
        time.sleep(3)
        draw_red_box_and_save(page, ".o_form_sheet", "contactos_nuevo.png")

        # --- INVENTARIO CRUD ---
        print("Módulo Inventario: Capturando CRUD...")
        # Lista de Productos
        page.goto(f"{ODOO_URL}/web#action=stock.product_template_action_product")
        time.sleep(5)
        draw_red_box_and_save(page, ".o_kanban_view", "inventario_productos_lista.png")
        
        # Formulario de creación de Producto
        page.click(".o-kanban-button-new, .o_list_button_add")
        time.sleep(3)
        draw_red_box_and_save(page, ".o_form_sheet", "inventario_producto_nuevo.png")

        # --- VENTAS CRUD ---
        print("Módulo Ventas B2B: Capturando CRUD...")
        page.goto(f"{ODOO_URL}/web#action=sale.action_orders")
        time.sleep(5)
        # Lista de Cotizaciones/Órdenes
        draw_red_box_and_save(page, ".o_list_renderer", "ventas_listado.png")
        
        # Formulario de creación de Cotización
        page.click(".o_list_button_add")
        time.sleep(3)
        draw_red_box_and_save(page, ".o_form_sheet", "ventas_nuevo.png")

        browser.close()
        print("Generación de capturas de detalle completada.")

if __name__ == "__main__":
    main()
