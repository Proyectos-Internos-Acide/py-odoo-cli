import os
from dotenv import load_dotenv
import xmlrpc.client
import json

load_dotenv()

URL = os.getenv("ODOO_URL")
DB = os.getenv("ODOO_DB")
USER = os.getenv("ODOO_USER")
PASS = os.getenv("ODOO_PASSWORD")

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

lead_id = 1939

print(f"Inspeccionando Oportunidad/Lead ID {lead_id}...")
lead = models.execute_kw(DB, uid, PASS, 'crm.lead', 'read', [[lead_id]])

if lead:
    l = lead[0]
    print("=== CAMPOS PRINCIPALES ===")
    print(f"ID: {l['id']}")
    print(f"Name: {l['name']}")
    print(f"Contact Name: {l.get('contact_name')}")
    print(f"Email From: {l.get('email_from')}")
    print(f"Phone: {l.get('phone')}")
    print(f"Partner: {l.get('partner_id')}")
    print(f"Created At: {l.get('create_date')}")
    print(f"Create UID: {l.get('create_uid')}")
    print(f"x_wayki_sync_payload: {l.get('x_wayki_sync_payload')}")
    
    print("\n=== DESCRIPTION (HTML o Payload) ===")
    print(l.get('description'))

    print("\n=== MENSAJES DEL CHATTER ===")
    messages = models.execute_kw(DB, uid, PASS, 'mail.message', 'search_read',
        [[('model', '=', 'crm.lead'), ('res_id', '=', lead_id)]],
        {'fields': ['id', 'date', 'body', 'author_id'], 'order': 'id asc'})
    for m in messages:
        print(f"Msg ID: {m['id']} | Date: {m['date']} | Author: {m['author_id']}")
        print(f"Body: {m['body']}")
        print("-" * 30)
else:
    print(f"No se encontró el Lead {lead_id}")
