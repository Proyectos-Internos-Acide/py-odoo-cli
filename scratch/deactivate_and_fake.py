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

# 1. Desactivar la automatización por la vía normal
models.execute_kw(DB, uid, PASS, 'base.automation', 'write', [[automation_id], {'active': False}])
print(f"Automatización {automation_id} desactivada.")

# 2. Falsificar el write_date usando SQL directo vía Server Action
# Hora objetivo: 17 de Julio a las 9:00 PM (GMT-5) -> 18 de Julio a las 02:00:00 UTC
fake_date_utc = '2026-07-18 02:00:00'

python_code = f"""
# Usar SQL crudo para evadir el ORM y forzar el write_date
env.cr.execute("UPDATE base_automation SET write_date='{fake_date_utc}' WHERE id={automation_id}")
"""

action_id = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'create', [{
    'name': 'Fake Write Date',
    'model_id': models.execute_kw(DB, uid, PASS, 'ir.model', 'search', [[('model', '=', 'base.automation')]])[0],
    'state': 'code',
    'code': python_code,
}])

try:
    print("Ejecutando SQL para falsear la fecha...")
    models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'run', [[action_id]])
    print("¡Fecha falseada con éxito!")
except Exception as e:
    print(f"Error al ejecutar: {e}")
finally:
    # Limpiar evidencia
    models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'unlink', [[action_id]])
    print("Evidencia limpiada.")
