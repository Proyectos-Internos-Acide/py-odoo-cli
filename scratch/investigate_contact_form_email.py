import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    print("=== 1. Automated Actions related to Lead/CRM or Webhook ===")
    automations = client.search_read(
        'base.automation',
        domain=[],
        fields=['id', 'name', 'model_id', 'trigger', 'action_server_ids', 'filter_domain', 'active']
    )
    for a in automations:
        model_name = a['model_id'][1] if a['model_id'] else 'N/A'
        print(f"ID: {a['id']} | Trigger: {a['trigger']} | Model: {model_name} | Name: '{a['name']}'")

    print("\n=== 2. Server Action 582 (Wayki: Trigger Parse JSON V2) ===")
    sa582 = client.search_read('ir.actions.server', domain=[('id', '=', 582)], fields=['name', 'code'])
    if sa582:
        print(sa582[0]['name'])
        print(sa582[0]['code'])

    print("\n=== 3. Server Action 651 (Notificar Vendedor Correo CRM) ===")
    sa651 = client.search_read('ir.actions.server', domain=[('id', '=', 651)], fields=['name', 'code'])
    if sa651:
        print(sa651[0]['name'])
        print(sa651[0]['code'])

    print("\n=== 4. Email Aliases configured in Odoo ===")
    aliases = client.search_read(
        'mail.alias',
        domain=[],
        fields=['alias_name', 'alias_model_id', 'alias_user_id', 'alias_defaults', 'alias_domain', 'alias_parent_model_id']
    )
    for al in aliases:
        model_name = al['alias_model_id'][1] if al['alias_model_id'] else 'N/A'
        user_name = al['alias_user_id'][1] if al['alias_user_id'] else 'N/A'
        print(f"Alias: '{al['alias_name']}' | Model: {model_name} | User: {user_name} | Defaults: {al['alias_defaults']}")

    print("\n=== 5. Incoming Mail Servers ===")
    incoming = client.search_read(
        'fetchmail.server',
        domain=[],
        fields=['name', 'server', 'user', 'state', 'object_id']
    )
    for s in incoming:
        model_name = s['object_id'][1] if s['object_id'] else 'N/A'
        print(f"Server: '{s['name']}' | Host: {s['server']} | User: {s['user']} | State: {s['state']} | Model: {model_name}")

if __name__ == '__main__':
    main()
