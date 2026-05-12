#!/usr/bin/env python3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient
from models_and_fields import run as run_models
from logic_and_automations import run as run_logic
from reports import run as run_reports
from views import run as run_views

def main():
    print("Configurando modal de cotización personalizada (V3) - MODULAR...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")
    
    wizard_model, wizard_line_model, wizard_service_line_model = run_models(client)
    run_logic(client, wizard_model, wizard_service_line_model)
    print_action_id, client_print_action_id = run_reports(client, wizard_model)
    run_views(client, wizard_model, print_action_id, client_print_action_id)
    
    print("🎉 V3 Modular lista.")

if __name__ == "__main__":
    main()
