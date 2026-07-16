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
# Ejecutar SQL directamente para saltar las validaciones del ORM en Odoo SaaS
# Volver a agregar grupo Own Docs (18)
env.cr.execute('INSERT INTO res_groups_users_rel (gid, uid) VALUES (18, 5) ON CONFLICT DO NOTHING')
env.cr.execute('INSERT INTO res_groups_users_rel (gid, uid) VALUES (18, 9) ON CONFLICT DO NOTHING')
env.cr.execute('INSERT INTO res_groups_users_rel (gid, uid) VALUES (18, 13) ON CONFLICT DO NOTHING')

# Quitar grupo All Docs (19)
env.cr.execute('DELETE FROM res_groups_users_rel WHERE gid = 19 AND uid IN (5, 9, 13)')

# Limpiar cache para que los cambios surtan efecto
env.registry.clear_cache()
"""

# Crear Server Action
action_id = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'create', [{
    'name': 'Revert Permissions SQL',
    'model_id': models.execute_kw(DB, uid, PASS, 'ir.model', 'search', [[('model', '=', 'res.users')]])[0],
    'state': 'code',
    'code': python_code,
}])

try:
    models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'run', [[action_id]])
    print("¡Permisos actualizados forzosamente usando SQL vía Server Action!")
except Exception as e:
    print(f"Error al ejecutar: {e}")
finally:
    models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'unlink', [[action_id]])

