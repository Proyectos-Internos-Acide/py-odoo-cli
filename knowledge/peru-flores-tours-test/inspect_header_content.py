#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from odoo_cli import OdooClient

def main():
    try:
        client = OdooClient()
        client.connect()
        
        view_id = 2113
        view = client.search_read('ir.ui.view', [['id', '=', view_id]], ['name', 'key', 'arch_db', 'arch_base'])
        if view:
            content = view[0].get('arch_db') or view[0].get('arch_base')
            print(f"--- Header View {view_id} ---")
            print(content)
            
        view_id = 2879
        view = client.search_read('ir.ui.view', [['id', '=', view_id]], ['name', 'key', 'arch_db', 'arch_base'])
        if view:
            content = view[0].get('arch_db') or view[0].get('arch_base')
            print(f"--- Header View {view_id} ---")
            print(content)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
