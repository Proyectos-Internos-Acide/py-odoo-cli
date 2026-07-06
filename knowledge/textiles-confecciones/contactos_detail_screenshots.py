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

        # Ir a la ficha de un contacto usando url directa de formulario
        # Así evitamos fallos al hacer clic en kanban
        print("Navegando a la vista formulario de un contacto...")
        page.goto(f"{ODOO_URL}/web#action=contacts.action_contacts&view_type=form")
        time.sleep(6)

        # Captura del Chatter de Odoo (normalmente a la derecha o abajo en la vista formulario)
        draw_red_box_and_save(page, ".o_FormRenderer_chatter, .o_chatter, .o-mail-Chatter", "contactos_chatter.png")

        browser.close()
        print("Chatter capturado correctamente.")

if __name__ == "__main__":
    main()
