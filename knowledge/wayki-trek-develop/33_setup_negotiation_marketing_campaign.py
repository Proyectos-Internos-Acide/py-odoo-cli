#!/usr/bin/env python3
"""
Setup CRM Lead 'Social Proof' Marketing Automation Campaign for Wayki Trek.
- Creates a marketing campaign for leads in 'Negociación / Cotización' stage (ID 6).
- Triggers a Server Action to send a WhatsApp testimonial & TripAdvisor message.
- Configurable delay (1 hour for testing, 2 days for production).
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

# CONFIGURACIÓN: Cambiar a False para producción (2 días)
TEST_MODE = True

def get_model_id(client: OdooClient, model_name: str) -> int:
    rec = client.search_read("ir.model", [["model", "=", model_name]], ["id"], limit=1)
    if not rec:
        raise ValueError(f"Modelo {model_name} no encontrado")
    return rec[0]["id"]

def setup_negotiation_marketing_campaign(client: OdooClient):
    print("🚀 Configurando Campaña de Marketing de Prueba Social...")
    
    crm_lead_model_id = get_model_id(client, "crm.lead")
    
    # 1. Crear o actualizar la acción del servidor vinculada (ir.actions.server)
    action_name = "WTK - Mkt Campaign: Enviar Social Proof WhatsApp"
    
    existing_action = client.search_read(
        "ir.actions.server",
        [["name", "=", action_name], ["model_id", "=", crm_lead_model_id]],
        ["id"],
        limit=1
    )
    
    # Código Python inteligente a ejecutar en Odoo
    python_code = (
        "# 1. Obtener la relación con el partner del lead\n"
        "partner = record.partner_id\n"
        "if partner:\n"
        "    # Buscar el canal de WhatsApp de este partner\n"
        "    channels = env['discuss.channel'].search([\n"
        "        ('whatsapp_partner_id', '=', partner.id)\n"
        "    ])\n"
        "    \n"
        "    # Cuerpo del mensaje interactivo (Prueba Social y Video)\n"
        "    msg_body = (\n"
        "        \"<p>¡Hola %s! Sé que estás planeando tu aventura a %s. Quería compartirte este breve video de 1 minuto sobre cómo es un día de campamento con nuestro equipo de Wayki Trek: https://youtu.be/video_waykitrek. Además, más del 98%% de nuestros caminantes nos califican con 5 estrellas en TripAdvisor. ¿Tienes alguna duda sobre la preparación física o el equipo necesario? Estoy aquí para ayudarte.</p>\"\n"
        "        % (partner.name, record.name or 'Perú')\n"
        "    )\n"
        "    \n"
        "    if channels:\n"
        "        # Enviar mensaje real de WhatsApp al canal existente\n"
        "        channels[0].message_post(\n"
        "            body=msg_body,\n"
        "            message_type='whatsapp_message'\n"
        "        )\n"
        "        \n"
        "    # Registrar nota interna en el Chatter del CRM Lead\n"
        "    record.message_post(\n"
        "        body=\"<b>Campaña de Marketing Activa:</b> Se envió el mensaje de Prueba Social por WhatsApp.\",\n"
        "        subtype_xmlid=\"mail.mt_note\"\n"
        "    )\n"
    )
    
    vals_action = {
        "name": action_name,
        "model_id": crm_lead_model_id,
        "state": "code",
        "code": python_code,
    }
    
    if existing_action:
        action_id = existing_action[0]["id"]
        client.write("ir.actions.server", [action_id], vals_action)
        print(f"✅ Acción de servidor actualizada. ID: {action_id}")
    else:
        action_id = client.create("ir.actions.server", vals_action)
        print(f"✅ Acción de servidor creada. ID: {action_id}")

    # 2. Crear o actualizar la Campaña de Marketing (marketing.campaign)
    campaign_name = "WTK - Campaña: Prueba Social y Acompañamiento"
    
    existing_campaign = client.search_read(
        "marketing.campaign",
        [["name", "=", campaign_name]],
        ["id"],
        limit=1
    )
    
    vals_campaign = {
        "name": campaign_name,
        "model_id": crm_lead_model_id,
        "domain": '[("stage_id", "=", 6)]',  # Negociación / Cotización (ID 6)
        "state": "draft",  # Creada en Borrador para revisión visual del usuario
    }
    
    if existing_campaign:
        campaign_id = existing_campaign[0]["id"]
        client.write("marketing.campaign", [campaign_id], vals_campaign)
        print(f"✅ Campaña de marketing actualizada. ID: {campaign_id}")
    else:
        campaign_id = client.create("marketing.campaign", vals_campaign)
        print(f"✅ Campaña de marketing creada. ID: {campaign_id}")

    # 3. Crear o actualizar la Actividad de la Campaña (marketing.activity)
    activity_name = "WTK - Enviar Social Proof WhatsApp"
    
    existing_activity = client.search_read(
        "marketing.activity",
        [["name", "=", activity_name], ["campaign_id", "=", campaign_id]],
        ["id"],
        limit=1
    )
    
    # Parámetros basados en TEST_MODE
    if TEST_MODE:
        interval_qty = 1
        interval_unit = "hours"
        mode_desc = "1 Hora (Modo Prueba)"
    else:
        interval_qty = 2
        interval_unit = "days"
        mode_desc = "2 Días (Modo Producción)"
        
    vals_activity = {
        "name": activity_name,
        "campaign_id": campaign_id,
        "activity_type": "action",  # Tipo Acción de Servidor
        "trigger_type": "begin",  # Al inicio de la campaña
        "interval_number": interval_qty,
        "interval_type": interval_unit,
        "server_action_id": action_id,
    }
    
    if existing_activity:
        activity_id = existing_activity[0]["id"]
        client.write("marketing.activity", [activity_id], vals_activity)
        print(f"✅ Actividad de campaña actualizada ({mode_desc}). ID: {activity_id}")
    else:
        activity_id = client.create("marketing.activity", vals_activity)
        print(f"✅ Actividad de campaña creada ({mode_desc}). ID: {activity_id}")
        
    print("\n🎉 Campaña de Marketing configurada con éxito en Odoo.")
    print("ℹ️ NOTA: La campaña se creó en estado 'Borrador' (Draft).")
    print("Para activarla:")
    print("1. Entra a Odoo > Automatización de Marketing.")
    # El ID es único y permite un enlace directo si lo desean
    print(f"2. Abre la campaña '{campaign_name}' y haz clic en el botón 'Iniciar' (Start).")

def main():
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado a Odoo (uid={uid})")
    setup_negotiation_marketing_campaign(client)

if __name__ == "__main__":
    main()
