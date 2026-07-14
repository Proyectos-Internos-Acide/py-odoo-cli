import os
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright

root_env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(root_env_path)

ODOO_URL = os.getenv('ODOO_URL', 'https://wayki-trek.odoo.com')
ODOO_USER = os.getenv('ODOO_USER', 'leocusi@waykitrek.net')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'usuario123')

BASE_DIR = Path(__file__).parent
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
REPORT_PATH = BASE_DIR / "tableros_reporte.md"

DASHBOARDS = [
    {"id": 1, "name": "Leads"},
    {"id": 2, "name": "Pipeline"},
    {"id": 3, "name": "Email Marketing"},
    {"id": 4, "name": "Invoicing"},
    {"id": 5, "name": "Sales"},
    {"id": 6, "name": "Product"}
]

async def run():
    print("Iniciando automatización de captura de todos los tableros...")
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()

        report_markdown = "# Reporte de Auditoría Visual: Tableros Odoo\n\n"
        report_markdown += f"**Fecha de generación:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report_markdown += f"**Entorno:** {ODOO_URL}\n\n"

        try:
            print("Navegando a Odoo para login...")
            await page.goto(f"{ODOO_URL}/web/login", wait_until="load")
            
            await page.wait_for_selector('input[name="login"]', timeout=15000)
            await page.fill('input[name="login"]', ODOO_USER)
            await page.fill('input[name="password"]', ODOO_PASSWORD)
            await page.click('button[type="submit"]')
            
            print("Esperando menú principal de Odoo...")
            await page.wait_for_selector('.o_home_menu, .o_home_menu_background', timeout=15000)
            
            try:
                print("Haciendo click en la aplicación Tableros...")
                await page.locator('.o_app', has_text='Tableros').first.click()
                await page.wait_for_selector('.o_spreadsheet_dashboard_action, .o_spreadsheet_container', timeout=15000)
            except Exception as e:
                print("Aviso: No se pudo hacer click inicial en Tableros.")

            for dashboard in DASHBOARDS:
                dashboard_id = dashboard["id"]
                dashboard_name = dashboard["name"]
                
                try:
                    print(f"\nNavegando al tablero: {dashboard_name} (ID: {dashboard_id})")
                    
                    try:
                        tab_locator = page.locator('.o_search_panel_category_value', has_text=dashboard_name).first
                        await tab_locator.wait_for(state="visible", timeout=3000)
                        await tab_locator.click()
                        print(f"Clickeado '{dashboard_name}' en el panel lateral.")
                    except Exception:
                        try:
                            fallback_locator = page.locator(f"xpath=//*[text()='{dashboard_name}']").first
                            await fallback_locator.wait_for(state="visible", timeout=3000)
                            await fallback_locator.click()
                            print(f"Clickeado '{dashboard_name}' usando selector de texto.")
                        except Exception:
                            print("Forzando recarga de página por hash.")
                            hash_url = f"action=spreadsheet_dashboard.spreadsheet_dashboard_action&active_id={dashboard_id}"
                            await page.evaluate(f"window.location.hash = '{hash_url}'")
                            await page.reload(wait_until="load")
                    
                    print(f"Esperando que el tablero '{dashboard_name}' termine de cargar...")
                    
                    try:
                        await page.wait_for_selector('.o_blockUI', state='hidden', timeout=5000)
                    except Exception:
                        pass
                    
                    target_locator = page
                    try:
                        locator = page.locator(".o_spreadsheet_dashboard_action, .o_spreadsheet_container").first
                        await locator.wait_for(state="visible", timeout=15000)
                        target_locator = locator
                    except Exception:
                        print(f"Aviso: Selector de contenedor no encontrado para {dashboard_name}. Capturando página entera.")
                        
                    await page.wait_for_timeout(8000)
                    
                    safe_name = dashboard_name.replace(' ', '_').lower()
                    file_name = f"tablero_{dashboard_id}_{safe_name}.png"
                    file_path = SCREENSHOTS_DIR / file_name
                    
                    await target_locator.screenshot(path=str(file_path))
                    print(f"Captura guardada: {file_name}")
                    
                    report_markdown += f"## Tablero: {dashboard_name}\n"
                    report_markdown += f"> Vista capturada automáticamente para {dashboard_name}.\n\n"
                    report_markdown += f"![{dashboard_name}](./screenshots/{file_name})\n\n"
                    
                except Exception as e:
                    print(f"Error capturando el tablero {dashboard_name}: {e}")
                    report_markdown += f"## Tablero: {dashboard_name}\n"
                    report_markdown += f"⚠️ **Error crítico al capturar el tablero:** {e}\n\n"
            
            with open(REPORT_PATH, "w", encoding="utf-8") as f:
                f.write(report_markdown)
            
            print(f"\n¡Éxito! Reporte actualizado generado en: {REPORT_PATH}")
            
        except Exception as e:
            print(f"Error crítico de login o inicialización: {e}")
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
