#!/usr/bin/env python3
"""
Cleanup script to rename the created warehouses (ID 3 and 4) and their locations
to [INACTIVO] to prevent them from interfering, since Odoo's integrity constraints
prevent deleting/archiving records with transaction history.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    wh_ids = [3, 4]
    print(f"Renaming warehouses {wh_ids} to [INACTIVO]...")
    
    # 1. Rename Warehouses and change codes
    for wh_id in wh_ids:
        try:
            wh = client.search_read('stock.warehouse', domain=[['id', '=', wh_id]], fields=['name', 'code'])
            if wh:
                old_name = wh[0]['name']
                new_name = f"[INACTIVO] {old_name}"
                new_code = f"X{wh[0]['code']}"[:5] # Max 5 characters
                print(f"Renaming warehouse '{old_name}' -> '{new_name}' (Code: {new_code})")
                client.write('stock.warehouse', [wh_id], {
                    'name': new_name,
                    'code': new_code
                })
        except Exception as e:
            print(f"Error renaming warehouse {wh_id}: {e}")
            
    # 2. Rename Locations
    try:
        # Find locations containing AGR or ATI
        locs = client.search_read('stock.location', domain=['|', ['complete_name', 'ilike', 'AGR'], ['complete_name', 'ilike', 'ATI']], fields=['id', 'name', 'complete_name'])
        for loc in locs:
            old_name = loc['name']
            new_name = f"x_{old_name}"
            print(f"Renaming location '{loc['complete_name']}' -> name: '{new_name}'")
            client.write('stock.location', [loc['id']], {
                'name': new_name
            })
            print(f"  ✅ Location renamed.")
    except Exception as e:
        print(f"Error renaming locations: {e}")

if __name__ == '__main__':
    main()
