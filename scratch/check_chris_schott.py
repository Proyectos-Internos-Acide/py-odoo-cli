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

print("1. Inspeccionando Server Action ID 582 (Parse JSON)...")
a582 = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'read', [582], {'fields': ['name', 'code']})
print(a582[0]['code'])

print("\n" + "="*50 + "\n")
print("2. Buscando Server Action 'Auto-Ligar Lead por Email'...")
actions_link = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'search_read',
    [[('name', 'ilike', 'Ligar')]], {'fields': ['id', 'name', 'code']})

for a in actions_link:
    print(f"ID: {a['id']} | Name: {a['name']}")
    print(a['code'])

print("\n" + "="*50 + "\n")
print("3. Buscando el partner 'Chris Schott'...")
chris = models.execute_kw(DB, uid, PASS, 'res.partner', 'search_read',
    [[('name', 'ilike', 'Chris Schott')]], {'fields': ['id', 'name', 'email']})
print("Chris Schott:", chris)

print("\n" + "="*50 + "\n")
print("4. Buscando los últimos leads creados y su partner_id...")
leads = models.execute_kw(DB, uid, PASS, 'crm.lead', 'search_read',
    [[]], {'fields': ['id', 'name', 'partner_id', 'contact_name', 'email_from', 'create_date'], 'limit': 5, 'order': 'id desc'})
for l in leads:
    print(f"Lead ID: {l['id']} | Name: {l['name']} | Partner: {l['partner_id']} | ContactName: {l['contact_name']} | Email: {l['email_from']} | Creado: {l['create_date']}")
