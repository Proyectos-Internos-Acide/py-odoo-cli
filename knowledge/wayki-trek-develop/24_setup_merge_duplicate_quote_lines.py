#!/usr/bin/env python3
"""
Automatiza la consolidación de líneas duplicadas en cotizaciones:
- Si se agrega el mismo producto/variante en la misma cotización,
  se suma cantidad en una sola línea y se elimina la duplicada.

Criterios de "misma línea":
- mismo pedido (sale.order)
- mismo producto (product_id, incluye variante)
- misma UoM
- mismo precio unitario
- mismo descuento
- mismos impuestos
- mismo texto de línea (name)
- solo en estados de cotización (draft/sent)
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


AUTOMATION_NAME = "WTK - Unificar líneas duplicadas en cotización"
ACTION_NAME = "WTK - Merge líneas repetidas (sale.order.line)"


def _get_model_id(client: OdooClient, model_name: str) -> int:
    rec = client.search_read("ir.model", domain=[["model", "=", model_name]], fields=["id"], limit=1)
    if not rec:
        raise RuntimeError(f"No se encontró modelo {model_name}")
    return rec[0]["id"]


def upsert_automation(client: OdooClient) -> None:
    model_id = _get_model_id(client, "sale.order.line")

    code = """
if record.display_type in (False, None) and record.order_id and record.product_id:
    if record.order_id.state in ('draft', 'sent'):
        candidates = env['sale.order.line'].search([
            ('order_id', '=', record.order_id.id),
            ('id', '!=', record.id),
            ('display_type', '=', False),
            ('product_id', '=', record.product_id.id),
            ('product_uom', '=', record.product_uom.id),
            ('price_unit', '=', record.price_unit),
            ('discount', '=', record.discount),
        ], order='id asc')

        record_taxes = set(record.tax_id.ids)
        for cand in candidates:
            if set(cand.tax_id.ids) == record_taxes and (cand.name or '') == (record.name or ''):
                cand.write({'product_uom_qty': cand.product_uom_qty + record.product_uom_qty})
                record.unlink()
                break
""".strip()

    existing = client.search_read(
        "base.automation",
        domain=[["name", "=", AUTOMATION_NAME], ["model_name", "=", "sale.order.line"]],
        fields=["id", "action_server_ids"],
        limit=1,
    )

    if existing:
        auto_id = existing[0]["id"]
        action_ids = existing[0].get("action_server_ids") or []

        if action_ids:
            client.write(
                "ir.actions.server",
                action_ids,
                {"name": ACTION_NAME, "model_id": model_id, "state": "code", "code": code},
            )
        else:
            action_id = client.create(
                "ir.actions.server",
                {
                    "name": ACTION_NAME,
                    "model_id": model_id,
                    "state": "code",
                    "code": code,
                    "base_automation_id": auto_id,
                },
            )
            client.write("base.automation", [auto_id], {"action_server_ids": [(4, action_id)]})

        client.write(
            "base.automation",
            [auto_id],
            {
                "active": True,
                "trigger": "on_create_or_write",
                "model_id": model_id,
            },
        )
    else:
        auto_id = client.create(
            "base.automation",
            {
                "name": AUTOMATION_NAME,
                "model_id": model_id,
                "trigger": "on_create_or_write",
                "active": True,
            },
        )
        action_id = client.create(
            "ir.actions.server",
            {
                "name": ACTION_NAME,
                "model_id": model_id,
                "state": "code",
                "code": code,
                "base_automation_id": auto_id,
            },
        )
        client.write("base.automation", [auto_id], {"action_server_ids": [(4, action_id)]})


def main() -> None:
    print("Configurando merge automático de líneas duplicadas en cotización...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")
    upsert_automation(client)
    print("✅ Automatización activa.")


if __name__ == "__main__":
    main()
