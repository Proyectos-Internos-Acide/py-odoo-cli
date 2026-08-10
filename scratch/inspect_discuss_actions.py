import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    print("=== Inspecting actions registered for discuss.channel ===")
    actions = client.search_read(
        'ir.actions.server',
        domain=[('model_id.model', '=', 'discuss.channel')],
        fields=['id', 'name', 'binding_model_id', 'binding_type']
    )
    print(f"Found {len(actions)} server actions bound to discuss.channel:")
    for a in actions:
        print(a)

    print("\n=== Inspecting actions registered for whatsapp.message ===")
    actions_wm = client.search_read(
        'ir.actions.server',
        domain=[('model_id.model', '=', 'whatsapp.message')],
        fields=['id', 'name', 'binding_model_id', 'binding_type']
    )
    print(f"Found {len(actions_wm)} server actions bound to whatsapp.message:")
    for a in actions_wm:
        print(a)

    print("\n=== Inspecting actions registered for res.partner ===")
    actions_rp = client.search_read(
        'ir.actions.server',
        domain=[('model_id.model', '=', 'res.partner'), ('name', 'like', 'WTK')],
        fields=['id', 'name', 'binding_model_id', 'binding_type']
    )
    print(f"Found {len(actions_rp)} WTK server actions bound to res.partner:")
    for a in actions_rp:
        print(a)

if __name__ == '__main__':
    main()
