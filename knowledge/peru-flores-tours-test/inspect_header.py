#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from odoo_cli import OdooClient

def main():
    try:
        client = OdooClient()
        client.connect()
        
        print("--- Languages ---")
        langs = client.search_read('res.lang', [], ['name', 'code', 'active'])
        for l in langs:
            print(f"ID: {l['id']} - Name: {l['name']} - Code: {l['code']} - Active: {l['active']}")

        print("\n--- Website ---")
        websites = client.search_read('website', [], ['name', 'language_ids'])
        for w in websites:
            print(f"Website ID: {w['id']} - Name: {w['name']} - Languages: {w.get('language_ids')}")

        print("\n--- Header Views ---")
        domain = ['|', ('key', 'ilike', 'website.header%'), ('key', 'ilike', 'website.template_header%')]
        views = client.search_read('ir.ui.view', domain, ['id', 'name', 'key', 'active'])
        for v in views:
            print(f"ID: {v['id']} - Name: {v['name']} - Key: {v['key']} - Active: {v['active']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
