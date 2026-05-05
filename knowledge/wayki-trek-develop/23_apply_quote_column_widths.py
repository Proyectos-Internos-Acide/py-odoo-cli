#!/usr/bin/env python3
"""
Ajusta anchos de columnas en la tabla de cotización:
- Producto (Descripción): más ancha
- Precio unitario: compacta
- Impuestos: compacta
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


VIEW_NAME = "wtk.sale.quote.column.widths"

ARCH_DB = """
<data inherit_id="sale.report_saleorder_document">
    <!-- Headers -->
    <xpath expr="//th[@name='th_description']" position="attributes">
        <attribute name="style">width: 52%;</attribute>
    </xpath>
    <xpath expr="//th[@name='th_priceunit']" position="attributes">
        <attribute name="style">width: 10%; white-space: nowrap;</attribute>
    </xpath>
    <xpath expr="//th[@name='th_taxes']" position="attributes">
        <attribute name="style">width: 8%; white-space: nowrap;</attribute>
    </xpath>
    <xpath expr="//th[@name='th_quantity']" position="attributes">
        <attribute name="style">width: 10%; white-space: nowrap;</attribute>
    </xpath>
    <xpath expr="//th[@name='th_subtotal']" position="attributes">
        <attribute name="style">width: 12%; white-space: nowrap;</attribute>
    </xpath>

    <!-- Body cells -->
    <xpath expr="//td[@name='td_product_name']" position="attributes">
        <attribute name="style">width: 52%;</attribute>
    </xpath>
    <xpath expr="//td[@name='td_product_priceunit']" position="attributes">
        <attribute name="style">width: 10%; white-space: nowrap;</attribute>
    </xpath>
    <xpath expr="//td[@name='td_product_taxes']" position="attributes">
        <attribute name="style">width: 8%; white-space: nowrap;</attribute>
    </xpath>
    <xpath expr="//td[@name='td_product_quantity']" position="attributes">
        <attribute name="style">width: 10%; white-space: nowrap;</attribute>
    </xpath>
    <xpath expr="//td[@name='td_product_subtotal']" position="attributes">
        <attribute name="style">width: 12%; white-space: nowrap;</attribute>
    </xpath>
</data>
""".strip()


def get_base_view_id(client: OdooClient) -> int:
    rec = client.search_read(
        "ir.model.data",
        domain=[["module", "=", "sale"], ["name", "=", "report_saleorder_document"], ["model", "=", "ir.ui.view"]],
        fields=["res_id"],
        limit=1,
    )
    if not rec:
        raise RuntimeError("No se encontró sale.report_saleorder_document")
    return rec[0]["res_id"]


def upsert_view(client: OdooClient, inherit_id: int) -> int:
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
        "priority": 98,
        "active": True,
        "inherit_id": inherit_id,
        "arch_db": ARCH_DB,
    }
    if existing:
        vid = existing[0]["id"]
        client.write("ir.ui.view", [vid], vals)
        return vid
    return client.create("ir.ui.view", vals)


def main() -> None:
    print("Aplicando anchos de columnas en cotización...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")
    base_id = get_base_view_id(client)
    view_id = upsert_view(client, base_id)
    print(f"✅ Anchos de columnas aplicados (view_id={view_id}).")
    print("Si deseas revertir, ejecuta: 18_revert_quote_header_design.py")


if __name__ == "__main__":
    main()
