from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient
from constants import WIZ_SERVICE_TEMPLATE_MODEL, _get_model

CATEGORY_MODEL = "x_wtk_service_category"
CATEGORY_MODEL_NAME = "WTK Service Category"
CATEGORY_VIEW_NAME = "wtk.service.category.form"

TYPE_MODEL = "x_wtk_service_type"
TYPE_MODEL_NAME = "WTK Service Type"
TYPE_VIEW_NAME = "wtk.service.type.form"

TEMPLATE_VIEW_NAME = "wtk.custom.service.template.form"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_simple_model(client: OdooClient, model: str, name: str) -> dict:
    rec = _get_model(client, model)
    if rec:
        return rec
    model_id = client.create("ir.model", {
        "name": name,
        "model": model,
        "state": "manual",
    })
    return {"id": model_id, "model": model, "name": name}


def _ensure_field(client, model, name, desc, ttype, relation=None):
    existing = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", model["model"]], ["name", "=", name]],
        fields=["id"], limit=1,
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
    return client.create("ir.model.fields", vals)


def _ensure_acl(client: OdooClient, model: dict) -> None:
    existing = client.search_read(
        "ir.model.access",
        domain=[["model_id", "=", model["id"]], ["group_id", "=", False]],
        fields=["id"], limit=1,
    )
    vals = {
        "name": f"access_{model['model']}_all",
        "model_id": model["id"],
        "perm_read": True,
        "perm_write": True,
        "perm_create": True,
        "perm_unlink": True,
    }
    if existing:
        client.write("ir.model.access", [existing[0]["id"]], vals)
    else:
        client.create("ir.model.access", vals)


# ---------------------------------------------------------------------------
# Form views for lookup models (shown when quick-creating)
# ---------------------------------------------------------------------------

def _upsert_simple_form_view(
    client: OdooClient,
    view_name: str,
    model: dict,
    title: str,
    placeholder: str,
) -> int:
    arch_db = f"""
<form string="{title}">
    <sheet>
        <group>
            <field name="x_name" string="{title}" placeholder="{placeholder}"/>
        </group>
    </sheet>
</form>
""".strip()
    existing = client.search_read(
        "ir.ui.view",
        domain=[["name", "=", view_name], ["model", "=", model["model"]]],
        fields=["id"], limit=1,
    )
    vals = {
        "name": view_name,
        "model": model["model"],
        "type": "form",
        "arch_db": arch_db,
        "active": True,
    }
    if existing:
        vid = existing[0]["id"]
        client.write("ir.ui.view", [vid], vals)
        return vid
    return client.create("ir.ui.view", vals)


# ---------------------------------------------------------------------------
# Service Template form view
# ---------------------------------------------------------------------------

def _upsert_template_form_view(client: OdooClient, tmpl_model: dict) -> int:
    """
    Form view for x_wtk_custom_service_template showing:
      - Categoría       (x_category_id)   — Many2one with quick create
      - Nombre          (x_raw_name)       — descriptive input
      - Tipo            (x_service_type_id)— Many2one with quick create
      - Capacidad       (x_capacity)       — integer  (N PAX)
      - Precio default  (x_price)
    x_name is hidden and auto-composed.
    """
    arch_db = """
<form string="Crear Servicio (Buscar/Crear)">
    <sheet>
        <div class="alert alert-success" role="alert" style="margin-bottom:12px;">
            <strong>🟩 Nuevo servicio para el catálogo</strong><br/>
            Se guardará como plantilla reutilizable en todas las cotizaciones
        </div>
        <group col="2">
            <field name="x_category_id"
                   string="Categoría"
                   placeholder="Ej. Transporte, Alojamiento..."
                   options="{'quick_create': True}"/>
            <field name="x_raw_name"
                   string="Nombre del servicio"
                   placeholder="Ej. Tren Vistadome ida y vuelta"/>
            <field name="x_service_type_id"
                   string="Tipo"
                   placeholder="Ej. Ejecutivo, Turista, Privado..."
                   options="{'quick_create': True}"/>
            <field name="x_capacity"
                   string="Capacidad (PAX)"
                   placeholder="Ej. 4"/>
        </group>
        <group col="1">
            <field name="x_price" string="Precio por defecto (USD)"/>
        </group>
        <field name="x_name" invisible="1"/>
    </sheet>
</form>
""".strip()
    existing = client.search_read(
        "ir.ui.view",
        domain=[["name", "=", TEMPLATE_VIEW_NAME], ["model", "=", tmpl_model["model"]]],
        fields=["id"], limit=1,
    )
    vals = {
        "name": TEMPLATE_VIEW_NAME,
        "model": tmpl_model["model"],
        "type": "form",
        "arch_db": arch_db,
        "active": True,
    }
    if existing:
        vid = existing[0]["id"]
        client.write("ir.ui.view", [vid], vals)
        return vid
    return client.create("ir.ui.view", vals)


