#!/usr/bin/env python3
"""
Reduce el espacio en blanco superior de la cotización (PDF/impresión)
ocultando el bloque de dirección de destinatario reservado por layout.

Reversible con:
- 18_revert_quote_header_design.py
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


VIEW_NAME = "wtk.sale.quote.compact.spacing"

ARCH_DB = """
<data inherit_id="sale.report_saleorder_document">
    <xpath expr="//t[@t-call='web.external_layout']" position="attributes">
        <attribute name="hide_recipient_address">True</attribute>
        <attribute name="custom_address_spacing">mb-1</attribute>
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
        "priority": 96,
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
    print("Aplicando compactación de espacio en cotización...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")
    base_view_id = get_base_view_id(client)
    view_id = upsert_view(client, base_view_id)
    print(f"✅ Espaciado compactado (view_id={view_id}).")
    print("Si deseas revertir, ejecuta: 18_revert_quote_header_design.py")


if __name__ == "__main__":
    main()
