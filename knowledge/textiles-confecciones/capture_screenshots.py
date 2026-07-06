import os
import sys
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Asegurar carga del .env
load_dotenv()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")
OUTPUT_DIR = "/home/acide/Descargas/project-reports/TEXTILES-Y-CONFECCIONES-ATLAS/Manual/images"

def draw_red_box_and_save(page, selector, output_name):
    try:
        # Intentar esperar al elemento
        page.wait_for_selector(selector, timeout=10000)
        # Añadir un recuadro rojo mediante evaluación de JS
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
        # Tomar captura normal de respaldo
        dest_path = os.path.join(OUTPUT_DIR, output_name)
        page.screenshot(path=dest_path)
        print(f"Captura de respaldo guardada: {dest_path}")

def main():
    if not ODOO_URL or not ODOO_USER or not ODOO_PASSWORD:
        print("Error: Configuración de .env incompleta para Playwright.")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with sync_playwright() as p:
        print("Iniciando navegador Chromium...")
        browser = p.chromium.launch(headless=True)
        # Configurar pantalla ancha
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # 1. Login en Odoo
        login_url = f"{ODOO_URL}/web/login"
        print(f"Navegando a la página de login: {login_url}")
        page.goto(login_url)
        page.wait_for_selector("#login", timeout=15000)

        # Rellenar credenciales
        page.fill("#login", ODOO_USER)
        page.fill("#password", ODOO_PASSWORD)
        
        # Enviar formulario
        page.click("button[type='submit']")
        
        # Esperar a que cargue el dashboard de Odoo
        print("Esperando la carga del panel principal...")
        page.wait_for_url(lambda url: "/web" in url or "/odoo" in url, timeout=30000)
        time.sleep(5) # Espera extra para renderizado de menúes

        # Captura 1: Tablero de Inventario (Dashboard general de Apps)
        # Navegamos a Inventario
        print("Navegando al módulo de Inventario...")
        page.goto(f"{ODOO_URL}/web#action=stock.action_stock_warehouse_key")
        time.sleep(5)
        # Resaltamos el dashboard de inventario
        draw_red_box_and_save(page, ".o_kanban_view", "inventario_dashboard.png")

        # Captura 2: Ficha del Contacto / Clientes
        print("Navegando al módulo de Contactos...")
        page.goto(f"{ODOO_URL}/web#action=contacts.action_contacts")
        time.sleep(5)
        # Resaltamos el botón de creación o la lista
        draw_red_box_and_save(page, ".o-kanban-button-new, .o_list_button_add", "contactos_ficha_cliente.png")

        # Captura 3: Código de Barras
        print("Navegando al módulo de Código de Barras...")
        page.goto(f"{ODOO_URL}/web#action=stock_barcode.stock_barcode_action_main_menu")
        time.sleep(5)
        draw_red_box_and_save(page, ".o_barcode_client_action, body", "barcode_escaneo.png")

        # Captura 4: Punto de Venta (Dashboard del PoS)
        print("Navegando al Punto de Venta...")
        page.goto(f"{ODOO_URL}/web#action=point_of_sale.action_pos_config_kanban")
        time.sleep(5)
        draw_red_box_and_save(page, ".o_kanban_view, body", "pos_interfaz_completa.png")

        # Captura 5: Ventas (Listado de órdenes o cotizaciones)
        print("Navegando a Ventas...")
        page.goto(f"{ODOO_URL}/web#action=sale.action_orders")
        time.sleep(5)
        draw_red_box_and_save(page, ".o_list_renderer, .o_list_view", "ventas_flujo.png")

        browser.close()
        print("Capturas automatizadas finalizadas.")

if __name__ == "__main__":
    main()
