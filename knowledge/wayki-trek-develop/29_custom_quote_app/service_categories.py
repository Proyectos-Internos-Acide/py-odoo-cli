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
TEMPLATE_VIEW_NAME = "wtk.custom.service.template.form"


def _ensure_category_model(client: OdooClient) -> dict:
    rec = _get_model(client, CATEGORY_MODEL)
    if rec:
        return rec
    model_id = client.create("ir.model", {
        "name": CATEGORY_MODEL_NAME,
        "model": CATEGORY_MODEL,
        "state": "manual",
    })
    return {"id": model_id, "model": CATEGORY_MODEL, "name": CATEGORY_MODEL_NAME}


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


def _upsert_category_form_view(client: OdooClient, cat_model: dict) -> int:
    arch_db = """
<form string="Categoría de servicio">
    <sheet>
        <group>
            <field name="x_name" string="Nombre de categoría" placeholder="Ej. Transporte, Alojamiento, Guía"/>
        </group>
    </sheet>
</form>
""".strip()
    existing = client.search_read(
        "ir.ui.view",
        domain=[["name", "=", CATEGORY_VIEW_NAME], ["model", "=", cat_model["model"]]],
        fields=["id"], limit=1,
    )
    vals = {
        "name": CATEGORY_VIEW_NAME,
        "model": cat_model["model"],
        "type": "form",
        "arch_db": arch_db,
        "active": True,
    }
    if existing:
        vid = existing[0]["id"]
        client.write("ir.ui.view", [vid], vals)
        return vid
    return client.create("ir.ui.view", vals)


def _upsert_template_form_view(client: OdooClient, tmpl_model: dict) -> int:
    """
    Overrides the form view of x_wtk_custom_service_template to show:
      - Categoría (x_category_id) — Many2one with quick create
      - Nombre del servicio (x_raw_name) — descriptive input
      - Precio por defecto (x_price)
    The x_name field is hidden (composed automatically).
    """
    arch_db = f"""
<form string="Crear Servicio (Buscar/Crear)">
    <sheet>
        <div class="alert alert-success" role="alert" style="margin-bottom:12px;">
            <strong>🟩 Nuevo servicio para el catálogo</strong><br/>
            Se guardará como plantilla reutilizable en todas las cotizaciones
        </div>
        <group>
            <field name="x_category_id"
                   string="Categoría"
                   placeholder="Ej. Transporte, Alojamiento..."
                   options="{{'create_name_field': 'x_name', 'quick_create': True}}"/>
            <field name="x_raw_name"
                   string="Nombre del servicio"
                   placeholder="Ej. Tren Vistadome ida y vuelta"/>
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


def _upsert_name_compose_automation(client: OdooClient, tmpl_model: dict) -> None:
    """
    When x_category_id or x_raw_name changes on the service template,
    auto-compose x_name = "Category - raw_name".
    """
    action_name = "WTK - Componer nombre de plantilla de servicio"
    action_code = """
target_records = records or record
if target_records:
    for rec in target_records:
        cat_name = rec.x_category_id.x_name if rec.x_category_id else ''
        raw = rec.x_raw_name or ''
        if cat_name and raw:
            composed = cat_name + ' - ' + raw
        elif cat_name:
            composed = cat_name
        else:
            composed = raw
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

    field_recs = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", WIZ_SERVICE_TEMPLATE_MODEL], ["name", "in", ["x_category_id", "x_raw_name"]]],
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


def run(client: OdooClient) -> None:
    print("-> Configurando Categorías de Servicio y Plantillas mejoradas...")

    # 1. Ensure category model exists
    cat_model = _ensure_category_model(client)
    print(f"   Modelo de categoría: {cat_model['model']} (id={cat_model['id']})")

    # 2. Ensure x_name field on category
    _ensure_field(client, cat_model, "x_name", "Nombre de categoría", "char")

    # 3. ACL for category model
    _ensure_acl(client, cat_model)

    # 4. Form view for category (used when quick-creating a new category)
    _upsert_category_form_view(client, cat_model)
    print("   Vista de categoría configurada.")

    # 5. Add fields to service template
    tmpl_model = _get_model(client, WIZ_SERVICE_TEMPLATE_MODEL)
    _ensure_field(client, tmpl_model, "x_category_id", "Categoría", "many2one", relation=CATEGORY_MODEL)
    _ensure_field(client, tmpl_model, "x_raw_name", "Nombre descriptivo del servicio", "char")
    print("   Campos x_category_id y x_raw_name añadidos a la plantilla.")

    # 6. Custom form view for service template
    _upsert_template_form_view(client, tmpl_model)
    print("   Vista del formulario de plantilla actualizada.")

    # 7. Automation to compose x_name
    _upsert_name_compose_automation(client, tmpl_model)
    print("   Automatización de composición de nombre configurada.")

    print("✅ Categorías y plantillas de servicio listas.")


if __name__ == "__main__":
    client = OdooClient()
    client.connect()
    run(client)
