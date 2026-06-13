#!/usr/bin/env python3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

def create_template():
    print("-> Configurando plantilla de WhatsApp para cotización personalizada...")
    client = OdooClient()
    client.connect()
    
    # 1. Obtener model_id de sale.order
    so_models = client.search_read("ir.model", [["model", "=", "sale.order"]], ["id"])
    if not so_models:
        print("❌ Error: No se encontró el modelo sale.order en Odoo.")
        return
    model_id = so_models[0]["id"]
    
    # 2. Obtener la cuenta de WhatsApp
    wa_account = client.search_read("whatsapp.account", [["name", "=", "MENSAJES WAYKI TREK"]], ["id"])
    if not wa_account:
        wa_account = client.search_read("whatsapp.account", [], ["id"], limit=1)
    if not wa_account:
        print("❌ Error: No se encontraron cuentas de WhatsApp configuradas en Odoo.")
        return
    wa_account_id = wa_account[0]["id"]
    
    # 3. Obtener el report_id para adjuntar el PDF
    reports = client.search_read(
        "ir.actions.report",
        domain=[["name", "=", "WTK - PDF Cotización cliente (SO)"], ["model", "=", "sale.order"]],
        fields=["id"],
        limit=1
    )
    report_id = reports[0]["id"] if reports else False
    
    # 4. Datos de la plantilla
    template_name = "wtk_custom_quotation"
    body = (
        "¡Hola {{1}}! 👋\n\n"
        "Te adjuntamos los detalles de tu cotización personalizada para el paquete *{{2}}*.\n\n"
        "👥 *Pasajeros (PAX):* {{3}}\n"
        "💵 *Precio por PAX:* {{4}}\n"
        "💰 *Precio Total:* {{5}}\n\n"
        "Si tienes alguna duda o deseas realizar algún cambio, por favor avísanos. 🏔️"
    )
    
    existing = client.search_read("whatsapp.template", [["name", "=", template_name]], ["id"])
    vals = {
        "name": template_name,
        "template_name": template_name,
        "wa_account_id": wa_account_id,
        "model_id": model_id,
        "phone_field": "partner_id.phone",
        "lang_code": "es",
        "template_type": "utility",
        "body": body,
        "status": "approved",
        "report_id": report_id,
    }
    
    if existing:
        template_id = existing[0]["id"]
        client.write("whatsapp.template", [template_id], vals)
        print(f"✅ Plantilla '{template_name}' actualizada (ID={template_id}).")
    else:
        template_id = client.create("whatsapp.template", vals)
        print(f"✅ Plantilla '{template_name}' creada (ID={template_id}).")
        
    # 5. Configurar variables de la plantilla ({{1}} a {{5}})
    existing_vars = client.search_read("whatsapp.template.variable", [["wa_template_id", "=", template_id]], ["id"])
    if existing_vars:
        client.execute("whatsapp.template.variable", "unlink", [v["id"] for v in existing_vars])
        
    vars_data = [
        {
            "name": "{{1}}",
            "wa_template_id": template_id,
            "line_type": "body",
            "field_type": "field",
            "field_name": "partner_id.name",
            "demo_value": "Cliente de Ejemplo",
        },
        {
            "name": "{{2}}",
            "wa_template_id": template_id,
            "line_type": "body",
            "field_type": "field",
            "field_name": "x_package_name",
            "demo_value": "Inca Trail 4 días",
        },
        {
            "name": "{{3}}",
            "wa_template_id": template_id,
            "line_type": "body",
            "field_type": "field",
            "field_name": "x_custom_quote_wizard_id.x_passenger_qty",
            "demo_value": "4",
        },
        {
            "name": "{{4}}",
            "wa_template_id": template_id,
            "line_type": "body",
            "field_type": "field",
            "field_name": "x_custom_quote_wizard_id.x_final_price",
            "demo_value": "$250.00",
        },
        {
            "name": "{{5}}",
            "wa_template_id": template_id,
            "line_type": "body",
            "field_type": "field",
            "field_name": "x_custom_quote_wizard_id.x_final_price_total",
            "demo_value": "$1000.00",
        }
    ]
    
    for var_vals in vars_data:
        client.create("whatsapp.template.variable", var_vals)
        
    print("🎉 Variables de plantilla configuradas exitosamente.")

if __name__ == "__main__":
    create_template()
