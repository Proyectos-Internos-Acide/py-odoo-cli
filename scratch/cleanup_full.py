"""
Limpieza total via Python:
- Elimina leads/oportunidades (con todas sus dependencias)
- Elimina contactos (excepto empresa y usuarios)
- Elimina cotizaciones y reinicia correlativo
Usa server action para ejecutar raw SQL dentro del contexto de Odoo.
"""
import sys
sys.path.insert(0, 'knowledge/wayki-trek-develop/29_custom_quote_app')
from odoo_cli import OdooClient
client = OdooClient()
client.connect()

# ─── 1. Obtener IDs de leads (activos e inactivos) ───────────────────────────
all_leads = client.search_read(
    'crm.lead',
    [('active', 'in', [True, False])],
    ['id'],
    limit=5000
)
lead_ids = [l['id'] for l in all_leads]
print(f'Total leads en BD: {len(lead_ids)}')

if not lead_ids:
    print('No hay leads que eliminar.')
else:
    # ─── 2. Crear server action que limpia dependencias + elimina via SQL ────
    # En Odoo, env.cr.execute() está disponible en server actions
    # Limpiamos en orden de dependencias para no violar FK constraints
    ids_str = ','.join(str(i) for i in lead_ids)

    cleanup_code = f"""
lead_ids_tuple = ({ids_str},)

# 1. Limpiar mail.message relacionados a leads
env.cr.execute(
    "DELETE FROM mail_message WHERE model = 'crm.lead' AND res_id IN %s",
    (lead_ids_tuple,)
)
env.cr.execute("DELETE FROM mail_message WHERE model = 'crm.lead' AND res_id IN %s", (lead_ids_tuple,))

# 2. Limpiar mail.activity relacionados a leads
env.cr.execute(
    "DELETE FROM mail_activity WHERE res_model = 'crm.lead' AND res_id IN %s",
    (lead_ids_tuple,)
)

# 3. Limpiar mail.followers relacionados a leads
env.cr.execute(
    "DELETE FROM mail_followers WHERE res_model = 'crm.lead' AND res_id IN %s",
    (lead_ids_tuple,)
)

# 4. Limpiar tabla de relacion calendar_event <-> crm_lead (si existe)
try:
    env.cr.execute(
        "DELETE FROM calendar_event_crm_lead_rel WHERE crm_lead_id IN %s",
        (lead_ids_tuple,)
    )
except Exception:
    pass  # La tabla puede no existir en esta version

# 5. Limpiar rating.rating relacionados a leads
try:
    env.cr.execute(
        "DELETE FROM rating_rating WHERE res_model = 'crm.lead' AND res_id IN %s",
        (lead_ids_tuple,)
    )
except Exception:
    pass

# 6. Finalmente eliminar los leads directamente de la tabla
env.cr.execute(
    "DELETE FROM crm_lead WHERE id IN %s",
    (lead_ids_tuple,)
)

deleted_count = env.cr.rowcount
result = f'Leads eliminados del DB: {{deleted_count}}'
"""

    # Verificar si ya existe la accion o crearla
    existing = client.search_read('ir.actions.server', [('name', '=', 'CLEANUP_LEADS_SQL')], ['id'])
    if existing:
        action_id = existing[0]['id']
        client.write('ir.actions.server', [action_id], {'code': cleanup_code.strip()})
        print(f'Server action actualizado: ID {action_id}')
    else:
        # Obtener model_id de crm.lead
        model = client.search_read('ir.model', [('model', '=', 'crm.lead')], ['id'])
        model_id = model[0]['id']
        action_id = client.execute('ir.actions.server', 'create', [{
            'name': 'CLEANUP_LEADS_SQL',
            'model_id': model_id,
            'state': 'code',
            'code': cleanup_code.strip(),
        }])
        print(f'Server action creado: ID {action_id}')

    # Ejecutar la accion
    print('Ejecutando limpieza SQL...')
    try:
        client.execute('ir.actions.server', 'run', [[action_id]])
        print('Limpieza SQL ejecutada exitosamente.')
    except Exception as e:
        print(f'Error ejecutando action: {e}')

    # Verificar
    remaining = client.search_read('crm.lead', [('active', 'in', [True, False])], ['id'], limit=5)
    print(f'Leads restantes en BD: {len(remaining)}')


# ─── 3. Limpiar contactos (excepto empresa y usuarios) ───────────────────────
print()
print('=== LIMPIANDO CONTACTOS ===')
user_partners = client.search_read('res.users', [], ['partner_id'])
user_partner_ids = [u['partner_id'][0] for u in user_partners if u['partner_id']]
company_partners = client.search_read('res.company', [], ['partner_id'])
company_partner_ids = [c['partner_id'][0] for c in company_partners if c['partner_id']]
exclude_ids = list(set(user_partner_ids + company_partner_ids + [1, 3]))
print(f'Partners protegidos (usuarios + empresa): {exclude_ids}')

partners_to_delete = client.search_read('res.partner', [
    ('id', 'not in', exclude_ids),
    ('is_company', '=', False),
    ('type', '=', 'contact'),
    ('active', 'in', [True, False]),
], ['id', 'name'], limit=500)

partner_ids = [p['id'] for p in partners_to_delete]
print(f'Contactos a eliminar: {len(partner_ids)}')
for p in partners_to_delete:
    print(f"  - {p['name']}")

