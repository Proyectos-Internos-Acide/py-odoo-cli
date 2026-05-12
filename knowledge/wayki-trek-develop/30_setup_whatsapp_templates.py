#!/usr/bin/env python3
"""
Setup WhatsApp Templates para Wayki Trek.
- Archiva (desactiva) plantillas de WhatsApp existentes.
- Crea 3 nuevas plantillas para sale.order en estado 'draft'.
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
    # Intentamos buscar una cuenta de WhatsApp existente
    rec = client.search_read("whatsapp.account", [], ["id"], limit=1)
    return rec[0]["id"] if rec else None

def archive_existing_templates(client: OdooClient):
    # Buscamos todas las plantillas activas
    templates = client.search_read("whatsapp.template", [["active", "=", True]], ["id", "name"])
    if not templates:
        print("ℹ️ No hay plantillas activas para archivar.")
        return

    template_ids = [t["id"] for t in templates]
    # Las archivamos poniendo active=False
    client.write("whatsapp.template", template_ids, {"active": False})
    print(f"✅ Archivadas {len(template_ids)} plantillas existentes.")

def create_template(client: OdooClient, name: str, model_id: int, body: str, account_id: int | None):
    vals = {
        "name": name,
        "model_id": model_id,
        "body": body,
        "status": "draft",
        "phone_field": "partner_id.phone",
    }
    # En versiones modernas de Odoo, se suele requerir el tipo de plantilla y el id de cuenta
    # template_type: 'utility' u otros, pero probamos crearlo sin eso si no es requerido o lo dejamos a Odoo inferir
    if account_id:
        vals["wa_account_id"] = account_id
        
    try:
        new_id = client.create("whatsapp.template", vals)
        print(f"✅ Plantilla '{name}' creada con ID: {new_id}")
    except Exception as e:
        print(f"❌ Error al crear '{name}': {e}")
        # Intentamos de nuevo sin cuenta por si falla por eso
        if account_id:
            vals.pop("wa_account_id")
            try:
                new_id = client.create("whatsapp.template", vals)
                print(f"✅ Plantilla '{name}' creada (sin cuenta WA) con ID: {new_id}")
            except Exception as e2:
                print(f"❌ Re-intento fallido para '{name}': {e2}")

def main():
    print("🚀 Iniciando configuración de plantillas de WhatsApp...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado a Odoo (uid={uid})")

    archive_existing_templates(client)

    sale_model_id = get_model_id(client, "sale.order")
    wa_account_id = None
    try:
        wa_account_id = get_wa_account_id(client)
    except Exception:
        print("⚠️ No se pudo verificar cuenta de WhatsApp (puede que el módulo no esté instalado o sin permisos).")

    # 1. Envío de Cotización
    body_cotizacion = (
        "¡Hola {{1}}! 🏔️\n"
        "Te enviamos la cotización *{{2}}* para tu próxima aventura con Wayki Trek. 🥾\n\n"
        "Monto total: {{3}}\n\n"
        "Si tienes alguna duda sobre el itinerario o los servicios incluidos, respóndenos por este medio. ¡Estamos para ayudarte!"
    )
    create_template(client, "Wayki Trek: Envío de Cotización", sale_model_id, body_cotizacion, wa_account_id)

    # 2. Confirmación de Reserva
    body_reserva = (
        "¡Excelente noticia, {{1}}! 🎉\n"
        "Tu reserva *{{2}}* ha sido confirmada con éxito.\n\n"
        "Nos emociona mucho que seas parte de esta experiencia inolvidable. Pronto nos pondremos en contacto con los detalles logísticos.\n\n"
        "¡Gracias por confiar en Wayki Trek! 🎒"
    )
    create_template(client, "Wayki Trek: Confirmación de Reserva", sale_model_id, body_reserva, wa_account_id)

    # 3. Enlace de Pago
    body_pago = (
        "Hola {{1}},\n"
        "Para completar la reserva de tu tour, por favor realiza el pago pendiente de *{{2}}*.\n\n"
        "Asegura tu lugar lo más pronto posible para que podamos organizar todos los detalles de tu viaje."
    )
    create_template(client, "Wayki Trek: Enlace de Pago", sale_model_id, body_pago, wa_account_id)

    print("🎉 Proceso finalizado. Por favor, revisa las plantillas en Odoo (WhatsApp > Plantillas) y asocia las variables a los campos correctos.")

if __name__ == "__main__":
    main()
