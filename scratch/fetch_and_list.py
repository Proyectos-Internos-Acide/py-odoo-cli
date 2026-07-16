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

python_code = """
servers = env['fetchmail.server'].search([('state', '=', 'done')])
for server in servers:
    try:
        server.fetch_mail()
    except Exception:
        pass
"""

action_id = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'create', [{
    'name': 'Force Fetchmail',
    'model_id': models.execute_kw(DB, uid, PASS, 'ir.model', 'search', [[('model', '=', 'fetchmail.server')]])[0],
    'state': 'code',
    'code': python_code,
}])
try:
    models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'run', [[action_id]])
except:
    pass
models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'unlink', [[action_id]])

print("Buscando correos de contactorogeris@gmail.com...")
recent_emails = models.execute_kw(DB, uid, PASS, 'mail.message', 'search_read', 
    [[('email_from', 'ilike', 'contactorogeris')]], 
    {'fields': ['id', 'subject', 'email_from', 'date', 'model', 'res_id', 'message_type'], 'limit': 5, 'order': 'id desc'})

for email in recent_emails:
    print(f"ID: {email['id']} | Fecha: {email['date']} | Asunto: {email['subject']} | Modelo: {email['model']} | ID Res: {email['res_id']} | Tipo: {email['message_type']}")

