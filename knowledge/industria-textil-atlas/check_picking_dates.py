#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    print("Checking date fields in stock.picking:")
    try:
        fields = client.execute('stock.picking', 'fields_get', [], ['string', 'type'])
        for f in fields:
            if 'date' in f or 'time' in f:
                print(f"  Field: {f} ({fields[f]['type']}) - {fields[f]['string']}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == '__main__':
    main()
