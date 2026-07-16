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

print("Revisando los parámetros del sistema (ir.config_parameter) para correos...")
params = models.execute_kw(DB, uid, PASS, 'ir.config_parameter', 'search_read', 
    [[('key', 'ilike', 'mail')]], 
    {'fields': ['key', 'value']})

for p in params:
    print(f"{p['key']} = {p['value']}")

print("Revisando los servidores Fetchmail para ver cómo enrutan los correos...")
fetchmail_servers = models.execute_kw(DB, uid, PASS, 'fetchmail.server', 'search_read', 
    [[]], 
    {'fields': ['id', 'name', 'user', 'server', 'state', 'object_id']})

for s in fetchmail_servers:
    # Get model name if object_id is set
    model_name = 'Ninguno'
    if s.get('object_id'):
        model_name = models.execute_kw(DB, uid, PASS, 'ir.model', 'read', [s['object_id'][0]], {'fields': ['model']})[0]['model']
    print(f"ID: {s['id']} | Usuario: {s['user']} | Modelo destino (object_id): {model_name} | Acción: {s.get('action_id')}")

print("\n3. Buscando los últimos correos descartados o ignorados en mail.message...")
# Buscar mensajes que no están en crm.lead
missing_emails = models.execute_kw(DB, uid, PASS, 'mail.message', 'search_read', 
    [[('message_type', '=', 'email'), ('model', '!=', 'crm.lead')]], 
    {'fields': ['id', 'subject', 'email_from', 'date', 'model', 'res_id'], 'order': 'id desc', 'limit': 5})

for email in missing_emails:
    print(f"ID: {email['id']} | Fecha: {email['date']} | Asunto: {email['subject']} | Modelo: {email['model']} | ID Res: {email['res_id']}")
