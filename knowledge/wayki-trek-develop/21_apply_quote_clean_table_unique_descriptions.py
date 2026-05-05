#!/usr/bin/env python3
"""
Personaliza la cotización para:
1) Mostrar tabla limpia (sin texto largo repetido en cada línea).
2) Agregar al final bloque "Detalles del programa" con descripción única por producto base.

Reversible con:
- 18_revert_quote_header_design.py
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


VIEW_NAME = "wtk.sale.quote.clean.table.unique.descriptions"

ARCH_DB = """
<data inherit_id="sale.report_saleorder_document">
    <!-- Ordenar líneas de producto alfabéticamente por producto base -->
    <xpath expr="//t[@t-foreach='lines_to_report']" position="attributes">
        <attribute name="t-foreach">sorted(lines_to_report, key=lambda l: ((l.product_id and l.product_id.product_tmpl_id and l.product_id.product_tmpl_id.name) or l.name or ''))</attribute>
    </xpath>

    <!-- Tabla: usar solo nombre de producto/variante para evitar párrafos largos por línea -->
    <xpath expr="//td[@name='td_product_name']/span[@t-field='line.name']" position="replace">
        <span t-if="line.product_id" t-out="line.product_id.display_name"/>
        <span t-else="" t-field="line.name"/>
    </xpath>

    <!-- Bloque final con descripciones únicas por producto base -->
    <xpath expr="//div[@name='so_total_summary']" position="after">
        <div class="mt-3" style="font-size: 12px;">
            <div style="font-size: 14px; color: #20603D; font-weight: 700; margin-bottom: 8px;">
                Detalles del programa
            </div>
            <t t-set="seen_templates" t-value="[]"/>
            <t t-foreach="sorted(lines_to_report, key=lambda l: ((l.product_id and l.product_id.product_tmpl_id and l.product_id.product_tmpl_id.name) or l.name or ''))" t-as="line">
                <t t-if="line.display_type in (False, None) and line.product_id and line.product_id.product_tmpl_id and line.product_id.product_tmpl_id.id not in seen_templates">
                    <t t-set="seen_templates" t-value="seen_templates + [line.product_id.product_tmpl_id.id]"/>
                    <t t-if="line.product_id.product_tmpl_id.description_sale">
                        <div style="margin: 0 0 10px 0; padding: 8px; border-left: 3px solid #E5B745; background: #FAFAF7;">
                            <div style="font-weight: 600; color: #20603D; margin-bottom: 4px;">
                                <span t-out="line.product_id.product_tmpl_id.name"/>
                            </div>
                            <div t-field="line.product_id.product_tmpl_id.description_sale"/>
                        </div>
                    </t>
                </t>
            </t>
        </div>
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
        "priority": 97,
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
    print("Aplicando tabla limpia + descripciones únicas al final...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")
    base_id = get_base_view_id(client)
    view_id = upsert_view(client, base_id)
    print(f"✅ Vista aplicada (view_id={view_id}).")
    print("Si deseas revertir, ejecuta: 18_revert_quote_header_design.py")


if __name__ == "__main__":
    main()
