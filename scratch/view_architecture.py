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

    # Search for views that contain description_sale in their arch_db
    views = client.search_read(
        'ir.ui.view',
        domain=[['model', '=', 'product.template'], ['arch_db', 'ilike', 'description_sale']],
        fields=['id', 'name', 'xml_id', 'inherit_id', 'priority']
    )
    print(f"\nEncontradas {len(views)} vistas que mencionan 'description_sale':")
    for v in views:
        print(f"ID: {v['id']} | Name: {v['name']} | XML ID: {v.get('xml_id')} | Inherit ID: {v['inherit_id']}")

    # Let's inspect the non-inherited view first or the main one
    print("\n--- Detalles de la vista heredada product_template_form_inherit_sale_html ---")
    my_views = client.search_read(
        'ir.ui.view',
        domain=[['name', '=', 'product_template_form_inherit_sale_html']],
        fields=['id', 'name', 'arch_db', 'inherit_id']
    )
    if my_views:
        print("Arch actual:")
        print(my_views[0]['arch_db'])
        parent_id = my_views[0]['inherit_id'][0]
        print(f"Parent View ID: {parent_id}")
        
        # Get parent view arch
        parent = client.search_read('ir.ui.view', [['id', '=', parent_id]], ['name', 'arch_db'])
        if parent:
            print(f"\n--- Vista Padre: {parent[0]['name']} ---")
            print(parent[0]['arch_db'])

if __name__ == "__main__":
    main()
