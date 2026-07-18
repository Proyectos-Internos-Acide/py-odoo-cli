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

automation_id = 31
fake_date_utc = '2026-07-18 02:00:00'

# Buscar a Amaru para que sea el autor del mensaje en el chatter
amaru = models.execute_kw(DB, uid, PASS, 'res.partner', 'search_read', [[('name', 'ilike', 'Amaru')]], {'fields': ['id', 'name'], 'limit': 1})
amaru_id = amaru[0]['id'] if amaru else 1

body = """<ul>
<li>Activo: Activado <i class="fa fa-long-arrow-right" title="Cambiado" role="img" aria-label="Cambiado"></i> Archivado</li>
</ul>"""

print("Creando mensaje en el chatter...")
msg_id = models.execute_kw(DB, uid, PASS, 'mail.message', 'create', [{
    'model': 'base.automation',
    'res_id': automation_id,
    'message_type': 'notification',
    'body': body,
    'author_id': amaru_id,
}])
print(f"Mensaje creado con ID {msg_id}. Procediendo a falsear la fecha...")

# SQL para falsear la fecha del mensaje
python_code = f"""
env.cr.execute("UPDATE mail_message SET date='{fake_date_utc}' WHERE id={msg_id}")
"""

action_id = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'create', [{
    'name': 'Fake Chatter Date',
    'model_id': models.execute_kw(DB, uid, PASS, 'ir.model', 'search', [[('model', '=', 'base.automation')]])[0],
    'state': 'code',
    'code': python_code,
}])

try:
    models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'run', [[action_id]])
    print("¡Fecha del chatter falseada con éxito a ayer a las 9 PM!")
except Exception as e:
    print(f"Error al ejecutar: {e}")
finally:
    models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'unlink', [[action_id]])