# ---------------------------------------------------------------------------
# Name composition automation
# Format: "Categoría - Nombre del servicio - Tipo - N PAX"
# ---------------------------------------------------------------------------

def _upsert_name_compose_automation(client: OdooClient, tmpl_model: dict) -> None:
    action_name = "WTK - Componer nombre de plantilla de servicio"
    action_code = """
target_records = records or record
if target_records:
    for rec in target_records:
        parts = []
        if rec.x_category_id and rec.x_category_id.x_name:
            parts.append(rec.x_category_id.x_name)
        if rec.x_raw_name:
            parts.append(rec.x_raw_name)
        if rec.x_service_type_id and rec.x_service_type_id.x_name:
            parts.append(rec.x_service_type_id.x_name)
        cap = rec.x_capacity
        if cap and cap > 0:
            parts.append(str(int(cap)) + ' PAX')
        composed = ' - '.join(parts)
        if composed != (rec.x_name or ''):
            rec.write({'x_name': composed})
""".strip()

    action_existing = client.search_read(
        "ir.actions.server",
        domain=[["name", "=", action_name], ["model_id", "=", tmpl_model["id"]]],
        fields=["id"], limit=1,
    )
    action_vals = {
        "name": action_name,
        "model_id": tmpl_model["id"],
        "state": "code",
        "code": action_code,
    }
    if action_existing:
        action_id = action_existing[0]["id"]
        client.write("ir.actions.server", [action_id], action_vals)
    else:
        action_id = client.create("ir.actions.server", action_vals)

    # Watch all four composing fields
    field_recs = client.search_read(
        "ir.model.fields",
        domain=[
            ["model", "=", WIZ_SERVICE_TEMPLATE_MODEL],
            ["name", "in", ["x_category_id", "x_raw_name", "x_service_type_id", "x_capacity"]],
        ],
        fields=["id"], limit=10,
    )
    field_ids = [r["id"] for r in field_recs]
    if not field_ids:
        print("  ⚠ No se encontraron campos para la automatización de composición de nombre.")
        return

    automation_name = "WTK - Auto componer nombre plantilla servicio"
    automation_existing = client.search_read(
        "base.automation",
        domain=[["name", "=", automation_name], ["model_id", "=", tmpl_model["id"]]],
        fields=["id"], limit=1,
    )
    automation_vals = {
        "name": automation_name,
        "model_id": tmpl_model["id"],
        "trigger": "on_change",
        "active": True,
        "on_change_field_ids": [(6, 0, field_ids)],
        "action_server_ids": [(6, 0, [action_id])],
    }
    if automation_existing:
        client.write("base.automation", [automation_existing[0]["id"]], automation_vals)
    else:
        client.create("base.automation", automation_vals)


# ---------------------------------------------------------------------------
# Generic list view + window action + menu helper
# ---------------------------------------------------------------------------

# parent: Ventas > Productos  (sale.menu_products)
_PRODUCTS_PARENT_XMLID = ("sale", "menu_products")


def _get_sales_products_parent(client: OdooClient) -> int:
    xml_rec = client.search_read(
        "ir.model.data",
        domain=[["module", "=", _PRODUCTS_PARENT_XMLID[0]], ["name", "=", _PRODUCTS_PARENT_XMLID[1]]],
        fields=["res_id"], limit=1,
    )
    return xml_rec[0]["res_id"] if xml_rec else False


def _upsert_list_view(client: OdooClient, model: dict, view_name: str, title: str, fields_xml: str) -> int:
    arch_db = f'<list string="{title}" multi_edit="1">{fields_xml}</list>'
    existing = client.search_read(
        "ir.ui.view",
        domain=[["name", "=", view_name], ["model", "=", model["model"]]],
        fields=["id"], limit=1,
    )
    vals = {"name": view_name, "model": model["model"], "type": "list", "arch_db": arch_db, "active": True}
    if existing:
        vid = existing[0]["id"]
        client.write("ir.ui.view", [vid], vals)
        return vid
    return client.create("ir.ui.view", vals)


def _upsert_window_action(client: OdooClient, model: dict, action_name: str) -> int:
    existing = client.search_read(
        "ir.actions.act_window",
        domain=[["name", "=", action_name], ["res_model", "=", model["model"]]],
        fields=["id"], limit=1,
    )
    vals = {"name": action_name, "res_model": model["model"], "view_mode": "list,form", "target": "current", "context": "{}"}
    if existing:
        aid = existing[0]["id"]
        client.write("ir.actions.act_window", [aid], vals)
        return aid
    return client.create("ir.actions.act_window", vals)


