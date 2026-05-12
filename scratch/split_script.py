import ast
from pathlib import Path
import os

source_path = Path("/home/acide/py-odoo-cli/knowledge/wayki-trek-develop/29_setup_custom_quote_modal_v1.py")
dest_dir = Path("/home/acide/py-odoo-cli/knowledge/wayki-trek-develop/29_custom_quote_app")
dest_dir.mkdir(parents=True, exist_ok=True)

lines = source_path.read_text().split('\n')

def get_source(node):
    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
        return '\n'.join(lines[node.lineno-1:node.end_lineno])
    return ""

tree = ast.parse(source_path.read_text())
functions = {node.name: get_source(node) for node in tree.body if isinstance(node, ast.FunctionDef)}

imports = """from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient
from .constants import *
"""

constants = """
WIZ_MODEL = "x_wtk_custom_quote_wizard"
WIZ_MODEL_NAME = "WTK Custom Quote Wizard"
WIZ_LINE_MODEL = "x_wtk_custom_quote_wizard_line"
WIZ_LINE_MODEL_NAME = "WTK Custom Quote Wizard Line"
WIZ_SERVICE_LINE_MODEL = "x_wtk_custom_quote_wizard_service_line"
WIZ_SERVICE_LINE_MODEL_NAME = "WTK Custom Quote Wizard Service Line"
WIZ_VIEW_NAME = "wtk.custom.quote.wizard.form"
WIZ_REPORT_TEMPLATE_NAME = "wtk.report_custom_quote_document"
WIZ_REPORT_ACTION_NAME = "WTK - PDF Cotización personalizada"
WIZ_PRINT_ACTION_NAME = "WTK - Generar PDF desde wizard"
BTN_ACTION_NAME = "WTK - Abrir modal cotización personalizada"
BTN_VIEW_NAME = "wtk.sale.order.form.custom.quote.button"

def _get_model(client, model_name: str) -> dict:
    rec = client.search_read("ir.model", domain=[["model", "=", model_name]], fields=["id", "model", "name"], limit=1)
    return rec[0] if rec else {}
"""

with open(dest_dir / "constants.py", "w") as f:
    f.write(constants)

models_file = imports + "\n" + "\n\n".join([
    functions["_ensure_model"],
    functions["_ensure_line_model"],
    functions["_ensure_service_line_model"],
    functions["_ensure_field"]
]) + """

def run(client: OdooClient):
    print("-> Creando modelos y campos...")
    wizard_model = _ensure_model(client)
    wizard_line_model = _ensure_line_model(client)
    wizard_service_line_model = _ensure_service_line_model(client)
    _ensure_field(client, wizard_model, "x_sale_order_id", "Cotización origen", "many2one", relation="sale.order")
    _ensure_field(client, wizard_model, "x_passenger_qty", "Cantidad de pasajeros", "integer")
    _ensure_field(client, wizard_model, "x_operational_cost_pax", "Costo operativo por PAX", "float")
    _ensure_field(client, wizard_model, "x_fixed_cost", "Costo fijo / gastos administrativos", "float")
    _ensure_field(client, wizard_model, "x_variable_cost", "Costo variable / otros gastos", "float")
    _ensure_field(client, wizard_model, "x_total_cost", "Total costos", "float")
    _ensure_field(client, wizard_model, "x_profit_pct", "Utilidad (%)", "float")
    _ensure_field(client, wizard_model, "x_profit_amount", "Utilidad (USD)", "float")
    _ensure_field(client, wizard_model, "x_subtotal_amount", "Subtotal (USD)", "float")
    _ensure_field(client, wizard_model, "x_apply_igv", "Aplicar IGV", "boolean")
    _ensure_field(client, wizard_model, "x_igv_pct", "IGV (%)", "float")
    _ensure_field(client, wizard_model, "x_apply_renta", "Aplicar Renta", "boolean")
    _ensure_field(client, wizard_model, "x_renta_pct", "Renta (%)", "float")
    _ensure_field(client, wizard_model, "x_tax_amount", "Monto impuesto (USD)", "float")
    _ensure_field(client, wizard_model, "x_subtotal_after_tax", "Subtotal acumulado (USD)", "float")
    _ensure_field(client, wizard_model, "x_card_commission_pct", "Comisión tarjetas (%)", "float")
    _ensure_field(client, wizard_model, "x_card_commission_amount", "Comisión tarjetas (USD)", "float")
    _ensure_field(client, wizard_model, "x_final_price", "Precio final (USD)", "float")

    _ensure_field(client, wizard_line_model, "x_wizard_id", "Wizard", "many2one", relation=WIZ_MODEL)
    _ensure_field(client, wizard_line_model, "x_passenger_qty", "Cantidad pasajeros (snapshot)", "integer")
    _ensure_field(client, wizard_line_model, "x_service_date", "Fecha", "date")
    _ensure_field(client, wizard_line_model, "x_product_id", "Producto", "many2one", relation="product.product")
    _ensure_field(client, wizard_line_model, "x_qty", "Cantidad", "integer")
    _ensure_field(client, wizard_line_model, "x_unit_price", "Precio unitario", "float")
    
    _ensure_field(client, wizard_service_line_model, "x_line_id", "Línea de cotización", "many2one", relation=WIZ_LINE_MODEL)
    _ensure_field(client, wizard_service_line_model, "x_name", "Servicio incluido", "char")
    _ensure_field(client, wizard_service_line_model, "x_is_group", "¿Grupal?", "boolean")
    _ensure_field(client, wizard_service_line_model, "x_price", "Precio", "float")
    _ensure_field(client, wizard_service_line_model, "x_price_pax", "PRECIO PAX", "float")
    
    _ensure_field(client, wizard_line_model, "x_service_line_ids", "Servicios incluidos", "one2many", relation=WIZ_SERVICE_LINE_MODEL, relation_field="x_line_id")
    _ensure_field(client, wizard_model, "x_line_ids", "Líneas custom", "one2many", relation=WIZ_LINE_MODEL, relation_field="x_wizard_id")

    for model_name in [WIZ_MODEL, WIZ_LINE_MODEL, WIZ_SERVICE_LINE_MODEL]:
        m = _get_model(client, model_name)
        existing_acl = client.execute("ir.model.access", "search_read", [["model_id", "=", m["id"]], ["group_id", "=", False]], fields=["id"], limit=1, context={"active_test": False})
        vals_acl = {"name": f"access_{model_name}_all", "model_id": m["id"], "perm_read": True, "perm_write": True, "perm_create": True, "perm_unlink": True}
        if existing_acl: client.write("ir.model.access", [existing_acl[0]["id"]], vals_acl)
        else: client.create("ir.model.access", vals_acl)
    return wizard_model, wizard_line_model, wizard_service_line_model

if __name__ == "__main__":
    client = OdooClient()
    client.connect()
    run(client)
"""
with open(dest_dir / "models_and_fields.py", "w") as f: f.write(models_file)

