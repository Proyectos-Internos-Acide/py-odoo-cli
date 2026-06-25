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
# Template list view (for the management menu)
# ---------------------------------------------------------------------------

TEMPLATE_LIST_VIEW_NAME = "wtk.custom.service.template.list"
TEMPLATE_ACTION_NAME = "WTK - Catálogo de Servicios"
TEMPLATE_MENU_NAME = "Catálogo de Servicios"


def _upsert_template_list_view(client: OdooClient, tmpl_model: dict) -> int:
    arch_db = """
<list string="Catálogo de servicios" multi_edit="1">
    <field name="x_name" string="Nombre completo" readonly="1"/>
    <field name="x_category_id" string="Categoría"/>
    <field name="x_raw_name" string="Nombre del servicio"/>
    <field name="x_service_type_id" string="Tipo"/>
    <field name="x_capacity" string="Capacidad (PAX)"/>
    <field name="x_price" string="Precio USD"/>
</list>
""".strip()
    existing = client.search_read(
        "ir.ui.view",
        domain=[["name", "=", TEMPLATE_LIST_VIEW_NAME], ["model", "=", tmpl_model["model"]]],
        fields=["id"], limit=1,
    )
    vals = {
        "name": TEMPLATE_LIST_VIEW_NAME,
        "model": tmpl_model["model"],
        "type": "list",
        "arch_db": arch_db,
        "active": True,
    }
    if existing:
        vid = existing[0]["id"]
        client.write("ir.ui.view", [vid], vals)
        return vid
    return client.create("ir.ui.view", vals)


def _upsert_template_window_action(client: OdooClient, tmpl_model: dict) -> int:
    existing = client.search_read(
        "ir.actions.act_window",
        domain=[["name", "=", TEMPLATE_ACTION_NAME], ["res_model", "=", tmpl_model["model"]]],
        fields=["id"], limit=1,
    )
    vals = {
        "name": TEMPLATE_ACTION_NAME,
        "res_model": tmpl_model["model"],
        "view_mode": "list,form",
        "target": "current",
        "context": "{}",
    }
    if existing:
        aid = existing[0]["id"]
        client.write("ir.actions.act_window", [aid], vals)
        return aid
    return client.create("ir.actions.act_window", vals)


def _upsert_template_menu(client: OdooClient, action_id: int) -> None:
    # Resolve the parent menu via XML ID (stable across reinstalls)
    xml_rec = client.search_read(
        "ir.model.data",
        domain=[["module", "=", TEMPLATE_MENU_PARENT_XMLID[0]], ["name", "=", TEMPLATE_MENU_PARENT_XMLID[1]]],
        fields=["res_id"], limit=1,
    )
    parent_id = xml_rec[0]["res_id"] if xml_rec else False

    existing = client.search_read(
        "ir.ui.menu",
        domain=[["name", "=", TEMPLATE_MENU_NAME]],
        fields=["id"], limit=1,
    )
    vals = {
        "name": TEMPLATE_MENU_NAME,
        "action": f"ir.actions.act_window,{action_id}",
        "active": True,
        "sequence": 30,
    }
    if parent_id:
        vals["parent_id"] = parent_id
    if existing:
        client.write("ir.ui.menu", [existing[0]["id"]], vals)
        print(f"   Menú '{TEMPLATE_MENU_NAME}' actualizado (id={existing[0]['id']}).")
    else:
        mid = client.create("ir.ui.menu", vals)
        print(f"   Menú '{TEMPLATE_MENU_NAME}' creado (id={mid}).")


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def run(client: OdooClient) -> None:
    print("-> Configurando Categorías, Tipos y Plantillas de Servicio...")

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

    # 5. Template list view + action + menu
    _upsert_template_list_view(client, tmpl_model)
    action_id = _upsert_template_window_action(client, tmpl_model)
    _upsert_template_menu(client, action_id)
    print("   Vista de lista y menú de gestión configurados.")

    # 6. Automation
    _upsert_name_compose_automation(client, tmpl_model)
    print("   Automatización de composición de nombre actualizada.")

    print("✅ Listo.")


if __name__ == "__main__":
    client = OdooClient()
    client.connect()
    run(client)