def _upsert_menu(client: OdooClient, menu_name: str, action_id: int, parent_id: int, sequence: int) -> None:
    existing = client.search_read(
        "ir.ui.menu",
        domain=[["name", "=", menu_name]],
        fields=["id"], limit=1,
    )
    vals = {"name": menu_name, "action": f"ir.actions.act_window,{action_id}", "active": True, "sequence": sequence}
    if parent_id:
        vals["parent_id"] = parent_id
    if existing:
        client.write("ir.ui.menu", [existing[0]["id"]], vals)
        print(f"   Menú '{menu_name}' actualizado (id={existing[0]['id']}).")
    else:
        mid = client.create("ir.ui.menu", vals)
        print(f"   Menú '{menu_name}' creado (id={mid}).")


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def run(client: OdooClient) -> None:
    print("-> Configurando Categorías, Tipos y Plantillas de Servicio...")

    # Resolve parent menu once
    products_parent_id = _get_sales_products_parent(client)

    # 1. Category model
    cat_model = _ensure_simple_model(client, CATEGORY_MODEL, CATEGORY_MODEL_NAME)
    print(f"   Categoría: {cat_model['model']} (id={cat_model['id']})")
    _ensure_field(client, cat_model, "x_name", "Nombre de categoría", "char")
    _ensure_acl(client, cat_model)
    _upsert_simple_form_view(
        client, CATEGORY_VIEW_NAME, cat_model,
        title="Categoría de servicio",
        placeholder="Ej. Transporte, Alojamiento, Guía",
    )
    _upsert_list_view(
        client, cat_model, "wtk.service.category.list",
        "Categorías de servicio",
        '<field name="x_name" string="Nombre de categoría"/>',
    )
    cat_action_id = _upsert_window_action(client, cat_model, "WTK - Categorías de servicio")
    _upsert_menu(client, "Categorías de servicio", cat_action_id, products_parent_id, sequence=31)

    # 2. Type model
    type_model = _ensure_simple_model(client, TYPE_MODEL, TYPE_MODEL_NAME)
    print(f"   Tipo: {type_model['model']} (id={type_model['id']})")
    _ensure_field(client, type_model, "x_name", "Nombre de tipo", "char")
    _ensure_acl(client, type_model)
    _upsert_simple_form_view(
        client, TYPE_VIEW_NAME, type_model,
        title="Tipo de servicio",
        placeholder="Ej. Ejecutivo, Turista, Privado, Grupal",
    )
    _upsert_list_view(
        client, type_model, "wtk.service.type.list",
        "Tipos de servicio",
        '<field name="x_name" string="Nombre de tipo"/>',
    )
    type_action_id = _upsert_window_action(client, type_model, "WTK - Tipos de servicio")
    _upsert_menu(client, "Tipos de servicio", type_action_id, products_parent_id, sequence=32)

    # 3. Service template fields
    tmpl_model = _get_model(client, WIZ_SERVICE_TEMPLATE_MODEL)
    _ensure_field(client, tmpl_model, "x_category_id", "Categoría", "many2one", relation=CATEGORY_MODEL)
    _ensure_field(client, tmpl_model, "x_raw_name", "Nombre descriptivo del servicio", "char")
    _ensure_field(client, tmpl_model, "x_service_type_id", "Tipo de servicio", "many2one", relation=TYPE_MODEL)
    _ensure_field(client, tmpl_model, "x_capacity", "Capacidad (PAX)", "integer")
    print("   Campos añadidos a la plantilla de servicio.")

    # 4. Template form view (Buscar/Crear modal)
    _upsert_template_form_view(client, tmpl_model)
    print("   Vista del formulario de plantilla actualizada.")

    # 5. Template list view + action + menu (Servicios Incluidos)
    _upsert_list_view(
        client, tmpl_model, "wtk.custom.service.template.list",
        "Catálogo de servicios",
        '<field name="x_name" string="Nombre completo" readonly="1"/>'
        '<field name="x_category_id" string="Categoría"/>'
        '<field name="x_raw_name" string="Nombre del servicio"/>'
        '<field name="x_service_type_id" string="Tipo"/>'
        '<field name="x_capacity" string="Capacidad (PAX)"/>'
        '<field name="x_price" string="Precio USD"/>',
    )
    tmpl_action_id = _upsert_window_action(client, tmpl_model, "WTK - Catálogo de Servicios")
    _upsert_menu(client, "Servicios Incluidos", tmpl_action_id, products_parent_id, sequence=30)
    print("   Vistas de lista y menús configurados.")

    # 6. Automation
    _upsert_name_compose_automation(client, tmpl_model)
    print("   Automatización de composición de nombre actualizada.")

    print("✅ Listo.")


if __name__ == "__main__":
    client = OdooClient()
    client.connect()
    run(client)
