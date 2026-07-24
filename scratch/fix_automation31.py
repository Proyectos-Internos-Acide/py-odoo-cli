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

print("Corrigiendo el código de la automatización 31...")
action = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'search_read',
    [[('name', '=', 'CRM: Enviar correo de confirmación al convertirse en Oportunidad')]],
    {'fields': ['id', 'name', 'code']})

if action:
    old_code = action[0].get('code')
    action_id = action[0]['id']
    
    # Agregar una verificación al principio para evitar que falle si no hay correo
    new_code = """
if not record.email_from:
    # No hay correo, no podemos enviar autorespuesta
    pass
else:
""" + "\n".join("    " + line for line in old_code.split("\n"))

    models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'write', [[action_id], {'code': new_code}])
    print("Código corregido.")
    
print("Reactivando la automatización de WhatsApp...")
automations = models.execute_kw(DB, uid, PASS, 'base.automation', 'search', [[('name', 'ilike', 'WhatsApp: Crear Oportunidad')]])
if automations:
    models.execute_kw(DB, uid, PASS, 'base.automation', 'write', [automations, {'active': True}])
    print("Automatización de WhatsApp reactivada.")
