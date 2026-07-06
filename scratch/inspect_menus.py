import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    print("--- Fetching root menus (parent_id = False) ---")
    menus = client.search_read(
        'ir.ui.menu',
        [('parent_id', '=', False)],
        fields=['id', 'name', 'xmlid', 'complete_name']
    )
    for m in menus:
        print(f"ID: {m['id']} | Name: {m['name']} | XMLID: {m.get('xmlid')} | Complete Name: {m.get('complete_name')}")

if __name__ == '__main__':
    main()
