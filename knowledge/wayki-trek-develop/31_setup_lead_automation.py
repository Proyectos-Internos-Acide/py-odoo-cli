#!/usr/bin/env python3
"""
Setup CRM Lead Automation for Wayki Trek.
- Automates moving stagnant leads in 'Nuevo Lead' stage (ID 5) to 'Seguimiento' stage (ID 12).
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

def setup_lead_automation(client: OdooClient):
    print("🚀 Configurando automatización de movimiento de leads...")
    
    crm_lead_model_id = get_model_id(client, "crm.lead")
    create_date_field_id = get_field_id(client, "crm.lead", "create_date")
    
    # Parámetros basados en TEST_MODE
    if TEST_MODE:
        delay_qty = 1
        delay_unit = "minutes"
        mode_desc = "1 Minuto (Modo Prueba)"
    else:
        delay_qty = 3
        delay_unit = "day"
        mode_desc = "3 Días (Modo Producción)"
        
    rule_name = "WTK - Movimiento automático de Leads estancados"
    
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
        "trg_date_id": create_date_field_id,
        "trg_date_range": delay_qty,
        "trg_date_range_type": delay_unit,
        "filter_domain": '[("stage_id", "=", 5)]',  # Nuevo Lead (Captación Automática)
        "active": True,
    }
    
    if existing_rule:
        rule_id = existing_rule[0]["id"]
        client.write("base.automation", [rule_id], vals_automation)
        print(f"✅ Regla de automatización actualizada ({mode_desc}). ID: {rule_id}")
    else:
        rule_id = client.create("base.automation", vals_automation)
        print(f"✅ Regla de automatización creada ({mode_desc}). ID: {rule_id}")

    # Fijar prioridad=0 en el cron encargado de ejecutar las reglas de tiempo (ID 49).
    # En Odoo SaaS, prioridad=0 es la máxima y garantiza que el cron no sea postergado.
    # La prioridad vive en ir.cron, no en base.automation.
    cron_automation_id = client.search_read("ir.cron", [["name", "=", "Automation Rules: check and execute"]], ["id"], limit=1)
    if cron_automation_id:
        client.write("ir.cron", [cron_automation_id[0]["id"]], {"priority": 0})
        print(f"✅ Prioridad del cron de automatización fijada a 0 (máxima). ID: {cron_automation_id[0]['id']}")
        
    # 2. Crear o actualizar la acción del servidor vinculada (ir.actions.server)
    action_name = f"WTK - Mover Lead a Seguimiento"
    
    existing_action = client.search_read(
        "ir.actions.server",
        [["name", "=", action_name], ["model_id", "=", crm_lead_model_id]],
        ["id"],
        limit=1
    )
    
    vals_action = {
        "name": action_name,
        "model_id": crm_lead_model_id,
        "state": "code",
        # Cambia al stage_id 12 ('Seguimiento') si está en el stage_id 5
        "code": (
            "if record.stage_id.id == 5:\n"
            "    record.write({'stage_id': 12})\n"
        ),
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
    print("ℹ️ NOTA TÉCNICA: Los triggers basados en tiempo ('on_time') son evaluados periódicamente")
    print("por el cron de Odoo. Si deseas probarlo al instante, puedes ejecutar manualmente la")
    print("acción programada (Settings > Technical > Scheduled Actions > 'Automation Rules: check delay rules')")

def main():
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado a Odoo (uid={uid})")
    setup_lead_automation(client)

if __name__ == "__main__":
    main()
