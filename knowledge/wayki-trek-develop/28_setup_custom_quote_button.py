#!/usr/bin/env python3
"""
Agrega botón "Cotización personalizada" en cotizaciones (sale.order form).

Acción del botón:
- Muestra un aviso de Odoo indicando "Estamos trabajando en ello".
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


ACTION_NAME = "WTK - Placeholder Cotización personalizada"
VIEW_NAME = "wtk.sale.order.form.custom.quote.button"


def _get_model_id(client: OdooClient, model_name: str) -> int:
    rec = client.search_read("ir.model", domain=[["model", "=", model_name]], fields=["id"], limit=1)
    if not rec:
        raise RuntimeError(f"No se encontró modelo: {model_name}")
    return rec[0]["id"]


def _upsert_server_action(client: OdooClient, model_id: int) -> int:
    code = """
action = {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': 'Cotización personalizada',
        'message': 'Estamos trabajando en ello.',
        'type': 'warning',
        'sticky': False,
    }
}
""".strip()

    existing = client.search_read(
        "ir.actions.server",
        domain=[["name", "=", ACTION_NAME], ["model_id", "=", model_id]],
        fields=["id"],
        limit=1,
    )
    vals = {
        "name": ACTION_NAME,
        "model_id": model_id,
        "state": "code",
        "code": code,
    }
    if existing:
        aid = existing[0]["id"]
        client.write("ir.actions.server", [aid], vals)
        return aid
    return client.create("ir.actions.server", vals)


def _upsert_view(client: OdooClient, action_id: int) -> int:
    base_xml = client.search_read(
        "ir.model.data",
        domain=[["module", "=", "sale"], ["name", "=", "view_order_form"], ["model", "=", "ir.ui.view"]],
        fields=["res_id"],
        limit=1,
    )
    if not base_xml:
        raise RuntimeError("No se encontró sale.view_order_form")
    base_view_id = base_xml[0]["res_id"]

    # Usamos ID numérico directo de la acción creada.
    arch_db = f"""
<data inherit_id="sale.view_order_form">
    <xpath expr="//form/header/button[@name='action_quotation_send']" position="after">
        <button string="Cotización personalizada"
                type="action"
                name="{action_id}"
                class="btn-primary"
                style="background-color:#20603D !important;border-color:#20603D !important;color:#FFFFFF !important;"
                invisible="state not in ('draft','sent')"/>
    </xpath>
</data>
""".strip()

    existing = client.search_read(
        "ir.ui.view",
        domain=[["name", "=", VIEW_NAME], ["type", "=", "form"]],
        fields=["id"],
        limit=1,
    )
    vals = {
        "name": VIEW_NAME,
        "model": "sale.order",
        "type": "form",
        "mode": "extension",
        "active": True,
        "priority": 99,
        "inherit_id": base_view_id,
        "arch_db": arch_db,
    }
    if existing:
        vid = existing[0]["id"]
        client.write("ir.ui.view", [vid], vals)
        return vid
    return client.create("ir.ui.view", vals)


def main() -> None:
    print("Configurando botón de cotización personalizada...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    sale_order_model_id = _get_model_id(client, "sale.order")
    action_id = _upsert_server_action(client, sale_order_model_id)
    view_id = _upsert_view(client, action_id)

    print(f"✅ Acción creada/actualizada (id={action_id})")
    print(f"✅ Vista aplicada (id={view_id})")


if __name__ == "__main__":
    main()
