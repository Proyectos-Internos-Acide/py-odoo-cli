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

partner_id = 92
lead_ids = [1842, 1843]
so_ids = [144, 143, 135, 136]

python_code = f"""
# 1. Cancelar y eliminar Órdenes de Venta
sos = env['sale.order'].browse({so_ids})
for so in sos:
    try:
        so.action_cancel()
    except Exception:
        pass
    # Eliminar líneas de orden de venta primero
    so.order_line.unlink()
    so.unlink()

# 2. Eliminar Leads / Oportunidades
leads = env['crm.lead'].browse({lead_ids})
leads.unlink()

# 3. Eliminar Mensajes vinculados
msgs = env['mail.message'].search(['|', ('partner_ids', 'in', [{partner_id}]), ('author_id', '=', {partner_id})])
msgs.unlink()

# 4. Eliminar el Contacto (res.partner)
partner = env['res.partner'].browse({partner_id})
partner.unlink()
"""

print("Creando Acción de Servidor para la eliminación limpia de todos los registros...")
action_id = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'create', [{
    'name': 'Eliminacion Total Contacto Rogeris',
    'model_id': models.execute_kw(DB, uid, PASS, 'ir.model', 'search', [[('model', '=', 'res.partner')]])[0],
    'state': 'code',
    'code': python_code,
}])

try:
    print("Ejecutando proceso de eliminación...")
    models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'run', [[action_id]])
    print("✅ Todos los registros (Contacto, Leads, Cotizaciones, Ventas y Mensajes) fueron eliminados exitosamente.")
except Exception as e:
    print(f"Error al eliminar: {e}")
finally:
    models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'unlink', [[action_id]])
    print("Limpieza de script finalizada.")
