#!/usr/bin/env python3
"""
Find menu items in Odoo matching 'Valoración' or 'Valuation'.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    print("Searching for Valuation menu items...")
    try:
        # Search ir.ui.menu
        menus = client.search_read(
            'ir.ui.menu',
            domain=['|', ['name', 'ilike', 'valoraci'], ['name', 'ilike', 'valuation']],
            fields=['name', 'complete_name', 'action', 'web_icon']
        )
        print(f"Found {len(menus)} menus:")
        for m in menus:
            print(f"  Menu: {m['name']} ({m['complete_name']}) - Action: {m.get('action')}")
    except Exception as e:
        print(f"Error searching ir.ui.menu: {e}")
        
    print("\nSearching for Stock Valuation actions in ir.actions.act_window...")
    try:
        actions = client.search_read(
            'ir.actions.act_window',
            domain=['|', ['name', 'ilike', 'valoraci'], ['name', 'ilike', 'valuation']],
            fields=['name', 'res_model', 'view_mode']
        )
        print(f"Found {len(actions)} window actions:")
        for a in actions:
            print(f"  Action: {a['name']} (ID: {a['id']}) - Model: {a.get('res_model')}")
    except Exception as e:
        print(f"Error searching actions: {e}")

if __name__ == '__main__':
    main()
