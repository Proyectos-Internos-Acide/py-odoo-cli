"""
Usa la server action 643 (que ya funciona) como vehículo para ejecutar SQL de limpieza.
Guarda el código original, lo reemplaza con SQL, ejecuta, restaura.
"""
import sys
sys.path.insert(0, 'knowledge/wayki-trek-develop/29_custom_quote_app')
from odoo_cli import OdooClient
client = OdooClient()
client.connect()

ACTION_ID = 643  # Esta accion ya existe y funciona

# ─── Guardar código original ─────────────────────────────────────────────────
original = client.search_read('ir.actions.server', [('id', '=', ACTION_ID)], ['code', 'name'])
original_code = original[0]['code']
print(f"Accion original: '{original[0]['name']}' - código guardado ({len(original_code)} chars)")

# ─── Obtener IDs de leads (activos e inactivos) ──────────────────────────────
all_leads = client.search_read('crm.lead', [('active', 'in', [True, False])], ['id'], limit=5000)
lead_ids = [l['id'] for l in all_leads]
print(f'Leads en BD: {len(lead_ids)}')

# ─── Obtener partners a eliminar ─────────────────────────────────────────────
user_partners = client.search_read('res.users', [], ['partner_id'])
user_partner_ids = [u['partner_id'][0] for u in user_partners if u['partner_id']]
company_partners = client.search_read('res.company', [], ['partner_id'])
company_partner_ids = [c['partner_id'][0] for c in company_partners if c['partner_id']]
# Excluir también: OdooBot (3), Public user, Portal user, etc. (IDs bajos del sistema)
exclude_ids = list(set(user_partner_ids + company_partner_ids + [1, 3]))
print(f'Partners protegidos: {sorted(exclude_ids)}')

partners_to_del = client.search_read('res.partner', [
    ('id', 'not in', exclude_ids),
    ('is_company', '=', False),
    ('type', '=', 'contact'),
    ('active', 'in', [True, False]),
], ['id', 'name'], limit=500)
partner_ids = [p['id'] for p in partners_to_del]
print(f'Contactos a eliminar: {len(partner_ids)} → {[p["name"] for p in partners_to_del]}')

# ─── Obtener IDs de cotizaciones ─────────────────────────────────────────────
quotes = client.search_read('sale.order', [], ['id'], limit=500)
quote_ids = [q['id'] for q in quotes]
print(f'Cotizaciones a eliminar: {len(quote_ids)}')

# ─── Construir el SQL de limpieza ─────────────────────────────────────────────
def make_tuple(ids):
    if not ids:
        return None
    if len(ids) == 1:
        return f"({ids[0]})"
    return f"({','.join(str(i) for i in ids)})"

lead_tuple   = make_tuple(lead_ids)
partner_tuple = make_tuple(partner_ids)
quote_tuple  = make_tuple(quote_ids)

sql_parts = []

# LEADS
if lead_tuple:
    sql_parts.append(f"""
# --- LEADS ---
env.cr.execute("DELETE FROM mail_message WHERE model = 'crm.lead' AND res_id IN {lead_tuple}")
env.cr.execute("DELETE FROM mail_activity WHERE res_model = 'crm.lead' AND res_id IN {lead_tuple}")
env.cr.execute("DELETE FROM mail_followers WHERE res_model = 'crm.lead' AND res_id IN {lead_tuple}")
try:
    env.cr.execute("DELETE FROM calendar_event_crm_lead_rel WHERE crm_lead_id IN {lead_tuple}")
except Exception:
    pass
try:
    env.cr.execute("DELETE FROM rating_rating WHERE res_model = 'crm.lead' AND res_id IN {lead_tuple}")
except Exception:
    pass
env.cr.execute("DELETE FROM crm_lead WHERE id IN {lead_tuple}")
""")

# CONTACTOS
if partner_tuple:
    sql_parts.append(f"""
# --- CONTACTOS ---
env.cr.execute("DELETE FROM mail_message WHERE model = 'res.partner' AND res_id IN {partner_tuple}")
env.cr.execute("DELETE FROM mail_activity WHERE res_model = 'res.partner' AND res_id IN {partner_tuple}")
env.cr.execute("DELETE FROM mail_followers WHERE res_model = 'res.partner' AND res_id IN {partner_tuple}")
env.cr.execute("DELETE FROM res_partner WHERE id IN {partner_tuple}")
""")

# COTIZACIONES
if quote_tuple:
    sql_parts.append(f"""
# --- COTIZACIONES ---
env.cr.execute("DELETE FROM sale_order_line WHERE order_id IN {quote_tuple}")
env.cr.execute("DELETE FROM mail_message WHERE model = 'sale.order' AND res_id IN {quote_tuple}")
env.cr.execute("DELETE FROM mail_followers WHERE res_model = 'sale.order' AND res_id IN {quote_tuple}")
env.cr.execute("DELETE FROM mail_activity WHERE res_model = 'sale.order' AND res_id IN {quote_tuple}")
env.cr.execute("DELETE FROM sale_order WHERE id IN {quote_tuple}")
""")

cleanup_code = '\n'.join(sql_parts) if sql_parts else 'pass  # nada que limpiar'
print(f'\nCódigo SQL preparado ({len(cleanup_code)} chars)')

# ─── Inyectar código en acción 643 ──────────────────────────────────────────
print('Inyectando código en acción 643...')
client.write('ir.actions.server', [ACTION_ID], {'code': cleanup_code})

# ─── Ejecutar acción 643 ─────────────────────────────────────────────────────
print('Ejecutando...')
try:
    client.execute('ir.actions.server', 'run', [[ACTION_ID]])
    print('✅ SQL ejecutado exitosamente.')
except Exception as e:
    print(f'Error: {e}')

# ─── Restaurar código original ────────────────────────────────────────────────
print('Restaurando código original...')
client.write('ir.actions.server', [ACTION_ID], {'code': original_code})
print('✅ Código original restaurado.')

# ─── Reiniciar correlativo de cotizaciones ────────────────────────────────────
seqs = client.search_read('ir.sequence', [('code', '=', 'sale.order')], ['id', 'name', 'number_next_actual'])
for s in seqs:
    client.write('ir.sequence', [s['id']], {'number_next_actual': 1})
    print(f"Secuencia '{s['name']}': reseteada a 1")

# ─── Verificación final ───────────────────────────────────────────────────────
print()
print('=== VERIFICACIÓN FINAL ===')
leads_v   = client.search_read('crm.lead', [('active', 'in', [True, False])], ['id'], limit=5)
partners_v = client.search_read('res.partner', [
    ('id', 'not in', exclude_ids),
    ('is_company', '=', False),
    ('type', '=', 'contact'),
    ('active', 'in', [True, False]),
], ['id', 'name'], limit=10)
quotes_v  = client.search_read('sale.order', [], ['id'], limit=5)
seqs_v    = client.search_read('ir.sequence', [('code', '=', 'sale.order')], ['id', 'number_next_actual'])

print(f'  Leads/Oportunidades: {len(leads_v)}')
print(f'  Contactos sobrantes: {len(partners_v)} → {[p["name"] for p in partners_v]}')
print(f'  Cotizaciones:        {len(quotes_v)}')
for s in seqs_v:
    print(f"  Correlativo ventas:  {s['number_next_actual']}")
print()
print('✅ LIMPIEZA COMPLETADA.')
