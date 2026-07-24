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

print("Corrigiendo la automatización de WhatsApp...")
new_code = """
if record.message_type == 'inbound':
    mobile = record.mobile_number
    if mobile:
        clean_mobile = mobile.replace('+', '')
        
        existing_partner = env['res.partner'].search([('phone', 'ilike', clean_mobile)], limit=1)
        existing_lead = env['crm.lead'].search([('phone', 'ilike', clean_mobile)], limit=1)
        
        if not existing_lead and not existing_partner:
            env['crm.lead'].create({
                'name': 'Nuevo WhatsApp: ' + str(mobile),
                'phone': mobile,
                'type': 'opportunity',
                'description': record.body,
            })
"""

action = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'search', [[('name', '=', 'Crear Lead desde WSP')]])
if action:
    models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'write', [action, {'code': new_code}])
    print("¡Automatización corregida!")

