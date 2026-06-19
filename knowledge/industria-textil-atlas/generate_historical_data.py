#!/usr/bin/env python3
"""
Script to generate historical data spread across the last 5 days
in the pre-existing warehouses: Almacén casa (WHC) and Almacén Tienda (WH).
"""

import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def validate_picking_with_date(client, picking_id, date_str):
    """Confirm, assign, set quantity, validate, and set historical date on a picking."""
    try:
        picking = client.search_read('stock.picking', domain=[['id', '=', picking_id]], fields=['state', 'name'])
        if not picking:
            return False
            
        name = picking[0]['name']
        state = picking[0]['state']
        
        if state == 'draft':
            client.execute('stock.picking', 'action_confirm', [picking_id])
            state = client.search_read('stock.picking', domain=[['id', '=', picking_id]], fields=['state'])[0]['state']
            
        if state in ['confirmed', 'waiting']:
            client.execute('stock.picking', 'action_assign', [picking_id])
            state = client.search_read('stock.picking', domain=[['id', '=', picking_id]], fields=['state'])[0]['state']
            
        # Read moves to update done quantity and date
        moves = client.search_read('stock.move', domain=[['picking_id', '=', picking_id]], fields=['id', 'product_uom_qty', 'state'])
        for m in moves:
            if m['state'] not in ['draft', 'cancel', 'done']:
                client.write('stock.move', [m['id']], {
                    'quantity': m['product_uom_qty'],
                    'picked': True,
                    'date': date_str
                })
                
        # Validate picking
        client.execute('stock.picking', 'button_validate', [picking_id])
        
        # Overwrite dates to make it historical
        # fields: date_done on stock.picking, date on stock.move
        client.write('stock.picking', [picking_id], {
            'scheduled_date': date_str,
            'date_done': date_str
        })
        
        # Force moves dates as well after validation
        for m in moves:
            client.write('stock.move', [m['id']], {'date': date_str})
            
        final_state = client.search_read('stock.picking', domain=[['id', '=', picking_id]], fields=['state'])[0]['state']
        print(f"      ✅ Picking {name} (ID: {picking_id}) final state: {final_state} - Date: {date_str}")
        return True
    except Exception as e:
        print(f"      ❌ Error validating picking {picking_id}: {e}")
        return False

