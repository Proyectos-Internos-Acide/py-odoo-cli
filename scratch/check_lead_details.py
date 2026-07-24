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

print("Revisando los detalles de los leads 1934 y 1932...")
leads = models.execute_kw(DB, uid, PASS, 'crm.lead', 'read',
    [[1934, 1932]],
    {'fields': ['name', 'partner_id', 'contact_name', 'email_from', 'phone', 'description', 'x_wayki_sync_payload', 'create_uid']})

for l in leads:
    print("----------------------------------------")
    print(f"ID: {l['id']} | Name: {l['name']}")
    print(f"Partner: {l['partner_id']}")
    print(f"Contact Name: {l['contact_name']}")
    print(f"Email From: {l['email_from']}")
    print(f"Phone: {l['phone']}")
    print(f"Create UID: {l['create_uid']}")
    print(f"Description (first 300 chars):\n{str(l['description'])[:300]}")

print("\n" + "="*50 + "\n")
print("Buscando si hay reglas por defecto (defaults) en ir.default o crm.team o ir.config_parameter...")
defaults = models.execute_kw(DB, uid, PASS, 'ir.default', 'search_read',
    [[('field_id.model', '=', 'crm.lead')]], {'fields': ['field_id', 'user_id', 'json_value']})
print("Ir Defaults para crm.lead:", defaults)

print("\nBuscando todos los partners con email 'a' o vacíos...")
partners_a = models.execute_kw(DB, uid, PASS, 'res.partner', 'search_read',
    [[('email', '=', 'a')]], {'fields': ['id', 'name', 'email']})
print("Partners con email='a':", partners_a)
