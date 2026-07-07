import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    # Menus to deactivate:
    # 127: Invoicing (Facturación)
    # 227: Link Tracker (Rastreador de enlaces)
    menu_ids = [127, 227]
    
    print(f"--- Deactivating menus with IDs {menu_ids} ---")
    for menu_id in menu_ids:
        # Fetch the menu to confirm it exists and check its current state
        menu = client.search_read('ir.ui.menu', [('id', '=', menu_id)], fields=['name', 'active'])
        if menu:
            name = menu[0]['name']
            current_active = menu[0]['active']
            print(f"Found menu: {name} (ID: {menu_id}), Active: {current_active}")
            
            # Deactivate
            success = client.write('ir.ui.menu', [menu_id], {'active': False})
            if success:
                print(f"[OK] Successfully deactivated menu: {name} (ID: {menu_id})")
            else:
                print(f"[ERROR] Failed to deactivate menu: {name} (ID: {menu_id})")
        else:
            print(f"[WARNING] Menu with ID {menu_id} not found.")

if __name__ == '__main__':
    main()
