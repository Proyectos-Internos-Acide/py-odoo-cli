#!/usr/bin/env python3
"""
Configuración de plantilla de WhatsApp para Ventas (sale.order).
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

def main():
    print("🚀 Configurando plantillas de WhatsApp para Ventas...")
    client = OdooClient()
    uid = client.connect()
    
    # Obtener IDs
    sale_model_id = client.search_read("ir.model", [["model", "=", "sale.order"]], ["id"], limit=1)[0]["id"]
    
    try:
        acc = client.search_read("whatsapp.account", [], ["id"], limit=1)
        wa_account_id = acc[0]["id"] if acc else None
    except:
        wa_account_id = None

    # Plantilla de Cotización para Ventas
    body = (
        "¡Hola {{1}}! 🏕️\n"
        "Adjunto encontrarás el detalle y la cotización oficial de tu viaje (Ref: {{2}}) 📄. "
        "Por favor, revisa el documento adjunto para ver todo el itinerario y los servicios incluidos ✨.\n\n"
        "Si todo está conforme o tienes alguna duda, escríbenos por aquí. ¡Estamos listos para tu aventura! 🎒"
    )
    
    vals = {
        "name": "wtk_venta_cotizacion",
        "model_id": sale_model_id,
        "body": body,
        "status": "draft",
        "phone_field": "partner_id.phone",
        "lang_code": "es",
        "template_type": "marketing",
        "header_type": "none", # Lo dejamos none temporalmente para evitar error al crear
    }
    if wa_account_id:
        vals["wa_account_id"] = wa_account_id
        
    template_id = client.create("whatsapp.template", vals)
    print(f"✅ Plantilla 'wtk_venta_cotizacion' creada con ID: {template_id}")

    # Configurar las variables
    vars_recs = client.search_read("whatsapp.template.variable", [["wa_template_id", "=", template_id]], ["id", "name"])
    for v in vars_recs:
        if v["name"] == "{{1}}":
            client.write("whatsapp.template.variable", [v["id"]], {"field_type": "field", "field_name": "partner_id.name"})
        elif v["name"] == "{{2}}":
            client.write("whatsapp.template.variable", [v["id"]], {"field_type": "field", "field_name": "name"})
            
    print("🎉 Plantilla configurada con variables (partner_id.name y name).")

if __name__ == "__main__":
    main()
