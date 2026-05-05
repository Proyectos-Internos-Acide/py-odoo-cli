#!/usr/bin/env python3
"""
Aplica diseño personalizado de cabecera para cotizaciones (sale.order report).

Reversible:
- Este script crea/actualiza una vista QWeb heredada.
- Para revertir, usa `18_revert_quote_header_design.py`.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


VIEW_NAME = "wtk.sale.quote.header.custom"
TARGET_REPORT_XMLID = ("sale", "report_saleorder_document")


ARCH_DB = """
<data inherit_id="sale.report_saleorder_document">
    <xpath expr="//div[@class='page']/div[@class='oe_structure']" position="after">
        <div style="margin-bottom: 16px; border: 1px solid #20603D; border-radius: 8px; overflow: hidden;">
            <div style="background: #20603D; color: #FFFFFF; padding: 10px 14px;">
                <strong style="font-size: 14px;">WAYKI TREK S.A.C.</strong>
            </div>
            <div style="padding: 12px 14px; font-size: 12px; color: #1f2937;">
                <div style="font-size: 13px; color: #20603D; margin-bottom: 6px;">
                    <strong>Propuesta de viaje personalizada</strong>
                </div>
                <div style="margin-bottom: 2px;">
                    Gracias por confiar en Wayki Trek.
                </div>
                <div style="margin-bottom: 2px;">
                    Esta cotización ha sido diseñada para brindarte una experiencia segura, humana y memorable.
                </div>
                <div style="margin-top: 8px; padding: 8px; background: #F8F5EA; border-left: 4px solid #E5B745;">
                    <span style="color: #20603D;">
                        <strong>Nota:</strong> Los precios se muestran en USD por persona, según la configuración del servicio.
                    </span>
                </div>
            </div>
        </div>
    </xpath>
</data>
""".strip()


def get_target_view_id(client: OdooClient) -> int:
    module, name = TARGET_REPORT_XMLID
    xmlid = client.search_read(
        "ir.model.data",
        domain=[["module", "=", module], ["name", "=", name], ["model", "=", "ir.ui.view"]],
        fields=["res_id"],
        limit=1,
    )
    if not xmlid:
        raise RuntimeError("No se encontró la vista base de reporte de cotización.")
    return xmlid[0]["res_id"]


def upsert_custom_view(client: OdooClient, inherit_view_id: int) -> int:
    existing = client.search_read(
        "ir.ui.view",
        domain=[["name", "=", VIEW_NAME], ["type", "=", "qweb"]],
        fields=["id"],
        limit=1,
    )
    vals = {
        "name": VIEW_NAME,
        "type": "qweb",
        "mode": "extension",
        "priority": 90,
        "active": True,
        "inherit_id": inherit_view_id,
        "arch_db": ARCH_DB,
    }
    if existing:
        view_id = existing[0]["id"]
        client.write("ir.ui.view", [view_id], vals)
        return view_id
    return client.create("ir.ui.view", vals)


def main() -> None:
    print("Aplicando diseño de cabecera de cotización...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    base_view_id = get_target_view_id(client)
    view_id = upsert_custom_view(client, base_view_id)
    print(f"✅ Vista personalizada aplicada (view_id={view_id}).")
    print("Si deseas revertir, ejecuta: 18_revert_quote_header_design.py")


if __name__ == "__main__":
    main()
