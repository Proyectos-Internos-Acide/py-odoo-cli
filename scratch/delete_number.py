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

target_number = '965718977'

print(f"Buscando el número {target_number} en Contactos (res.partner)...")
partners = models.execute_kw(DB, uid, PASS, 'res.partner', 'search', [[('phone', 'ilike', target_number)]])
if partners:
    models.execute_kw(DB, uid, PASS, 'res.partner', 'write', [partners, {'phone': '000000000'}])
    print(f"✅ Se eliminó el número de {len(partners)} contacto(s).")
else:
    print("No se encontraron contactos con ese número.")

print(f"Buscando el número {target_number} en Leads/Oportunidades (crm.lead)...")
leads = models.execute_kw(DB, uid, PASS, 'crm.lead', 'search', [[('phone', 'ilike', target_number)]])
if leads:
    models.execute_kw(DB, uid, PASS, 'crm.lead', 'write', [leads, {'phone': '000000000'}])
    print(f"✅ Se eliminó el número de {len(leads)} lead(s).")
else:
    print("No se encontraron leads con ese número.")
