import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    print("=== Checking base.automation (Automated Actions) ===")
    automations = client.search_read(
        'base.automation',
        domain=[],
        fields=['id', 'name', 'model_id', 'trigger', 'action_server_ids', 'active']
    )
    print(f"Found {len(automations)} automated actions:")
    for a in automations:
        model_name = a['model_id'][1] if a['model_id'] else 'N/A'
        print(f"  • ID: {a['id']} | Name: '{a['name']}' | Model: {model_name} | Trigger: {a['trigger']} | Server Actions: {a['action_server_ids']}")

    print("\n=== Checking Server Actions linked to wtk models ===")
    server_actions = client.search_read(
        'ir.actions.server',
        domain=['|', '|', ('model_id.model', 'like', 'wtk'), ('name', 'like', 'WTK'), ('name', 'like', 'Recalcular')],
        fields=['id', 'name', 'model_id', 'state', 'code']
    )
    for sa in server_actions:
        model_name = sa['model_id'][1] if sa['model_id'] else 'N/A'
        print(f"\nAction ID: {sa['id']} | Name: '{sa['name']}' | Model: {model_name} | State: {sa['state']}")
        print("Code snippet:")
        print(sa['code'][:300] if sa['code'] else 'No code')

if __name__ == '__main__':
    main()