def main():
    client = OdooClient()
    client.connect()
    
    print("====================================================")
    print("🚀 GENERATING HISTORICAL ODOO DATA (LAST 5 DAYS) 🚀")
    print("====================================================")
    
    # Real warehouse IDs
    supplier_id = 22 # PROVEEDOR TEXTIL LIMA S.A.C.
    wh_agr_id = 2    # Almacén casa
    wh_ati_id = 1    # Almacén Tienda
    loc_agr_id = 16  # WHC/Existencias
    loc_ati_id = 5   # WH/Stock
    loc_customer_id = 2 # Customers
    
    # Retrieve clients
    clients = client.search_read('res.partner', domain=[['customer_rank', '>', 0]], fields=['id', 'name'])
    client_ids = [c['id'] for c in clients]
    if len(client_ids) < 5:
        print("   ❌ Error: Less than 5 clients found in system. Run generate_all_data.py first.")
        sys.exit(1)
        
    print(f"   Using clients: {[c['name'] for c in clients[:5]]}")
    
    # Retrieve product variants
    products = client.search_read(
        'product.product',
        domain=[['default_code', 'in', ['POLO-PIQUE', 'CAMISA-OXFORD', 'PANTALON-CHINO', 'CASACA-CORTAVIENTO', 'POLERA-CAPUCHA']]],
        fields=['id', 'name', 'default_code', 'uom_id', 'standard_price']
    )
    product_map = {}
    for p in products:
        product_map[p['default_code']] = {
            'id': p['id'],
            'name': p['name'],
            'uom_id': p['uom_id'][0] if p.get('uom_id') else 1,
            'standard_price': p['standard_price']
        }
        
    # Get picking types
    picking_types_whc = client.search_read('stock.picking.type', domain=[['code', '=', 'incoming'], ['warehouse_id', '=', wh_agr_id]], fields=['id'])
    picking_type_incoming = picking_types_whc[0]['id']
    
    picking_types_whc_internal = client.search_read('stock.picking.type', domain=[['code', '=', 'internal'], ['warehouse_id', '=', wh_agr_id]], fields=['id'])
    picking_type_internal = picking_types_whc_internal[0]['id']
    
    picking_types_wh_delivery = client.search_read('stock.picking.type', domain=[['code', '=', 'outgoing'], ['warehouse_id', '=', wh_ati_id], ['name', 'not ilike', 'pos'], ['name', 'not ilike', 'pdv']], fields=['id'])
    picking_type_delivery = picking_types_wh_delivery[0]['id']
    
    # 5 Days Ago
    date_5_days_ago = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n📅 [Day -5: {date_5_days_ago}] - Replenishment of stock in Almacén casa (WHC)")
    po_lines_5d = [
        (0, 0, {
            'product_id': product_map['POLO-PIQUE']['id'],
            'name': product_map['POLO-PIQUE']['name'],
            'product_qty': 300,
            'price_unit': product_map['POLO-PIQUE']['standard_price'],
            'date_planned': date_5_days_ago
        }),
        (0, 0, {
            'product_id': product_map['CAMISA-OXFORD']['id'],
            'name': product_map['CAMISA-OXFORD']['name'],
            'product_qty': 150,
            'price_unit': product_map['CAMISA-OXFORD']['standard_price'],
            'date_planned': date_5_days_ago
        }),
        (0, 0, {
            'product_id': product_map['PANTALON-CHINO']['id'],
            'name': product_map['PANTALON-CHINO']['name'],
            'product_qty': 100,
            'price_unit': product_map['PANTALON-CHINO']['standard_price'],
            'date_planned': date_5_days_ago
        })
    ]
    po_id_5d = client.create('purchase.order', {
        'partner_id': supplier_id,
        'picking_type_id': picking_type_incoming,
        'date_order': date_5_days_ago,
        'order_line': po_lines_5d
    })
    client.execute('purchase.order', 'button_confirm', [po_id_5d])
    pickings_5d = client.search_read('stock.picking', domain=[['purchase_id', '=', po_id_5d]], fields=['id'])
    if pickings_5d:
        validate_picking_with_date(client, pickings_5d[0]['id'], date_5_days_ago)

    # 4 Days Ago
    date_4_days_ago = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n📅 [Day -4: {date_4_days_ago}] - Internal Transfer and 2 Delivery Orders")
    # Transfer 100 polos and 50 camisas from WHC to WH
    picking_id_4d = client.create('stock.picking', {
        'picking_type_id': picking_type_internal,
        'location_id': loc_agr_id,
        'location_dest_id': loc_ati_id,
        'origin': 'Transferencia Histórica #1',
        'scheduled_date': date_4_days_ago
    })
    client.create('stock.move', {
        'picking_id': picking_id_4d,
        'product_id': product_map['POLO-PIQUE']['id'],
        'product_uom_qty': 100,
        'uom_id': product_map['POLO-PIQUE']['uom_id'],
        'location_id': loc_agr_id,
        'location_dest_id': loc_ati_id
    })
    client.create('stock.move', {
        'picking_id': picking_id_4d,
        'product_id': product_map['CAMISA-OXFORD']['id'],
        'product_uom_qty': 50,
        'uom_id': product_map['CAMISA-OXFORD']['uom_id'],
        'location_id': loc_agr_id,
        'location_dest_id': loc_ati_id
    })
    validate_picking_with_date(client, picking_id_4d, date_4_days_ago)
    
    # Delivery 1 to Client 1
    del_id_4d_1 = client.create('stock.picking', {
        'picking_type_id': picking_type_delivery,
        'partner_id': client_ids[0],
        'location_id': loc_ati_id,
        'location_dest_id': loc_customer_id,
        'origin': 'Despacho Histórico #1',
        'scheduled_date': date_4_days_ago
    })
    client.create('stock.move', {
        'picking_id': del_id_4d_1,
        'product_id': product_map['POLO-PIQUE']['id'],
        'product_uom_qty': 15,
        'uom_id': product_map['POLO-PIQUE']['uom_id'],
        'location_id': loc_ati_id,
        'location_dest_id': loc_customer_id
    })
    validate_picking_with_date(client, del_id_4d_1, date_4_days_ago)

    # Delivery 2 to Client 2
    del_id_4d_2 = client.create('stock.picking', {
        'picking_type_id': picking_type_delivery,
        'partner_id': client_ids[1],
        'location_id': loc_ati_id,
        'location_dest_id': loc_customer_id,
        'origin': 'Despacho Histórico #2',
        'scheduled_date': date_4_days_ago
    })
    client.create('stock.move', {
        'picking_id': del_id_4d_2,
        'product_id': product_map['CAMISA-OXFORD']['id'],
        'product_uom_qty': 10,
        'uom_id': product_map['CAMISA-OXFORD']['uom_id'],
        'location_id': loc_ati_id,
        'location_dest_id': loc_customer_id
    })
    validate_picking_with_date(client, del_id_4d_2, date_4_days_ago)

    # 3 Days Ago
    date_3_days_ago = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n📅 [Day -3: {date_3_days_ago}] - Purchase Order #2 (Casacas, Poleras) & Internal Transfer #2")
    po_lines_3d = [
        (0, 0, {
            'product_id': product_map['CASACA-CORTAVIENTO']['id'],
            'name': product_map['CASACA-CORTAVIENTO']['name'],
            'product_qty': 150,
            'price_unit': product_map['CASACA-CORTAVIENTO']['standard_price'],
            'date_planned': date_3_days_ago
        }),
        (0, 0, {
            'product_id': product_map['POLERA-CAPUCHA']['id'],
            'name': product_map['POLERA-CAPUCHA']['name'],
            'product_qty': 200,
            'price_unit': product_map['POLERA-CAPUCHA']['standard_price'],
            'date_planned': date_3_days_ago
        })
    ]
    po_id_3d = client.create('purchase.order', {
        'partner_id': supplier_id,
        'picking_type_id': picking_type_incoming,
        'date_order': date_3_days_ago,
        'order_line': po_lines_3d
    })
    client.execute('purchase.order', 'button_confirm', [po_id_3d])
    pickings_3d = client.search_read('stock.picking', domain=[['purchase_id', '=', po_id_3d]], fields=['id'])
    if pickings_3d:
        validate_picking_with_date(client, pickings_3d[0]['id'], date_3_days_ago)
        
    # Transfer 60 pantalones and 40 casacas to WH
    picking_id_3d = client.create('stock.picking', {
        'picking_type_id': picking_type_internal,
        'location_id': loc_agr_id,
        'location_dest_id': loc_ati_id,
        'origin': 'Transferencia Histórica #2',
        'scheduled_date': date_3_days_ago
    })
    client.create('stock.move', {
        'picking_id': picking_id_3d,
        'product_id': product_map['PANTALON-CHINO']['id'],
        'product_uom_qty': 60,
        'uom_id': product_map['PANTALON-CHINO']['uom_id'],
        'location_id': loc_agr_id,
        'location_dest_id': loc_ati_id
    })
    client.create('stock.move', {
        'picking_id': picking_id_3d,
        'product_id': product_map['CASACA-CORTAVIENTO']['id'],
        'product_uom_qty': 40,
        'uom_id': product_map['CASACA-CORTAVIENTO']['uom_id'],
        'location_id': loc_agr_id,
        'location_dest_id': loc_ati_id
    })
    validate_picking_with_date(client, picking_id_3d, date_3_days_ago)

    # 2 Days Ago
    date_2_days_ago = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n📅 [Day -2: {date_2_days_ago}] - Delivery Order #3 & Internal Transfer #3")
    # Delivery 3 to Client 3
    del_id_2d = client.create('stock.picking', {
        'picking_type_id': picking_type_delivery,
        'partner_id': client_ids[2],
        'location_id': loc_ati_id,
        'location_dest_id': loc_customer_id,
        'origin': 'Despacho Histórico #3',
        'scheduled_date': date_2_days_ago
    })
    client.create('stock.move', {
        'picking_id': del_id_2d,
        'product_id': product_map['PANTALON-CHINO']['id'],
        'product_uom_qty': 12,
        'uom_id': product_map['PANTALON-CHINO']['uom_id'],
        'location_id': loc_ati_id,
        'location_dest_id': loc_customer_id
    })
    client.create('stock.move', {
        'picking_id': del_id_2d,
        'product_id': product_map['CASACA-CORTAVIENTO']['id'],
        'product_uom_qty': 8,
        'uom_id': product_map['CASACA-CORTAVIENTO']['uom_id'],
        'location_id': loc_ati_id,
        'location_dest_id': loc_customer_id
    })
    validate_picking_with_date(client, del_id_2d, date_2_days_ago)

    # Transfer 80 poleras and 50 more polos to WH
    picking_id_2d = client.create('stock.picking', {
        'picking_type_id': picking_type_internal,
        'location_id': loc_agr_id,
        'location_dest_id': loc_ati_id,
        'origin': 'Transferencia Histórica #3',
        'scheduled_date': date_2_days_ago
    })
    client.create('stock.move', {
        'picking_id': picking_id_2d,
        'product_id': product_map['POLERA-CAPUCHA']['id'],
        'product_uom_qty': 80,
        'uom_id': product_map['POLERA-CAPUCHA']['uom_id'],
        'location_id': loc_agr_id,
        'location_dest_id': loc_ati_id
    })
    client.create('stock.move', {
        'picking_id': picking_id_2d,
        'product_id': product_map['POLO-PIQUE']['id'],
        'product_uom_qty': 50,
        'uom_id': product_map['POLO-PIQUE']['uom_id'],
        'location_id': loc_agr_id,
        'location_dest_id': loc_ati_id
    })
    validate_picking_with_date(client, picking_id_2d, date_2_days_ago)

    # 1 Day Ago
    date_1_day_ago = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n📅 [Day -1: {date_1_day_ago}] - 2 Delivery Orders (Sales to Clients 4 and 5)")
    # Delivery 4 to Client 4
    del_id_1d_1 = client.create('stock.picking', {
        'picking_type_id': picking_type_delivery,
        'partner_id': client_ids[3],
        'location_id': loc_ati_id,
        'location_dest_id': loc_customer_id,
        'origin': 'Despacho Histórico #4',
        'scheduled_date': date_1_day_ago
    })
    client.create('stock.move', {
        'picking_id': del_id_1d_1,
        'product_id': product_map['POLERA-CAPUCHA']['id'],
        'product_uom_qty': 20,
        'uom_id': product_map['POLERA-CAPUCHA']['uom_id'],
        'location_id': loc_ati_id,
        'location_dest_id': loc_customer_id
    })
    validate_picking_with_date(client, del_id_1d_1, date_1_day_ago)

    # Delivery 5 to Client 5
    del_id_1d_2 = client.create('stock.picking', {
        'picking_type_id': picking_type_delivery,
        'partner_id': client_ids[4],
        'location_id': loc_ati_id,
        'location_dest_id': loc_customer_id,
        'origin': 'Despacho Histórico #5',
        'scheduled_date': date_1_day_ago
    })
    client.create('stock.move', {
        'picking_id': del_id_1d_2,
        'product_id': product_map['POLO-PIQUE']['id'],
        'product_uom_qty': 30,
        'uom_id': product_map['POLO-PIQUE']['uom_id'],
        'location_id': loc_ati_id,
        'location_dest_id': loc_customer_id
    })
    client.create('stock.move', {
        'picking_id': del_id_1d_2,
        'product_id': product_map['CAMISA-OXFORD']['id'],
        'product_uom_qty': 15,
        'uom_id': product_map['CAMISA-OXFORD']['uom_id'],
        'location_id': loc_ati_id,
        'location_dest_id': loc_customer_id
    })
    validate_picking_with_date(client, del_id_1d_2, date_1_day_ago)

    print("\n====================================================")
    print("🎉 HISTORICAL DATA GENERATED SUCCESSFULLY 🎉")
    print("====================================================")

if __name__ == '__main__':
    main()