logic_file = imports + "\n" + "\n\n".join([
    functions["_upsert_service_price_pax_onchange"],
    functions["_upsert_wizard_passenger_qty_sync"],
    functions["_upsert_wizard_cost_totals_automation"],
    functions["_upsert_tax_exclusive_automations"]
]) + """

def run(client: OdooClient, wizard_model: dict, wizard_service_line_model: dict):
    print("-> Configurando lógica y automatizaciones...")
    _upsert_wizard_passenger_qty_sync(client, wizard_model)
    _upsert_service_price_pax_onchange(client, wizard_service_line_model)
    _upsert_wizard_cost_totals_automation(client, wizard_model, wizard_service_line_model)
    _upsert_tax_exclusive_automations(client, wizard_model)

if __name__ == "__main__":
    client = OdooClient()
    client.connect()
    wizard_model = _get_model(client, WIZ_MODEL)
    wizard_service_line_model = _get_model(client, WIZ_SERVICE_LINE_MODEL)
    run(client, wizard_model, wizard_service_line_model)
"""
with open(dest_dir / "logic_and_automations.py", "w") as f: f.write(logic_file)

views_file = imports + "\n" + "\n\n".join([
    functions["_upsert_wizard_view"],
    functions["_upsert_sale_button_action"],
    functions["_upsert_sale_form_button_view"]
]) + """

def run(client: OdooClient, wizard_model: dict, print_action_id: int):
    print("-> Configurando vistas y botones...")
    wizard_view_id = _upsert_wizard_view(client, wizard_model, print_action_id)
    sale_order_model = _get_model(client, "sale.order")
    sale_action_id = _upsert_sale_button_action(client, sale_order_model, wizard_model, wizard_view_id)
    sale_view_id = _upsert_sale_form_button_view(client, sale_action_id)
    return wizard_view_id, sale_action_id, sale_view_id

if __name__ == "__main__":
    client = OdooClient()
    client.connect()
    wizard_model = _get_model(client, WIZ_MODEL)
    print_action_id = client.search_read("ir.actions.server", [["name", "=", WIZ_PRINT_ACTION_NAME], ["model_id", "=", wizard_model["id"]]], fields=["id"], limit=1)[0]["id"]
    run(client, wizard_model, print_action_id)
"""
with open(dest_dir / "views.py", "w") as f: f.write(views_file)

reports_file = imports + "\n" + "\n\n".join([
    functions["_upsert_wizard_report_template"],
    functions["_upsert_report_action"],
    functions["_upsert_wizard_print_action"]
]) + """

def run(client: OdooClient, wizard_model: dict):
    print("-> Configurando reportes (QWeb y Acciones PDF)...")
    _upsert_wizard_report_template(client)
    _upsert_report_action(client, wizard_model)
    print_action_id = _upsert_wizard_print_action(client, wizard_model, WIZ_REPORT_ACTION_NAME)
    return print_action_id

if __name__ == "__main__":
    client = OdooClient()
    client.connect()
    wizard_model = _get_model(client, WIZ_MODEL)
    run(client, wizard_model)
"""
with open(dest_dir / "reports.py", "w") as f: f.write(reports_file)

with open(dest_dir / "__init__.py", "w") as f: f.write("")

run_all = """#!/usr/bin/env python3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient
from models_and_fields import run as run_models
from logic_and_automations import run as run_logic
from reports import run as run_reports
from views import run as run_views

def main():
    print("Configurando modal de cotización personalizada (V3) - MODULAR...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")
    
    wizard_model, wizard_line_model, wizard_service_line_model = run_models(client)
    run_logic(client, wizard_model, wizard_service_line_model)
    print_action_id = run_reports(client, wizard_model)
    run_views(client, wizard_model, print_action_id)
    
    print("🎉 V3 Modular lista.")

if __name__ == "__main__":
    main()
"""
with open(dest_dir / "run_all.py", "w") as f: f.write(run_all)
os.chmod(dest_dir / "run_all.py", 0o755)

print("Modularization complete!")
