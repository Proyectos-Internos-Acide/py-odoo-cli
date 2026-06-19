#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    print("Checking detailed_type field on product.template:")
    try:
        fields = client.execute('product.template', 'fields_get', ['detailed_type'], ['selection'])
        if 'detailed_type' in fields:
            print(f"  Selection: {fields['detailed_type'].get('selection')}")
        else:
            print("  detailed_type field DOES NOT exist")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == '__main__':
    main()
