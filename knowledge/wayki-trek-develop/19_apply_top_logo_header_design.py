#!/usr/bin/env python3
"""
Aplica personalización del header superior (zona logo) en reportes,
incluyendo cotizaciones.

Reversible con:
- 18_revert_quote_header_design.py
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


VIEW_NAME = "wtk.external_layout.top_header.custom"
TARGET_XMLID = ("web", "external_layout_standard")

ARCH_DB = """
<data inherit_id="web.external_layout_standard">
    <xpath expr="//table[@class='table-borderless']" position="replace">
        <table class="table-borderless" style="width: 100%; border-bottom: 3px solid #E5B745; margin-bottom: 4px;">
            <tr>
                <td t-if="company.logo" class="align-top pe-3" style="width: 32%;">
                    <img class="o_company_logo_big" t-att-src="image_data_uri(company.logo)" alt="Logo" style="max-height: 86px;"/>
                </td>
                <td class="align-top text-end" style="width: 68%; padding-bottom: 8px;">
                    <div style="font-size: 15px; color: #20603D; font-weight: 700; letter-spacing: 0.4px;">
                        WAYKI TREK S.A.C.
                    </div>
                    <div style="font-size: 11px; color: #374151; margin-top: 2px;" t-if="company.phone">
                        Tel: <span t-field="company.phone"/>
                    </div>
                    <div style="font-size: 11px; color: #374151;" t-if="company.email">
                        Email: <span t-field="company.email"/>
                    </div>
                    <div style="font-size: 11px; color: #374151;" t-if="company.website">
                        Web: <span t-field="company.website"/>
                    </div>
                    <div style="font-size: 10px; color: #6B7280; margin-top: 4px;">
                        Cotización oficial - Wayki Trek Experience
                    </div>
                </td>
            </tr>
        </table>
    </xpath>
</data>
""".strip()


def get_target_view_id(client: OdooClient) -> int:
    module, name = TARGET_XMLID
    xmlid = client.search_read(
        "ir.model.data",
        domain=[["module", "=", module], ["name", "=", name], ["model", "=", "ir.ui.view"]],
        fields=["res_id"],
        limit=1,
    )
    if not xmlid:
        raise RuntimeError("No se encontró la vista base external_layout_standard.")
    return xmlid[0]["res_id"]


def upsert_view(client: OdooClient, inherit_view_id: int) -> int:
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
        "priority": 95,
        "active": True,
        "inherit_id": inherit_view_id,
        "arch_db": ARCH_DB,
    }
    if existing:
        vid = existing[0]["id"]
        client.write("ir.ui.view", [vid], vals)
        return vid
    return client.create("ir.ui.view", vals)


def main() -> None:
    print("Aplicando diseño superior (logo/header) de cotización...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    base_view_id = get_target_view_id(client)
    view_id = upsert_view(client, base_view_id)
    print(f"✅ Header superior personalizado aplicado (view_id={view_id}).")
    print("Si deseas revertir, ejecuta: 18_revert_quote_header_design.py")


if __name__ == "__main__":
    main()
