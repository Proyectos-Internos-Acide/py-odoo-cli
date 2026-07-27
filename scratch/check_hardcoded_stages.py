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

print("1. Obteniendo todas las Etapas (Columnas) actuales del CRM...")
stages = models.execute_kw(DB, uid, PASS, 'crm.stage', 'search_read', [[]], {'fields': ['id', 'name', 'sequence', 'is_won']})
print("Etapas del CRM en la BD:")
for s in stages:
    print(f"  - ID: {s['id']} | Nombre: '{s['name']}' | Secuencia: {s['sequence']} | Es Ganado: {s['is_won']}")

print("\n" + "="*50 + "\n")
print("2. Analizando el código de las Acciones del Servidor en busca de nombres o IDs de Etapas hardcoded...")

actions = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'search_read',
    [[('state', '=', 'code')]],
    {'fields': ['id', 'name', 'code']})

for a in actions:
    code = a.get('code', '')
    if 'stage' in code or 'stage_id' in code:
        print(f"\n📌 Acción ID: {a['id']} | Nombre: '{a['name']}'")
        for line in code.split('\n'):
            if 'stage' in line or 'stage_id' in line or 'Nuevo Lead' in line or 'Confirmado' in line or 'Seguimiento' in line:
                print(f"   👉 {line.strip()}")
