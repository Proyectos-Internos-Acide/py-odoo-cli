#!/usr/bin/env python3
"""
Setup CRM Lead Smart WhatsApp Automation for Wayki Trek.
- Automates moving leads in 'Primer mensaje' stage (ID 11) to 'Seguimiento' stage (ID 12) if:
  1. No WhatsApp channel/message exists for the client.
  2. The last message was sent by us (sales/system) and the client has not replied.
- Configurable delay (1 minute for testing, 3 days for production).
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

# CONFIGURACIÓN: Cambiar a False para producción (3 días)
TEST_MODE = True

def get_model_id(client: OdooClient, model_name: str) -> int:
    rec = client.search_read("ir.model", [["model", "=", model_name]], ["id"], limit=1)
    if not rec:
        raise ValueError(f"Modelo {model_name} no encontrado")
    return rec[0]["id"]

def get_field_id(client: OdooClient, model_name: str, field_name: str) -> int:
    rec = client.search_read(
        "ir.model.fields",
        [["model", "=", model_name], ["name", "=", field_name]],
        ["id"],
        limit=1
    )
    if not rec:
        raise ValueError(f"Campo {field_name} para {model_name} no encontrado")
    return rec[0]["id"]

def setup_lead_whatsapp_automation(client: OdooClient):
    print("🚀 Configurando automatización inteligente de WhatsApp...")
    
    crm_lead_model_id = get_model_id(client, "crm.lead")
    date_last_stage_update_field_id = get_field_id(client, "crm.lead", "date_last_stage_update")
    
    # Parámetros basados en TEST_MODE
    if TEST_MODE:
        delay_qty = 1
        delay_unit = "minutes"
        mode_desc = "1 Minuto (Modo Prueba)"
    else:
        delay_qty = 3
        delay_unit = "day"
        mode_desc = "3 Días (Modo Producción)"
        
    rule_name = "WTK - WhatsApp Lead No Respondido o Estancado"
    
    # 1. Crear o actualizar la regla de automatización (base.automation)
    existing_rule = client.search_read(
        "base.automation",
        [["name", "=", rule_name]],
        ["id"],
        limit=1
    )
    
    vals_automation = {
        "name": rule_name,
        "model_id": crm_lead_model_id,
        "trigger": "on_time",
        "trg_date_id": date_last_stage_update_field_id,
        "trg_date_range": delay_qty,
        "trg_date_range_type": delay_unit,
        "filter_domain": '[("stage_id", "=", 11)]',  # Primer mensaje (ID 11)
        "active": True,
    }
    
    if existing_rule:
        rule_id = existing_rule[0]["id"]
        client.write("base.automation", [rule_id], vals_automation)
        print(f"✅ Regla de automatización actualizada ({mode_desc}). ID: {rule_id}")
    else:
        rule_id = client.create("base.automation", vals_automation)
        print(f"✅ Regla de automatización creada ({mode_desc}). ID: {rule_id}")

    # Fijar prioridad=0 en el cron encargado de ejecutar las reglas de tiempo.
    # A petición especial, prioridad=0 es la máxima en Odoo SaaS.
    cron_automation_id = client.search_read("ir.cron", [["name", "=", "Automation Rules: check and execute"]], ["id"], limit=1)
    if cron_automation_id:
        client.write("ir.cron", [cron_automation_id[0]["id"]], {"priority": 0})
        print(f"✅ Prioridad del cron de automatización fijada a 0 (máxima). ID: {cron_automation_id[0]['id']}")
        
    # 2. Crear o actualizar la acción del servidor vinculada (ir.actions.server)
    action_name = "WTK - Validar y Mover Lead sin WhatsApp"
    
    existing_action = client.search_read(
        "ir.actions.server",
        [["name", "=", action_name], ["model_id", "=", crm_lead_model_id]],
        ["id"],
        limit=1
    )
    
    # Código Python inteligente a ejecutar en Odoo
    python_code = (
        "# 1. Obtener la relación con el partner del lead\n"
        "partner = record.partner_id\n\n"
        "if not partner:\n"
        "    # Si no hay partner asociado, mover a Seguimiento por seguridad\n"
        "    record.write({'stage_id': 12})\n"
        "else:\n"
        "    # 2. Buscar canales de WhatsApp vinculados a este partner\n"
        "    channels = env['discuss.channel'].search([\n"
        "        ('whatsapp_partner_id', '=', partner.id)\n"
        "    ])\n\n"
        "    if not channels:\n"
        "        # Caso A: No hay ningún canal de WhatsApp. Mover.\n"
        "        record.write({'stage_id': 12})\n"
        "    else:\n"
        "        # 3. Buscar el último mensaje de WhatsApp dentro de esos canales\n"
        "        messages = env['mail.message'].search([\n"
        "            ('model', '=', 'discuss.channel'),\n"
        "            ('res_id', 'in', channels.ids),\n"
        "            ('message_type', '=', 'whatsapp_message')\n"
        "        ], order='create_date desc', limit=1)\n\n"
        "        if not messages:\n"
        "            # Caso B: Hay canal pero no tiene mensajes. Mover.\n"
        "            record.write({'stage_id': 12})\n"
        "        else:\n"
        "            # Caso C: Hay mensajes. Validamos el autor del último\n"
        "            ultimo_mensaje = messages[0]\n"
        "            \n"
        "            # Verificamos si fue enviado por nosotros (usuario interno)\n"
        "            es_enviado_por_nosotros = bool(ultimo_mensaje.author_id.user_ids)\n"
        "            \n"
        "            if es_enviado_por_nosotros:\n"
        "                # El cliente no ha respondido a nuestro mensaje\n"
        "                record.write({'stage_id': 12})\n"
    )
    
    vals_action = {
        "name": action_name,
        "model_id": crm_lead_model_id,
        "state": "code",
        "code": python_code,
        "base_automation_id": rule_id,
    }
    
    if existing_action:
        action_id = existing_action[0]["id"]
        client.write("ir.actions.server", [action_id], vals_action)
        print(f"✅ Acción de servidor actualizada y vinculada. ID: {action_id}")
    else:
        action_id = client.create("ir.actions.server", vals_action)
        print(f"✅ Acción de servidor creada y vinculada. ID: {action_id}")
        
    print("\n🎉 Configuración completada con éxito.")
    print("ℹ️ NOTA TÉCNICA: Esta regla se activa 1 minuto después de que el lead entre a la etapa 'Primer mensaje'")
    print("según el campo 'date_last_stage_update'.")

def main():
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado a Odoo (uid={uid})")
    setup_lead_whatsapp_automation(client)

if __name__ == "__main__":
    main()
