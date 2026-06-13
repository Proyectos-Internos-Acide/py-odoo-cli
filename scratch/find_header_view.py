#!/usr/bin/env python3
"""
Find where the Cusco / company header info is defined — 
look at the web.external_layout or report header views
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    print("Conectado.\n")

    # Search all views for "Cusco" or "waykitrek"
    views = client.search_read(
        "ir.ui.view",
        [["arch_db", "ilike", "Cusco"]],
        ["id", "name", "key", "model", "type", "inherit_id"]
    )
    print(f"Views with 'Cusco': {len(views)}")
    for v in views:
        print(f"  ID:{v['id']} | {v['name']} | key:{v['key']} | model:{v['model']} | type:{v['type']}")

    print()
    views2 = client.search_read(
        "ir.ui.view",
        [["arch_db", "ilike", "waykitrek"]],
        ["id", "name", "key", "model", "type", "arch_db"]
    )
    print(f"Views with 'waykitrek': {len(views2)}")
    for v in views2:
        print(f"  ID:{v['id']} | {v['name']} | key:{v['key']}")
        arch = v.get("arch_db", "") or ""
        idx = arch.find("waykitrek")
        print("  Context:", arch[max(0, idx-100):idx+200])
        print()

if __name__ == "__main__":
    main()
