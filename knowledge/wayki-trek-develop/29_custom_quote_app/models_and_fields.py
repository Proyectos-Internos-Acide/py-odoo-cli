from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient
from constants import *
from constants import _get_model

def _ensure_model(client: OdooClient) -> dict:
    rec = _get_model(client, WIZ_MODEL)
    if rec:
        return rec
    model_id = client.create(
        "ir.model",
        {
            "name": WIZ_MODEL_NAME,
            "model": WIZ_MODEL,
            "state": "manual",
        },
    )
    return {"id": model_id, "model": WIZ_MODEL, "name": WIZ_MODEL_NAME}

def _ensure_line_model(client: OdooClient) -> dict:
    rec = _get_model(client, WIZ_LINE_MODEL)
    if rec:
        return rec
    model_id = client.create(
        "ir.model",
        {
            "name": WIZ_LINE_MODEL_NAME,
            "model": WIZ_LINE_MODEL,
            "state": "manual",
        },
    )
    return {"id": model_id, "model": WIZ_LINE_MODEL, "name": WIZ_LINE_MODEL_NAME}

def _ensure_service_line_model(client: OdooClient) -> dict:
    rec = _get_model(client, WIZ_SERVICE_LINE_MODEL)
    if rec:
        return rec
    model_id = client.create(
        "ir.model",
        {
            "name": WIZ_SERVICE_LINE_MODEL_NAME,
            "model": WIZ_SERVICE_LINE_MODEL,
            "state": "manual",
        },
    )
    return {"id": model_id, "model": WIZ_SERVICE_LINE_MODEL, "name": WIZ_SERVICE_LINE_MODEL_NAME}

def _ensure_field(
    client: OdooClient,
    model: dict,
    name: str,
    desc: str,
    ttype: str,
    relation: str | None = None,
    relation_field: str | None = None,
) -> int:
    existing = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", model["model"]], ["name", "=", name]],
        fields=["id"],
        limit=1,
    )
    if existing:
        return existing[0]["id"]

    vals = {
        "name": name,
        "field_description": desc,
        "model_id": model["id"],
        "model": model["model"],
        "ttype": ttype,
        "state": "manual",
        "store": True,
    }
    if relation:
        vals["relation"] = relation
    if relation_field:
        vals["relation_field"] = relation_field
    return client.create("ir.model.fields", vals)

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
