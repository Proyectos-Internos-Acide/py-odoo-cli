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

print("1. Limpiando el email de Chris Schott (ID 106)...")
models.execute_kw(DB, uid, PASS, 'res.partner', 'write', [[106], {'email': False}])
print("✅ Email de Chris Schott reseteado a vacío.")

print("\n2. Mejorando el código de la automatización 'Auto-Ligar Lead por Email'...")
action = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'search_read',
    [[('name', '=', 'Auto-Ligar Lead por Email')]], {'fields': ['id', 'code']})

if action:
    action_id = action[0]['id']
    new_code = """# Variables inyectadas por Odoo en su framework interno de acciones:
# 'record' = Es el nuevo registro del crm.lead que se acaba de crear.
# 'env' = El framework ORM para hacer consultas a la BD local segura.

# Evitar colisiones: Solo aplica si el Lead NO tiene un contacto ya enlazado
# y SÍ tiene un email escrito con un formato mínimo válido (debe contener '@' y más de 4 caracteres)
if not record.partner_id and record.email_from:
    raw_email = record.email_from.strip().lower()

    if '@' in raw_email and len(raw_email) > 4:
        # Buscar si ya existe un Contacto con ese mismo correo válido en la BD
        partner = env['res.partner'].search([('email', '=ilike', raw_email)], limit=1)

        if partner:
            # Lo encontramos! Actualizamos la referencia directamente
            record.write({'partner_id': partner.id})
"""
    models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'write', [[action_id], {'code': new_code}])
    print("✅ Código de la acción de servidor mejorado con validación de correo real (@).")

