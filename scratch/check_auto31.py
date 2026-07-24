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

print("Verificando el estado de la automatización 31...")
auto = models.execute_kw(DB, uid, PASS, 'base.automation', 'search_read',
    [[('id', '=', 31), '|', ('active', '=', True), ('active', '=', False)]],
    {'fields': ['name', 'active']})

print(f"Estado en BD: {auto}")
