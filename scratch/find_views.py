#!/usr/bin/env python3
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    print("Conectado a Odoo.")

    # Search for all form views on product.template
    views = client.search_read(
        'ir.ui.view',
        domain=[['model', '=', 'product.template'], ['type', '=', 'form']],
        fields=['id', 'name', 'inherit_id', 'active']
    )
    print(f"\nForm views found: {len(views)}")
    for v in views:
        print(f"ID: {v['id']} | Name: {v['name']} | Inherit ID: {v['inherit_id']} | Active: {v['active']}")

if __name__ == "__main__":
    main()
