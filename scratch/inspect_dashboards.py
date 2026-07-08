"""
inspect_dashboards.py
Inspecciona los tableros (dashboards) en Odoo Wayki Trek (saas-19.2).
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

from odoo_cli import OdooClient

client = OdooClient()
client.connect()

SEP = "=" * 70

def section(title):
    print(f"\n{title}")
    print("-" * 50)

def safe_read(model, domain, fields, limit=100):
    try:
        return client.search_read(model, domain, fields=fields, limit=limit)
    except Exception as e:
        short = str(e).split('\n')[0]
        print(f"  ⚠️  [{model}] no disponible → {short}")
        return []

def get_fields(model):
    """Devuelve los campos disponibles de un modelo."""
    try:
        return client.execute(model, "fields_get", [], {"attributes": ["string", "type"]})
    except Exception:
        return {}

print(SEP)
print("📊  TABLEROS / DASHBOARDS — Wayki Trek Odoo (saas-19.2)")
print(SEP)

# ── 1. Grupos de tableros spreadsheet ────────────────────────────────────────
section("1. GRUPOS DE TABLEROS (spreadsheet.dashboard.group)")
groups = safe_read("spreadsheet.dashboard.group", [], ["name", "dashboard_ids"])
if groups:
    for g in groups:
        count = len(g.get("dashboard_ids", []))
        print(f"  📁 {g['name']}  ({count} tableros)  [id={g['id']}]")
else:
    print("  (ninguno)")

# ── 2. Tableros spreadsheet individuales ─────────────────────────────────────
section("2. TABLEROS SPREADSHEET (spreadsheet.dashboard)")
# Primero descubrir campos disponibles
dash_fields = get_fields("spreadsheet.dashboard")
available = [f for f in ["name", "dashboard_group_id", "access_group_ids"] if f in dash_fields]
available = available or ["name"]

dashboards = safe_read("spreadsheet.dashboard", [], available, limit=50)
if dashboards:
    print(f"  Total: {len(dashboards)}")
    for d in dashboards:
        grp = ""
        if "dashboard_group_id" in d and d["dashboard_group_id"]:
            grp = f"  [{d['dashboard_group_id'][1]}]"
        print(f"  • {d['name']}{grp}  (id={d['id']})")
else:
    print("  (ninguno)")

# ── 3. Acción cliente del módulo dashboards ───────────────────────────────────
section("3. ACCIONES CLIENTE (ir.actions.client)")
actions = safe_read("ir.actions.client", [], ["name", "tag", "res_model"], limit=200)
board_actions = [a for a in actions
                 if "board" in (a.get("tag") or "").lower()
                 or "dashboard" in (a.get("name") or "").lower()
                 or "spreadsheet" in (a.get("tag") or "").lower()]
if board_actions:
    for a in board_actions:
        print(f"  [tag: {a['tag']}]  {a['name']}")
else:
    print("  (ninguna)")

# ── 4. Módulos de dashboard instalados ───────────────────────────────────────
section("4. MÓDULOS DE DASHBOARD INSTALADOS")
modules = safe_read(
    "ir.module.module",
    [["state", "=", "installed"]],
    ["name", "shortdesc"],
    limit=300,
)
dash_mods = [m for m in modules
             if any(kw in m["name"] for kw in ["board", "dashboard", "spreadsheet", "report"])]
for m in dash_mods:
    print(f"  ✅ {m['name']:45s}  {m['shortdesc']}")

# ── 5. Resumen de datos funcionales ──────────────────────────────────────────
section("5. RESUMEN DATOS FUNCIONALES")

leads_total = safe_read("crm.lead", [["type","=","lead"],["active","=",True]], ["id"], limit=1000)
opps_total  = safe_read("crm.lead", [["type","=","opportunity"],["active","=",True]], ["id"], limit=1000)
orders_q    = safe_read("sale.order", [["state","in",["draft","sent","sale"]]], ["id","amount_total"], limit=1000)
revenue     = sum(o["amount_total"] for o in orders_q)

print(f"  CRM Leads activos:           {len(leads_total)}")
print(f"  CRM Oportunidades activas:   {len(opps_total)}")
print(f"  Pedidos de venta activos:    {len(orders_q)}")
print(f"  Revenue en pedidos activos:  S/ {revenue:,.2f}")

# Etapas CRM con conteos
section("6. OPORTUNIDADES POR ETAPA")
stages = safe_read("crm.stage", [], ["name", "sequence"], limit=20)
stages.sort(key=lambda s: s.get("sequence", 0))
for st in stages:
    opps_in_stage = safe_read(
        "crm.lead",
        [["stage_id","=",st["id"]],["type","=","opportunity"],["active","=",True]],
        ["id","expected_revenue"],
        limit=500,
    )
    rev = sum(o.get("expected_revenue", 0) for o in opps_in_stage)
    bar = "█" * min(len(opps_in_stage), 20)
    print(f"  {st['name']:30s} {len(opps_in_stage):3d} ops  {bar}  S/ {rev:,.0f}")

print(f"\n{SEP}")
print("FIN DEL REPORTE")
print(SEP)
