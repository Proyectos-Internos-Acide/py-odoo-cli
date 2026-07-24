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

print("Inspeccionando acciones de servidor relacionadas con Leads / JSON / Contactos...")
actions = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'search_read',
    [[('state', '=', 'code')]],
    {'fields': ['id', 'name', 'code']})

for a in actions:
    code = a.get('code', '')
    if 'Chris' in code or 'Schott' in code or 'partner' in code or 'JSON' in code or 'crm.lead' in code:
        print(f"=== Accion ID: {a['id']} | Name: {a['name']} ===")
        print(code[:2000])
        print("="*40)
