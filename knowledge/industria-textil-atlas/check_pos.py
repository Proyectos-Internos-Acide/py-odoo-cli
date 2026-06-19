#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    # Check pos.order and pos.session
    models = client.search_read('ir.model', domain=[['model', 'in', ['pos.order', 'pos.session']]], fields=['model', 'name'])
    print("POS Models:")
    for m in models:
        print(f"  Model: {m['model']} - {m['name']}")

if __name__ == '__main__':
    main()
