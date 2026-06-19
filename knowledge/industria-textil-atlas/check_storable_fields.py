#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    print("Checking fields on product.template for stock/tracking:")
    try:
        fields = client.execute('product.template', 'fields_get', [], ['string', 'type'])
        for f in fields:
            f_lower = f.lower()
            string_lower = fields[f].get('string', '').lower()
            if any(term in f_lower or term in string_lower for term in ['storable', 'track', 'stock', 'inventory', 'type']):
                print(f"  Field: {f} ({fields[f]['type']}) - {fields[f]['string']}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == '__main__':
    main()
