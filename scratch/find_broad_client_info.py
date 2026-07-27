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

emails = [
    'contactorogeris@gmail.com',
    'rogeliosanchez405@gmail.com',
    'rinfasanchez@gmail.com'
]

print("Buscando de forma amplia en Contactos (res.partner)...")
for e in emails:
    p = models.execute_kw(DB, uid, PASS, 'res.partner', 'search_read',
        [['|', '|', ('email', 'ilike', e), ('name', 'ilike', e), ('comment', 'ilike', e)]],
        {'fields': ['id', 'name', 'email', 'phone', 'create_date']})
    print(f"Búsqueda Contactos para '{e}': {len(p)} encontrados")
    for item in p:
        print(f"  -> ID: {item['id']} | Nombre: {item['name']} | Email: {item['email']} | Tel: {item['phone']}")

print("\nBuscando de forma amplia en Leads / Oportunidades (crm.lead)...")
for e in emails:
    l = models.execute_kw(DB, uid, PASS, 'crm.lead', 'search_read',
        [['|', '|', '|', ('email_from', 'ilike', e), ('name', 'ilike', e), ('contact_name', 'ilike', e), ('description', 'ilike', e)]],
        {'fields': ['id', 'name', 'stage_id', 'user_id', 'email_from', 'partner_id', 'expected_revenue', 'create_date']})
    print(f"Búsqueda Leads para '{e}': {len(l)} encontrados")
    for item in l:
        print(f"  -> Lead ID: {item['id']} | Nombre: {item['name']} | Email: {item['email_from']} | Stage: {item['stage_id']} | Partner: {item['partner_id']}")
