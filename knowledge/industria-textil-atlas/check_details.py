#!/usr/bin/env python3
"""
Check Odoo version, models, and metadata to prepare data generation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    # 1. Version
    common = client._get_common()
    version_info = common.version()
    print(f"Odoo Version: {version_info}")
    
    # 2. Check if models exist in ir.model
    models_to_check = ['sale.order', 'purchase.order', 'stock.picking', 'stock.warehouse.orderpoint', 'stock.quant']
    print("\nChecking if models exist:")
    for model_name in models_to_check:
        models = client.search_read('ir.model', domain=[['model', '=', model_name]], fields=['model', 'name'])
        if models:
            print(f"  ✅ Model {model_name} exists: {models[0]['name']}")
        else:
            print(f"  ❌ Model {model_name} DOES NOT exist")

    # 3. Check product types available
    print("\nChecking product types available in system:")
    try:
        # Get field definition for 'type' in product.template
        fields_info = client.execute('product.template', 'fields_get', ['type'], ['selection'])
        if 'type' in fields_info:
            print(f"  Product Template 'type' selection: {fields_info['type'].get('selection')}")
    except Exception as e:
        print(f"  Error reading product type selection: {e}")

    # 4. Check picking types (stock.picking.type)
    print("\nChecking picking types:")
    try:
        picking_types = client.search_read(
            'stock.picking.type',
            domain=[],
            fields=['name', 'code', 'warehouse_id', 'default_location_src_id', 'default_location_dest_id'],
            limit=20
        )
        for pt in picking_types:
            print(f"  Picking Type: {pt['name']} [{pt['code']}] (ID: {pt['id']}) - Src: {pt.get('default_location_src_id')} - Dest: {pt.get('default_location_dest_id')} - Warehouse: {pt.get('warehouse_id')}")
    except Exception as e:
        print(f"  Error reading picking types: {e}")

    # 5. Check orderpoint (reordering rule) fields
    print("\nChecking orderpoint fields:")
    try:
        fields_info = client.execute('stock.warehouse.orderpoint', 'fields_get', [], ['string', 'type'])
        important_fields = ['product_id', 'location_id', 'warehouse_id', 'product_min_qty', 'product_max_qty', 'qty_multiple']
        for f in important_fields:
            if f in fields_info:
                print(f"  Field: {f} ({fields_info[f].get('type')}) - {fields_info[f].get('string')}")
            else:
                print(f"  Field: {f} DOES NOT exist")
    except Exception as e:
        print(f"  Error reading orderpoint fields: {e}")

if __name__ == '__main__':
    main()
