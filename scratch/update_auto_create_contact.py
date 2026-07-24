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

print("Actualizando la automatización 'Auto-Ligar Lead por Email' para crear el contacto si no existe...")

action = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'search_read',
    [[('name', '=', 'Auto-Ligar Lead por Email')]], {'fields': ['id', 'code']})

if action:
    action_id = action[0]['id']
    new_code = """# Variables inyectadas por Odoo en su framework interno de acciones:
# 'record' = Es el nuevo registro del crm.lead que se acaba de crear.
# 'env' = El framework ORM para hacer consultas a la BD local segura.

if not record.partner_id and record.email_from:
    raw_email = record.email_from.strip().lower()

    # Validar que sea un email real
    if '@' in raw_email and len(raw_email) > 4:
        # 1. Buscar si ya existe un Contacto con este mismo correo
        partner = env['res.partner'].search([('email', '=ilike', raw_email)], limit=1)

        if partner:
            # Si ya existe, lo enlazamos al Lead
            record.write({'partner_id': partner.id})
        else:
            # 2. Si NO existe, creamos el nuevo Contacto con sus datos
            contact_name = record.contact_name or record.name or raw_email.split('@')[0]
            
            # Limpiar prefijos como [INTERNO] o [PAGO] del nombre si vienen en record.name
            if contact_name.startswith('['):
                parts = contact_name.split(']', 1)
                if len(parts) > 1:
                    contact_name = parts[1].strip()

            partner_vals = {
                'name': contact_name,
                'email': raw_email,
            }
            if record.phone:
                partner_vals['phone'] = record.phone

            new_partner = env['res.partner'].create(partner_vals)
            record.write({'partner_id': new_partner.id})
"""
    models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'write', [[action_id], {'code': new_code}])
    print("✅ Automatización actualizada con éxito. Ahora asociará o creará el contacto automáticamente.")