if partner_ids:
    ids_str2 = ','.join(str(i) for i in partner_ids)
    partner_code = f"""
partner_ids_tuple = ({ids_str2},)

# Limpiar mail.message de estos contactos
env.cr.execute(
    "DELETE FROM mail_message WHERE model = 'res.partner' AND res_id IN %s",
    (partner_ids_tuple,)
)

# Limpiar mail.followers
env.cr.execute(
    "DELETE FROM mail_followers WHERE res_model = 'res.partner' AND res_id IN %s",
    (partner_ids_tuple,)
)

# Limpiar mail.activity
env.cr.execute(
    "DELETE FROM mail_activity WHERE res_model = 'res.partner' AND res_id IN %s",
    (partner_ids_tuple,)
)

# Eliminar los partners
env.cr.execute(
    "DELETE FROM res_partner WHERE id IN %s",
    (partner_ids_tuple,)
)
result = f'Contactos eliminados: {{env.cr.rowcount}}'
"""
    model_partner = client.search_read('ir.model', [('model', '=', 'res.partner')], ['id'])
    model_partner_id = model_partner[0]['id']

    existing_p = client.search_read('ir.actions.server', [('name', '=', 'CLEANUP_PARTNERS_SQL')], ['id'])
    if existing_p:
        action_p_id = existing_p[0]['id']
        client.write('ir.actions.server', [action_p_id], {'code': partner_code.strip()})
    else:
        action_p_id = client.execute('ir.actions.server', 'create', [{
            'name': 'CLEANUP_PARTNERS_SQL',
            'model_id': model_partner_id,
            'state': 'code',
            'code': partner_code.strip(),
        }])

    try:
        client.execute('ir.actions.server', 'run', [[action_p_id]])
        print('Contactos eliminados.')
    except Exception as e:
        print(f'Error eliminando contactos: {e}')


# ─── 4. Limpiar cotizaciones y reiniciar correlativo ─────────────────────────
print()
print('=== LIMPIANDO COTIZACIONES ===')
quotes = client.search_read('sale.order', [], ['id', 'name'], limit=500)
print(f'Cotizaciones a eliminar: {len(quotes)}')

if quotes:
    quote_ids = [q['id'] for q in quotes]
    ids_str3 = ','.join(str(i) for i in quote_ids)
    sale_code = f"""
order_ids_tuple = ({ids_str3},)

# Limpiar lineas de venta primero
env.cr.execute("DELETE FROM sale_order_line WHERE order_id IN %s", (order_ids_tuple,))

# Limpiar mensajes y actividades
env.cr.execute("DELETE FROM mail_message WHERE model = 'sale.order' AND res_id IN %s", (order_ids_tuple,))
env.cr.execute("DELETE FROM mail_followers WHERE res_model = 'sale.order' AND res_id IN %s", (order_ids_tuple,))
env.cr.execute("DELETE FROM mail_activity WHERE res_model = 'sale.order' AND res_id IN %s", (order_ids_tuple,))

# Eliminar ordenes
env.cr.execute("DELETE FROM sale_order WHERE id IN %s", (order_ids_tuple,))
result = f'Cotizaciones eliminadas: {{env.cr.rowcount}}'
"""
    model_sale = client.search_read('ir.model', [('model', '=', 'sale.order')], ['id'])
    model_sale_id = model_sale[0]['id']

    existing_s = client.search_read('ir.actions.server', [('name', '=', 'CLEANUP_SALES_SQL')], ['id'])
    if existing_s:
        action_s_id = existing_s[0]['id']
        client.write('ir.actions.server', [action_s_id], {'code': sale_code.strip()})
    else:
        action_s_id = client.execute('ir.actions.server', 'create', [{
            'name': 'CLEANUP_SALES_SQL',
            'model_id': model_sale_id,
            'state': 'code',
            'code': sale_code.strip(),
        }])

    try:
        client.execute('ir.actions.server', 'run', [[action_s_id]])
        print('Cotizaciones eliminadas.')
    except Exception as e:
        print(f'Error eliminando cotizaciones: {e}')

# ─── 5. Reiniciar correlativo de cotizaciones ─────────────────────────────────
print()
print('=== REINICIANDO CORRELATIVO ===')
seqs = client.search_read('ir.sequence', [('code', '=', 'sale.order')], ['id', 'name', 'number_next_actual'])
for s in seqs:
    client.write('ir.sequence', [s['id']], {'number_next_actual': 1})
    print(f"  Secuencia '{s['name']}': {s['number_next_actual']} -> 1")

# ─── 6. Verificacion final ────────────────────────────────────────────────────
print()
print('=== VERIFICACION FINAL ===')
leads_v = client.search_read('crm.lead', [('active', 'in', [True, False])], ['id'], limit=5)
partners_v = client.search_read('res.partner', [
    ('id', 'not in', exclude_ids),
    ('is_company', '=', False),
    ('type', '=', 'contact'),
    ('active', 'in', [True, False]),
], ['id', 'name'], limit=10)
quotes_v = client.search_read('sale.order', [], ['id'], limit=5)

print(f'  Leads/Oportunidades: {len(leads_v)}')
print(f'  Contactos extra:     {len(partners_v)}')
print(f'  Cotizaciones:        {len(quotes_v)}')
print()
print('LIMPIEZA COMPLETADA.')
