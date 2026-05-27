#!/usr/bin/env python3
"""
Configuración de plantillas de WhatsApp para CRM (Wayki Trek).
- Crea 5 plantillas en estado 'draft' (borrador) con idioma 'es' y tipo 'marketing'.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

def get_model_id(client: OdooClient, model_name: str) -> int:
    rec = client.search_read("ir.model", [["model", "=", model_name]], ["id"], limit=1)
    if not rec:
        raise ValueError(f"Modelo {model_name} no encontrado")
    return rec[0]["id"]

def get_wa_account_id(client: OdooClient) -> int | None:
    rec = client.search_read("whatsapp.account", [], ["id"], limit=1)
    return rec[0]["id"] if rec else None

def create_template(client: OdooClient, name: str, model_id: int, body: str, account_id: int | None, header_type: str = "none"):
    vals = {
        "name": name,
        "model_id": model_id,
        "body": body,
        "status": "draft",
        "phone_field": "phone",
        "lang_code": "es",
        "template_type": "marketing",
        "header_type": header_type,
    }
    if account_id:
        vals["wa_account_id"] = account_id
        
    try:
        new_id = client.create("whatsapp.template", vals)
        print(f"✅ Plantilla '{name}' creada con ID: {new_id}")
    except Exception as e:
        print(f"❌ Error al crear '{name}': {e}")
        # Reintento sin wa_account_id
        if account_id:
            vals.pop("wa_account_id")
            try:
                new_id = client.create("whatsapp.template", vals)
                print(f"✅ Plantilla '{name}' creada (sin cuenta WA) con ID: {new_id}")
            except Exception as e2:
                print(f"❌ Reintento fallido para '{name}': {e2}")

def main():
    print("🚀 Configurando plantillas de WhatsApp para CRM...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado a Odoo (uid={uid})")

    crm_model_id = get_model_id(client, "crm.lead")
    wa_account_id = None
    try:
        wa_account_id = get_wa_account_id(client)
    except Exception:
        print("⚠️ No se pudo verificar cuenta de WhatsApp.")

    # 1. Bienvenida
    t1_body = (
        "¡Hola {{1}}! 👋 Somos el equipo de Wayki Trek 🏔️. Hemos recibido tu interés por nuestro tour {{2}}. "
        "Para verificar disponibilidad y organizar la mejor experiencia, ¿en qué fechas tenías planeado viajar? 📅"
    )
    create_template(client, "wtk_bienvenida_lead", crm_model_id, t1_body, wa_account_id)

    # 2. Seguimiento (3 días)
    t2_body = (
        "¡Hola {{1}}! ⏳ Hace unos días te enviamos información. Como los espacios para {{2}} se agotan rápido "
        "por regulaciones del gobierno 🏛️, queríamos saber si pudiste revisar la propuesta o si tienes alguna duda "
        "en la que podamos ayudarte 🎒."
    )
    create_template(client, "wtk_seguimiento_3dias", crm_model_id, t2_body, wa_account_id)

    # 3. Cotización (con PDF)
    t3_body = (
        "¡Hola {{1}}! ✨ Adjunto encontrarás el itinerario detallado 📄 y la cotización oficial para tu viaje. "
        "Si todo está conforme, avísanos para enviarte el link del depósito inicial y asegurar tus espacios 🎫."
    )
    create_template(client, "wtk_envio_cotizacion", crm_model_id, t3_body, wa_account_id, header_type="none")

    # 4. Cobro de Saldo
    t4_body = (
        "¡Tu aventura está muy cerca, {{1}}! 🏔️ Recuerda que para asegurar la logística final, "
        "el saldo de tu reserva debe ser cancelado 💳. Puedes realizar el pago de forma segura aquí: {{2}} 🔒"
    )
    create_template(client, "wtk_recordatorio_saldo", crm_model_id, t4_body, wa_account_id)

    # 5. Post-Venta
    t5_body = (
        "¡Hola {{1}}! 🌟 Ha sido un honor acompañarte en esta aventura. Si disfrutaste la experiencia con nuestro equipo, "
        "nos ayudaría muchísimo si compartes tu opinión en TripAdvisor 📝: {{2}}. ¡Gracias por confiar en Wayki Trek! 🙏"
    )
    create_template(client, "wtk_post_tour_review", crm_model_id, t5_body, wa_account_id)

    print("🎉 Plantillas configuradas en estado Borrador (Draft) con idioma Español.")

if __name__ == "__main__":
    main()
