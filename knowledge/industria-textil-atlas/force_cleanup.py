#!/usr/bin/env python3
"""
Force cleanup script to delete warehouses 3 and 4 by unlinking them and all
their related records (rules, picking types, moves, quants, routes, etc.)
in the correct order of dependency.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    wh_ids = [3, 4]
    print(f"Force deleting warehouses {wh_ids}...")
    
    # 1. Delete reordering rules (orderpoints)
    try:
        rules = client.search_read('stock.warehouse.orderpoint', domain=[['warehouse_id', 'in', wh_ids]], fields=['id'])
        if rules:
            client.unlink('stock.warehouse.orderpoint', [r['id'] for r in rules])
            print("  ✅ Deleted reordering rules.")
    except Exception as e:
        print(f"  ⚠️ Error deleting rules: {e}")

    # 2. Get picking types linked to these warehouses
    pt_ids = []
    try:
        pts = client.search_read('stock.picking.type', domain=[['warehouse_id', 'in', wh_ids]], fields=['id'])
        pt_ids = [pt['id'] for pt in pts]
        print(f"  Found picking types: {pt_ids}")
    except Exception as e:
        print(f"  ⚠️ Error finding picking types: {e}")

    # 3. Find pickings, moves, valuation layers, and move lines
    if pt_ids:
        try:
            pickings = client.search_read('stock.picking', domain=[['picking_type_id', 'in', pt_ids]], fields=['id'])
            picking_ids = [p['id'] for p in pickings]
            if picking_ids:
                print(f"  Found pickings: {picking_ids}")
                
                # Find moves
                moves = client.search_read('stock.move', domain=[['picking_id', 'in', picking_ids]], fields=['id'])
                move_ids = [m['id'] for m in moves]
                
                if move_ids:
                    print(f"    Found stock moves: {move_ids}")
                    
                    # Delete stock.valuation.layer if any
                    try:
                        svls = client.search_read('stock.valuation.layer', domain=[['stock_move_id', 'in', move_ids]], fields=['id'])
                        if svls:
                            client.unlink('stock.valuation.layer', [s['id'] for s in svls])
                            print("      ✅ Deleted stock valuation layers.")
                    except Exception as ev:
                        print(f"      ⚠️ No valuation layers deleted: {ev}")
                        
                    # Delete stock.move.line if any
                    try:
                        smls = client.search_read('stock.move.line', domain=[['move_id', 'in', move_ids]], fields=['id'])
                        if smls:
                            client.unlink('stock.move.line', [s['id'] for s in smls])
                            print("      ✅ Deleted stock move lines.")
                    except Exception as el:
                        print(f"      ⚠️ No move lines deleted: {el}")
                        
                    # Delete stock moves
                    try:
                        client.unlink('stock.move', move_ids)
                        print("    ✅ Deleted stock moves.")
                    except Exception as em:
                        print(f"    ❌ Error deleting stock moves: {em}")
                        
                # Delete pickings
                try:
                    client.unlink('stock.picking', picking_ids)
                    print("  ✅ Deleted pickings.")
                except Exception as ep:
                    print(f"  ❌ Error deleting pickings: {ep}")
        except Exception as e:
            print(f"  ⚠️ Error in picking/move cleanup: {e}")

    # 4. Delete stock rules (stock.rule)
    if pt_ids:
        try:
            rules = client.search_read('stock.rule', domain=[['picking_type_id', 'in', pt_ids]], fields=['id'])
            if rules:
                client.unlink('stock.rule', [r['id'] for r in rules])
                print("  ✅ Deleted stock rules referencing picking types.")
        except Exception as e:
            print(f"  ⚠️ Error deleting stock rules for picking types: {e}")

    # 5. Delete routes linked to warehouses
    try:
        # Find warehouse routes
        routes = client.search_read('stock.route', domain=['|', ['warehouse_ids', 'in', wh_ids], ['supplied_wh_ids', 'in', wh_ids]], fields=['id', 'name'])
        if routes:
            print(f"  Found routes: {[r['name'] for r in routes]}")
            client.unlink('stock.route', [r['id'] for r in routes])
            print("  ✅ Deleted warehouse routes.")
    except Exception as e:
        print(f"  ⚠️ Error deleting warehouse routes: {e}")

    # 6. Delete picking types
    if pt_ids:
        try:
            client.unlink('stock.picking.type', pt_ids)
            print("  ✅ Deleted picking types.")
        except Exception as e:
            print(f"  ❌ Error deleting picking types: {e}")

    # 7. Delete locations
    try:
        # Locations that belong to the warehouses
        locs = client.search_read('stock.location', domain=['|', ['complete_name', 'ilike', 'XAGR'], ['complete_name', 'ilike', 'XATI']], fields=['id', 'complete_name'])
        loc_ids = [l['id'] for l in locs]
        if loc_ids:
            # Delete quants first if possible (even if it might error, let's try)
            try:
                quants = client.search_read('stock.quant', domain=[['location_id', 'in', loc_ids]], fields=['id'])
                if quants:
                    client.unlink('stock.quant', [q['id'] for q in quants])
                    print("    ✅ Deleted stock quants.")
            except Exception as eq:
                print(f"    ⚠️ Could not delete quants directly: {eq}")
                
            # Unlink child locations first, then parent
            # Sort by complete_name length descending to delete children first
            locs.sort(key=lambda x: len(x['complete_name']), reverse=True)
            for loc in locs:
                try:
                    client.unlink('stock.location', [loc['id']])
                    print(f"    ✅ Deleted location {loc['complete_name']}")
                except Exception as el:
                    print(f"    ❌ Error deleting location {loc['complete_name']}: {el}")
    except Exception as e:
        print(f"  ⚠️ Error cleaning up locations: {e}")

    # 8. Finally delete warehouses
    for wh_id in wh_ids:
        try:
            client.unlink('stock.warehouse', [wh_id])
            print(f"  ✅ Deleted warehouse ID {wh_id}")
        except Exception as e:
            print(f"  ❌ Error deleting warehouse {wh_id}: {e}")

if __name__ == '__main__':
    main()
