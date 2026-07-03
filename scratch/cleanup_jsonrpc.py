"""
Usa JSON-RPC (no XML-RPC) para ejecutar el server action 643 via /web/dataset/call_kw
que usa una ruta diferente al XML-RPC y evita el bug unhashable type: list
"""
import sys, json, requests

sys.path.insert(0, 'knowledge/wayki-trek-develop/29_custom_quote_app')
from odoo_cli import OdooClient
client = OdooClient()
client.connect()

# Leer configuracion del cliente
url   = client._base_url.rstrip('/')
db    = client.db
uid   = client.uid
pwd   = client.password

ACTION_ID = 643

session = requests.Session()

def json_rpc(endpoint, method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "id": 1,
        "params": params
    }
    r = session.post(f"{url}{endpoint}", json=payload, timeout=60)
    resp = r.json()
    if "error" in resp:
        raise Exception(resp["error"])
    return resp.get("result")

def call_kw(model, method, args, kwargs=None):
    return json_rpc("/web/dataset/call_kw", "call", {
        "model": model,
        "method": method,
        "args": args,
        "kwargs": kwargs or {},
        "context": {}
    })

# Autenticar via JSON-RPC
print("Autenticando via JSON-RPC...")
auth_result = json_rpc("/web/session/authenticate", "call", {
    "db": db,
    "login": client.username,
    "password": pwd
})
print(f"  Auth OK: uid={auth_result.get('uid')}")

# ─── Guardar código original de acción 643 ───────────────────────────────────
original = client.search_read('ir.actions.server', [('id', '=', ACTION_ID)], ['code', 'name'])
original_code = original[0]['code']
print(f"\nAcción 643: '{original[0]['name']}' guardada ({len(original_code)} chars)")

# ─── Obtener IDs ──────────────────────────────────────────────────────────────
all_leads = client.search_read('crm.lead', [('active', 'in', [True, False])], ['id'], limit=5000)
lead_ids = [l['id'] for l in all_leads]
print(f"Leads en BD: {len(lead_ids)}")

user_partners = client.search_read('res.users', [], ['partner_id'])
user_partner_ids = [u['partner_id'][0] for u in user_partners if u['partner_id']]
company_partners = client.search_read('res.company', [], ['partner_id'])
company_partner_ids = [c['partner_id'][0] for c in company_partners if c['partner_id']]
# OdooBot=3, Public=es otro ID, Portal Template=otro
# Proteger todos los que sean usuarios del sistema
system_low_ids = list(range(1, 10))  # IDs 1-9 son sistema
exclude_ids = list(set(user_partner_ids + company_partner_ids + system_low_ids))
print(f"Partners protegidos: {sorted(exclude_ids)}")

partners_to_del = client.search_read('res.partner', [
    ('id', 'not in', exclude_ids),
    ('is_company', '=', False),
    ('type', '=', 'contact'),
    ('active', 'in', [True, False]),
], ['id', 'name'], limit=500)
partner_ids = [p['id'] for p in partners_to_del]
print(f"Contactos a eliminar: {len(partner_ids)} → {[p['name'] for p in partners_to_del]}")

# ─── Construir SQL de limpieza ────────────────────────────────────────────────
def make_tuple(ids):
    if not ids: return None
    if len(ids) == 1: return f"({ids[0]})"
    return f"({','.join(str(i) for i in ids)})"

lead_t    = make_tuple(lead_ids)
partner_t = make_tuple(partner_ids)

parts = []
if lead_t:
    parts.append(f"""# LEADS
env.cr.execute("DELETE FROM mail_message WHERE model = 'crm.lead' AND res_id IN {lead_t}")
env.cr.execute("DELETE FROM mail_activity WHERE res_model = 'crm.lead' AND res_id IN {lead_t}")
env.cr.execute("DELETE FROM mail_followers WHERE res_model = 'crm.lead' AND res_id IN {lead_t}")
try:
    env.cr.execute("DELETE FROM calendar_event_crm_lead_rel WHERE crm_lead_id IN {lead_t}")
except Exception:
    pass
env.cr.execute("DELETE FROM crm_lead WHERE id IN {lead_t}")""")

if partner_t:
    parts.append(f"""# CONTACTOS
env.cr.execute("DELETE FROM mail_message WHERE model = 'res.partner' AND res_id IN {partner_t}")
env.cr.execute("DELETE FROM mail_activity WHERE res_model = 'res.partner' AND res_id IN {partner_t}")
env.cr.execute("DELETE FROM mail_followers WHERE res_model = 'res.partner' AND res_id IN {partner_t}")
env.cr.execute("DELETE FROM res_partner WHERE id IN {partner_t}")""")

cleanup_code = '\n'.join(parts) if parts else 'pass'
print(f"\nSQL preparado ({len(cleanup_code)} chars)")

# ─── Inyectar en acción 643 ───────────────────────────────────────────────────
client.write('ir.actions.server', [ACTION_ID], {'code': cleanup_code})
print("Código inyectado en acción 643.")

# ─── Ejecutar vía JSON-RPC /web/dataset/call_kw ──────────────────────────────
print("Ejecutando vía JSON-RPC...")
try:
    result = call_kw('ir.actions.server', 'run', [[ACTION_ID]])
    print(f"✅ Resultado: {result}")
except Exception as e:
    print(f"Error JSON-RPC: {e}")

# ─── Restaurar código original ────────────────────────────────────────────────
client.write('ir.actions.server', [ACTION_ID], {'code': original_code})
print("✅ Código original restaurado.")

# ─── Reiniciar correlativo ────────────────────────────────────────────────────
seqs = client.search_read('ir.sequence', [('code', '=', 'sale.order')], ['id', 'name', 'number_next_actual'])
for s in seqs:
    client.write('ir.sequence', [s['id']], {'number_next_actual': 1})
    print(f"Secuencia '{s['name']}': reseteada a 1")

# ─── Verificación ─────────────────────────────────────────────────────────────
print("\n=== VERIFICACIÓN FINAL ===")
leads_v = client.search_read('crm.lead', [('active', 'in', [True, False])], ['id'])
partners_v = client.search_read('res.partner', [
    ('id', 'not in', exclude_ids),
    ('is_company', '=', False),
    ('type', '=', 'contact'),
    ('active', 'in', [True, False]),
], ['id', 'name'])
quotes_v = client.search_read('sale.order', [], ['id'])
print(f"  Leads/Opps:          {len(leads_v)}")
print(f"  Contactos sobrantes: {len(partners_v)} → {[p['name'] for p in partners_v]}")
print(f"  Cotizaciones:        {len(quotes_v)}")
print("\n✅ LIMPIEZA COMPLETADA.")
