import sys
import os
from dotenv import load_dotenv
import xmlrpc.client

load_dotenv()

URL = os.getenv("ODOO_URL")
DB = os.getenv("ODOO_DB")
USER = os.getenv("ODOO_USER")
PASS = os.getenv("ODOO_PASSWORD")

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

print(f"Connected to {URL} DB {DB} as UID {uid}")

# Search for ir.actions.server related to crm.lead, res.partner, or email
server_actions = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'search_read',
    [[]], {'fields': ['id', 'name', 'model_id', 'state', 'code']})

print("\n--- SERVER ACTIONS ---")
for sa in server_actions:
    code = sa.get('code') or ''
    name = sa.get('name') or ''
    if any(k in code.lower() or k in name.lower() for k in ['partner', 'email', 'lead', 'contact', 'auto-ligar']):
        print(f"\nID: {sa['id']} | Name: {sa['name']} | Model: {sa.get('model_id')}")
        print("CODE:")
        print(code[:1000])

print("\n--- BASE AUTOMATIONS ---")
try:
    automations = models.execute_kw(DB, uid, PASS, 'base.automation', 'search_read',
        [[]], {'fields': ['id', 'name', 'model_id', 'trigger', 'action_server_ids']})
    for auto in automations:
        print(f"ID: {auto['id']} | Name: {auto['name']} | Model: {auto.get('model_id')} | Trigger: {auto.get('trigger')} | Server Actions: {auto.get('action_server_ids')}")
except Exception as e:
    print(f"Error fetching base.automation: {e}")
