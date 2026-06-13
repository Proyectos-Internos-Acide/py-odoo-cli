#!/usr/bin/env python3
"""
Find the actual embedded list inside the sale.order form <field name="order_line"> tag
The form arch has an inline list embedded inside the o2m field.
Let's get the full arch and search for the inline list with actual columns.
"""
import sys
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    print("Conectado a Odoo.\n")

    # Get the full arch and dump it to a file for analysis
    base = client.search_read("ir.ui.view", [["id", "=", 1583]], ["arch_db"])
    arch = base[0]["arch_db"]
    
    # Write full arch to file for manual inspection
    out_path = Path(__file__).parent / "sale_order_form_arch.xml"
    out_path.write_text(arch, encoding="utf-8")
    print(f"Full arch saved to: {out_path}")
    print(f"Total length: {len(arch)} chars")
    
    # Find "Cantidad" or column-like definitions
    for keyword in ["product_uom_qty", "price_unit", "tax_ids", "price_subtotal"]:
        positions = [m.start() for m in re.finditer(re.escape(keyword), arch)]
        print(f"  '{keyword}' found at positions: {positions}")

if __name__ == "__main__":
    main()
