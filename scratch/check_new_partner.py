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

print("Buscando partners con el número 965718977...")
partners = models.execute_kw(DB, uid, PASS, 'res.partner', 'search_read', 
    [[('phone', 'ilike', '965718977')]], 
    {'fields': ['id', 'name', 'phone', 'create_date']})

for p in partners:
    print(f"Partner: {p['id']} | {p['name']} | {p['phone']} | Creado: {p['create_date']}")
