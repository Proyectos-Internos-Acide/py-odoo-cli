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

print("Buscando módulos de WhatsApp instalados...")
modules = models.execute_kw(DB, uid, PASS, 'ir.module.module', 'search_read', 
    [[('name', 'ilike', 'whatsapp'), ('state', '=', 'installed')]], 
    {'fields': ['name', 'shortdesc']})

for m in modules:
    print(f"- {m['name']}: {m['shortdesc']}")

print("\nBuscando reglas automatizadas que creen Leads (crm.lead) a partir de WhatsApp...")
automations = models.execute_kw(DB, uid, PASS, 'base.automation', 'search_read', 
    [[]], 
    {'fields': ['id', 'name', 'model_name']})

for a in automations:
    if 'whatsapp' in str(a.get('model_name', '')).lower() or 'whatsapp' in str(a.get('name', '')).lower():
        print(f"Automatización WhatsApp encontrada: {a['name']} (Modelo: {a['model_name']})")
    elif 'discuss.channel' in str(a.get('model_name', '')):
         print(f"Automatización en Canales (posible WSP): {a['name']}")
