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

print("Revisando los parámetros del sistema (ir.config_parameter) para correos...")
params = models.execute_kw(DB, uid, PASS, 'ir.config_parameter', 'search_read', 
    [[('key', 'ilike', 'mail')]], 
    {'fields': ['key', 'value']})

for p in params:
    print(f"{p['key']} = {p['value']}")

print("\nRevisando el alias del equipo de ventas (crm.team)...")
teams = models.execute_kw(DB, uid, PASS, 'crm.team', 'search_read',
    [[]],
    {'fields': ['name', 'alias_name', 'alias_domain']})
for t in teams:
    print(f"Equipo: {t['name']} | Alias: {t.get('alias_name', '')} @ {t.get('alias_domain', '')}")

