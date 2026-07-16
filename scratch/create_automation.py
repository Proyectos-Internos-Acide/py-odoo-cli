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

# 1. Verificar si 'base.automation' está instalado
modules = models.execute_kw(DB, uid, PASS, 'ir.module.module', 'search_read', 
    [[('name', '=', 'base_automation')]], 
    {'fields': ['state']})

if modules and modules[0]['state'] == 'installed':
    print("El módulo 'base_automation' está instalado. Procediendo a crear la regla...")
    
    # 2. Buscar ID del modelo mail.message
    model_id = models.execute_kw(DB, uid, PASS, 'ir.model', 'search', [[('model', '=', 'mail.message')]])[0]
    
    # Código Python a ejecutar
    python_code = """
if record.model == 'crm.lead' and record.res_id and record.message_type == 'email':
    lead = env['crm.lead'].browse(record.res_id)
    if lead.user_id and lead.user_id.partner_id and record.author_id.id != lead.user_id.partner_id.id:
        sender = record.email_from or 'Cliente'
        subject = record.subject or 'Sin asunto'
        # Un mensaje limpio y directo
        body = f"🔔 @{lead.user_id.name} | De: {sender} <br/> Asunto: {subject}"
        lead.message_post(
            body=body,
            message_type='comment',
            subtype_xmlid='mail.mt_note',
            partner_ids=[lead.user_id.partner_id.id]
        )
"""
    
    existing = models.execute_kw(DB, uid, PASS, 'base.automation', 'search', [[('name', '=', 'Notificar Vendedor Correo CRM')]])
    if existing:
        automation_id = existing[0]
        # Update action server linked to it
        action_server = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'search', [[('base_automation_id', '=', automation_id)]])
        if action_server:
            models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'write', [[action_server[0]], {'code': python_code}])
            print(f"Automatización ID {automation_id} actualizada.")
    else:
        # 3. Crear base.automation
        automation_id = models.execute_kw(DB, uid, PASS, 'base.automation', 'create', [{
            'name': 'Notificar Vendedor Correo CRM',
            'model_id': model_id,
            'trigger': 'on_create',
            'filter_domain': "[('message_type', '=', 'email'), ('model', '=', 'crm.lead')]",
            'active': True
        }])
        
        # 4. Crear ir.actions.server
        action_id = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'create', [{
            'name': 'Server Action - Notificar Vendedor',
            'model_id': model_id,
            'state': 'code',
            'code': python_code,
            'base_automation_id': automation_id
        }])
        
        print(f"¡Acción Automatizada creada con éxito! Automation ID: {automation_id} | Server Action ID: {action_id}")

