import sys
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

print("--- SERVER ACTION 584 ---")
sa584 = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'read', [[584]], {'fields': ['name', 'model_id', 'code']})
print(sa584[0]['name'])
print(sa584[0]['code'])

print("\n--- SERVER ACTION 651 ---")
sa651 = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'read', [[651]], {'fields': ['name', 'model_id', 'code']})
print(sa651[0]['name'])
print(sa651[0]['code'])
