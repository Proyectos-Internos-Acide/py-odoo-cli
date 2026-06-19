#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    print("Checking stock.move fields:")
    try:
        fields = client.execute('stock.move', 'fields_get', [], ['string', 'type'])
        for f in ['product_uom_qty', 'quantity', 'qty_done', 'state', 'picked']:
            if f in fields:
                print(f"  Field: {f} ({fields[f]['type']}) - {fields[f]['string']}")
            else:
                print(f"  Field: {f} DOES NOT exist")
    except Exception as e:
        print(f"  Error: {e}")

    print("\nChecking stock.picking fields:")
    try:
        fields = client.execute('stock.picking', 'fields_get', [], ['string', 'type'])
        for f in ['state', 'picking_type_id', 'location_id', 'location_dest_id', 'move_ids']:
            if f in fields:
                print(f"  Field: {f} ({fields[f]['type']}) - {fields[f]['string']}")
            else:
                print(f"  Field: {f} DOES NOT exist")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == '__main__':
    main()
