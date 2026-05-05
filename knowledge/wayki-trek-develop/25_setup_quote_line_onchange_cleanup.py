#!/usr/bin/env python3
"""
Mejora en tiempo real (onchange) para líneas de cotización:
- Oculta descripción larga dejando solo display_name del producto.

Nota:
- La fusión de líneas duplicadas se mantiene en la automatización on_create_or_write
  (al guardar), porque el sandbox de Odoo restringe operaciones más agresivas en onchange.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


AUTOMATION_NAME = "WTK - Onchange compactar descripción cotización"
ACTION_NAME = "WTK - Onchange compactar descripción"


def _get_model_id(client: OdooClient, model_name: str) -> int:
    rec = client.search_read("ir.model", domain=[["model", "=", model_name]], fields=["id"], limit=1)
    if not rec:
        raise RuntimeError(f"No se encontró modelo {model_name}")
    return rec[0]["id"]


def _get_field_ids(client: OdooClient) -> list[int]:
    fields = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", "sale.order.line"], ["name", "in", ["product_id"]]],
        fields=["id", "name"],
        limit=20,
    )
    return [f["id"] for f in fields]


def upsert_onchange_automation(client: OdooClient) -> None:
    model_id = _get_model_id(client, "sale.order.line")
    trigger_field_ids = _get_field_ids(client)

    code = """
if record.display_type in (False, None) and record.product_id:
    clean_name = record.product_id.display_name or record.name
    if record.name != clean_name:
        record.write({'name': clean_name})
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
                "trigger": "on_change",
                "model_id": model_id,
                "trigger_field_ids": [(6, 0, trigger_field_ids)],
            },
        )
    else:
        auto_id = client.create(
            "base.automation",
            {
                "name": AUTOMATION_NAME,
                "model_id": model_id,
                "trigger": "on_change",
                "active": True,
                "trigger_field_ids": [(6, 0, trigger_field_ids)],
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
    print("Configurando limpieza/merge en onchange de cotización...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")
    upsert_onchange_automation(client)
    print("✅ Automatización onchange activa.")


if __name__ == "__main__":
    main()
