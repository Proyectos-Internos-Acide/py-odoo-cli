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

print("Buscando automatizaciones que envían correos...")
print("Verificando el código de la acción del servidor para la automatización 31...")
action = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'search_read',
    [[('name', '=', 'CRM: Enviar correo de confirmación al convertirse en Oportunidad')]],
    {'fields': ['name', 'code', 'template_id']})

if action:
    print(f"Name: {action[0]['name']}")
    print(f"Code:\n{action[0].get('code')}")
    if action[0].get('template_id'):
        print(f"Template ID: {action[0]['template_id']}")

