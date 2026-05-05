#!/usr/bin/env python3
"""
Compacta la descripción en líneas de cotización (backend):
- Cuando se crea/actualiza una línea con producto, `name` se reemplaza por
  el display_name del producto (sin description_sale larga).

Objetivo:
- En la pestaña "Líneas de la orden" se vea limpio y legible.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


AUTOMATION_NAME = "WTK - Compactar descripción en sale.order.line"
ACTION_NAME = "WTK - Limpiar texto largo en línea de cotización"


def _get_model_id(client: OdooClient, model_name: str) -> int:
    rec = client.search_read("ir.model", domain=[["model", "=", model_name]], fields=["id"], limit=1)
    if not rec:
        raise RuntimeError(f"No se encontró modelo {model_name}")
    return rec[0]["id"]


def upsert_automation(client: OdooClient) -> None:
    line_model_id = _get_model_id(client, "sale.order.line")

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
                {
                    "name": ACTION_NAME,
                    "model_id": line_model_id,
                    "state": "code",
                    "code": code,
                },
            )
        else:
            action_id = client.create(
                "ir.actions.server",
                {
                    "name": ACTION_NAME,
                    "model_id": line_model_id,
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
                "model_id": line_model_id,
            },
        )
    else:
        auto_id = client.create(
            "base.automation",
            {
                "name": AUTOMATION_NAME,
                "model_id": line_model_id,
                "trigger": "on_create_or_write",
                "active": True,
            },
        )
        action_id = client.create(
            "ir.actions.server",
            {
                "name": ACTION_NAME,
                "model_id": line_model_id,
                "state": "code",
                "code": code,
                "base_automation_id": auto_id,
            },
        )
        client.write("base.automation", [auto_id], {"action_server_ids": [(4, action_id)]})


def normalize_existing_lines(client: OdooClient) -> int:
    lines = client.search_read(
        "sale.order.line",
        domain=[["display_type", "=", False], ["product_id", "!=", False]],
        fields=["id", "name", "product_id"],
        limit=10000,
    )
    updated = 0
    for line in lines:
        product = line.get("product_id")
        if isinstance(product, list) and len(product) >= 2:
            target = product[1]
            if line.get("name") != target:
                client.write("sale.order.line", [line["id"]], {"name": target})
                updated += 1
    return updated


def main() -> None:
    print("Configurando descripción compacta en backend de cotización...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    upsert_automation(client)
    updated = normalize_existing_lines(client)
    print("✅ Automatización activa para nuevas líneas.")
    print(f"✅ Líneas existentes normalizadas: {updated}")


if __name__ == "__main__":
    main()
