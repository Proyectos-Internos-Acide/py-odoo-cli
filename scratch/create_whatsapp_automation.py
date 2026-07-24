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

print("Creando la Acción del Servidor...")
python_code = """
if record.message_type == 'inbound':
    mobile = record.mobile_number
    if mobile:
        # Extraer el número sin el + para búsquedas flexibles
        clean_mobile = mobile.replace('+', '')
        
        # Buscar si ya existe un lead o un cliente con este número
        existing_partner = env['res.partner'].search(['|', ('phone', 'ilike', clean_mobile), ('mobile', 'ilike', clean_mobile)], limit=1)
        existing_lead = env['crm.lead'].search(['|', ('phone', 'ilike', clean_mobile), ('mobile', 'ilike', clean_mobile)], limit=1)
        
        # Si NO hay lead existente y NO hay cliente registrado con ese número
        if not existing_lead and not existing_partner:
            env['crm.lead'].create({
                'name': 'Nuevo WhatsApp: ' + str(mobile),
                'phone': mobile,
                'type': 'opportunity',
                'description': record.body,
            })
"""

# Obtener model_id de whatsapp.message
wa_model = models.execute_kw(DB, uid, PASS, 'ir.model', 'search', [[('model', '=', 'whatsapp.message')]])
if not wa_model:
    print("El modelo whatsapp.message no existe.")
    exit()

wa_model_id = wa_model[0]

# Crear la regla de automatización
print("Creando regla en base.automation...")
automation_id = models.execute_kw(DB, uid, PASS, 'base.automation', 'create', [{
    'name': 'WhatsApp: Crear Oportunidad por Número Nuevo',
    'model_id': wa_model_id,
    'trigger': 'on_create',
    'filter_pre_domain': "[]",
    'filter_domain': "[('message_type', '=', 'inbound')]",
}])

print("Creando Acción de Servidor (Código Python)...")
action_id = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'create', [{
    'name': 'Crear Lead desde WSP',
    'model_id': wa_model_id,
    'state': 'code',
    'code': python_code,
}])

print("Vinculando acción al trigger...")
models.execute_kw(DB, uid, PASS, 'base.automation', 'write', [[automation_id], {
    'action_server_ids': [(4, action_id)]
}])

print("¡Automatización creada y vinculada con éxito!")
