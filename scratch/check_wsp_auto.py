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

print("Verificando automatización de WhatsApp...")
automations = models.execute_kw(DB, uid, PASS, 'base.automation', 'search_read', 
    [[('name', 'ilike', 'WhatsApp: Crear Oportunidad'), '|', ('active', '=', True), ('active', '=', False)]], 
    {'fields': ['id', 'name', 'active', 'trigger', 'model_id']})

for a in automations:
    print(f"- {a['name']} | ID: {a['id']} | Activo: {a['active']}")
