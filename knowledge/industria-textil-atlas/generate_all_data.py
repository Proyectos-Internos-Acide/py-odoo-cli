#!/usr/bin/env python3
"""
Comprehensive Data Generation Script for Industria Textil Atlas E.I.R.L.
Generates:
1. 5+ Peruvian Clients (res.partner)
2. 5 Textile Products (product.template / product.product)
3. Purchase Orders (purchase.order) for stock replenishment in ALMACEN GRANDE (AGR)
4. Confirm & validate receipts to populate AGR stock
5. Multiple Internal Transfers (stock.picking) between AGR and ALMACEN TIENDA (ATI)
6. Multiple Outgoing Delivery Orders (stock.picking) from ATI to Clients (representing Sales)
7. Reordering Rules (stock.warehouse.orderpoint) in ATI
"""

import sys
import os
import random
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient, OdooFaultError

def validate_picking(client, picking_id):
    """Confirm, assign, set quantity, and validate a stock picking."""
    try:
        # Read picking state
        picking = client.search_read('stock.picking', domain=[['id', '=', picking_id]], fields=['state', 'name'])
        if not picking:
            print(f"      ❌ Picking {picking_id} not found.")
            return False
            
        name = picking[0]['name']
        state = picking[0]['state']
        print(f"      Processing picking {name} (ID: {picking_id}) - current state: {state}")
        
        if state == 'draft':
            client.execute('stock.picking', 'action_confirm', [picking_id])
            state = client.search_read('stock.picking', domain=[['id', '=', picking_id]], fields=['state'])[0]['state']
            print(f"      State after confirm: {state}")
            
        if state in ['confirmed', 'waiting']:
            client.execute('stock.picking', 'action_assign', [picking_id])
            state = client.search_read('stock.picking', domain=[['id', '=', picking_id]], fields=['state'])[0]['state']
            print(f"      State after assign: {state}")
            
        # Read moves to update done quantity
        moves = client.search_read('stock.move', domain=[['picking_id', '=', picking_id]], fields=['id', 'product_uom_qty', 'state'])
        for m in moves:
            if m['state'] not in ['draft', 'cancel', 'done']:
                client.write('stock.move', [m['id']], {
                    'quantity': m['product_uom_qty'],
                    'picked': True
                })
                
        # Validate picking
        client.execute('stock.picking', 'button_validate', [picking_id])
        final_state = client.search_read('stock.picking', domain=[['id', '=', picking_id]], fields=['state'])[0]['state']
        print(f"      ✅ Picking {name} final state: {final_state}")
        return final_state == 'done'
    except Exception as e:
        print(f"      ❌ Error validating picking {picking_id}: {e}")
        return False

def main():
    client = OdooClient()
    client.connect()
    
    print("==============================================")
    print("🚀 STARTING BULK DATA GENERATION FOR ATLAS 🚀")
    print("==============================================")
    
    # Target real warehouses in the database
    supplier_id = 22 # PROVEEDOR TEXTIL LIMA S.A.C.
    wh_agr_id = 2    # Almacén casa
    wh_ati_id = 1    # Almacén Tienda
    loc_agr_id = 16  # WHC/Existencias
    loc_ati_id = 5   # WH/Stock
    loc_customer_id = 2 # Customers
    
    # Double check locations and warehouses dynamically
    try:
        whs = client.search_read('stock.warehouse', domain=[['id', 'in', [wh_agr_id, wh_ati_id]]], fields=['id', 'name', 'lot_stock_id'])
        print(f"Verified warehouses in DB: {whs}")
        for w in whs:
            if w['id'] == wh_agr_id:
                loc_agr_id = w['lot_stock_id'][0]
            elif w['id'] == wh_ati_id:
                loc_ati_id = w['lot_stock_id'][0]
    except Exception as e:
        print(f"⚠️ Error verifying warehouses: {e}. Using default IDs.")

    # 1. CREATE CLIENTS (5+ Peruvian clients)
    print("\n👥 Step 1: Creating Peruvian Clients...")
    clients_data = [
        {
            'name': 'Juan Carlos Quispe Mamani',
            'is_company': False,
            'customer_rank': 1,
            'supplier_rank': 0,
            'vat': '10453869811',
            'street': 'Av. Ejercito 720, Yanahuara, Arequipa',
            'phone': '958347219',
            'email': 'juan.quispe@gmail.com'
        },
        {
            'name': 'Ana María Condori Huamán',
            'is_company': False,
            'customer_rank': 1,
            'supplier_rank': 0,
            'vat': '09348123',
            'street': 'Calle Mercaderes 115, Arequipa',
            'phone': '945281934',
            'email': 'ana.condori@gmail.com'
        },
        {
            'name': 'Carlos Alberto Sánchez Rodríguez',
            'is_company': False,
            'customer_rank': 1,
            'supplier_rank': 0,
            'vat': '40128945',
            'street': 'Av. Larco 850, Miraflores, Lima',
            'phone': '981273645',
            'email': 'carlos.sanchez@gmail.com'
        },
        {
            'name': 'Patricia Fiorella Torres Chávez',
            'is_company': False,
            'customer_rank': 1,
            'supplier_rank': 0,
            'vat': '43928174',
            'street': 'Jr. Huallaga 450, Cercado de Lima',
            'phone': '992837465',
            'email': 'patricia.torres@gmail.com'
        },
        {
            'name': 'Víctor Raúl Haya de la Torre',
            'is_company': False,
            'customer_rank': 1,
            'supplier_rank': 0,
            'vat': '07281945',
            'street': 'Av. Venezuela 1400, Breña, Lima',
            'phone': '938475612',
            'email': 'victor.haya@gmail.com'
        }
    ]
    
    client_ids = []
    for c in clients_data:
        # Check if already exists to prevent duplicates
        existing = client.search_read('res.partner', domain=[['name', '=', c['name']]], fields=['id'])
        if existing:
            cid = existing[0]['id']
            print(f"   Client '{c['name']}' already exists with ID: {cid}")
        else:
            cid = client.create('res.partner', c)
            print(f"   Created client: {c['name']} (ID: {cid})")
        client_ids.append(cid)

    # 2. CREATE PRODUCTS (5 Textile garments)
    print("\n👕 Step 2: Creating Textile Products...")
    products_data = [
        {'name': 'Polo Camisero Piqué', 'default_code': 'POLO-PIQUE', 'type': 'consu', 'is_storable': True, 'list_price': 55.0, 'standard_price': 25.0},
        {'name': 'Camisa de Vestir Oxford', 'default_code': 'CAMISA-OXFORD', 'type': 'consu', 'is_storable': True, 'list_price': 85.0, 'standard_price': 38.0},
        {'name': 'Pantalón Chino Slim Fit', 'default_code': 'PANTALON-CHINO', 'type': 'consu', 'is_storable': True, 'list_price': 120.0, 'standard_price': 50.0},
        {'name': 'Casaca Cortaviento Térmica', 'default_code': 'CASACA-CORTAVIENTO', 'type': 'consu', 'is_storable': True, 'list_price': 150.0, 'standard_price': 65.0},
        {'name': 'Polera con Capucha Algodón', 'default_code': 'POLERA-CAPUCHA', 'type': 'consu', 'is_storable': True, 'list_price': 95.0, 'standard_price': 42.0}
    ]
    
    product_variant_ids = []
    product_map = {} # Maps product_id -> details
    for p in products_data:
        existing = client.search_read('product.template', domain=[['default_code', '=', p['default_code']]], fields=['id'])
        if existing:
            tmpl_id = existing[0]['id']
            print(f"   Product '{p['name']}' template already exists with ID: {tmpl_id}")
        else:
            tmpl_id = client.create('product.template', p)
            print(f"   Created product template: {p['name']} (ID: {tmpl_id})")
            
        # Get variant ID
        variants = client.search_read('product.product', domain=[['product_tmpl_id', '=', tmpl_id]], fields=['id', 'uom_id'])
        if variants:
            var_id = variants[0]['id']
            uom_id = variants[0]['uom_id'][0] if variants[0].get('uom_id') else 1
            product_variant_ids.append(var_id)
            product_map[var_id] = {
                'name': p['name'],
                'uom_id': uom_id,
                'list_price': p['list_price'],
                'standard_price': p['standard_price']
            }
            print(f"     Variant ID: {var_id}, UoM ID: {uom_id}")

    # 3. CREATE REORDERING RULES (Reglas de Abastecimiento) IN ALMACEN TIENDA (ATI)
    print("\n⚙️ Step 3: Creating Reordering Rules in ALMACEN TIENDA (ATI)...")
    for prod_id in product_variant_ids:
        # Check if reordering rule already exists
        existing_rule = client.search_read(
            'stock.warehouse.orderpoint',
            domain=[['product_id', '=', prod_id], ['warehouse_id', '=', wh_ati_id]],
            fields=['id']
        )
        if existing_rule:
            print(f"   Reordering rule for product ID {prod_id} in ATI already exists (ID: {existing_rule[0]['id']})")
        else:
            rule_id = client.create('stock.warehouse.orderpoint', {
                'product_id': prod_id,
                'warehouse_id': wh_ati_id,
                'location_id': loc_ati_id,
                'product_min_qty': 20.0,
                'product_max_qty': 150.0
            })
            print(f"   Created reordering rule for product '{product_map[prod_id]['name']}' (ID: {rule_id})")

    # 4. CREATE PURCHASE ORDERS (PO) TO REPLENISH ALMACEN GRANDE (AGR)
    print("\n📦 Step 4: Creating and Validating Purchase Orders (AGR Stock Replenishment)...")
    # Find incoming picking type (receipts) for ALMACEN GRANDE (AGR, ID 3)
    picking_types_agr = client.search_read(
        'stock.picking.type',
        domain=[['code', '=', 'incoming'], ['warehouse_id', '=', wh_agr_id]],
        fields=['id', 'name']
    )
    if not picking_types_agr:
        print("   ❌ Error: Receipt picking type for ALMACEN GRANDE not found!")
        sys.exit(1)
        
    picking_type_agr_receipt = picking_types_agr[0]['id']
    print(f"   Incoming Picking Type for AGR: {picking_type_agr_receipt} ({picking_types_agr[0]['name']})")
    
    # We will create 2 Purchase Orders to simulate multiple purchases on different dates
    purchases = [
        # Purchase 1: Large quantity of polo, camisa, pantalon
        [
            (product_variant_ids[0], 250), # 250 Polos
            (product_variant_ids[1], 150), # 150 Camisas
            (product_variant_ids[2], 100), # 100 Pantalones
        ],
        # Purchase 2: Large quantity of casaca, polera
        [
            (product_variant_ids[3], 120), # 120 Casacas
            (product_variant_ids[4], 180), # 180 Poleras
            (product_variant_ids[0], 100), # 100 extra Polos
        ]
    ]
    
    for idx, po_items in enumerate(purchases, 1):
        print(f"   Creating Purchase Order #{idx}...")
        po_lines = []
        for prod_id, qty in po_items:
            po_lines.append((0, 0, {
                'product_id': prod_id,
                'name': product_map[prod_id]['name'],
                'product_qty': qty,
                'price_unit': product_map[prod_id]['standard_price'],
                'date_planned': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
            }))
            
        po_id = client.create('purchase.order', {
            'partner_id': supplier_id,
            'picking_type_id': picking_type_agr_receipt,
            'date_order': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
            'order_line': po_lines
        })
        print(f"      PO created with ID: {po_id}")
        
        # Confirm Purchase Order
        print(f"      Confirming PO {po_id}...")
        client.execute('purchase.order', 'button_confirm', [po_id])
        
        # Find picking linked to this PO
        pickings = client.search_read(
            'stock.picking',
            domain=[['purchase_id', '=', po_id]],
            fields=['id', 'state']
        )
        if pickings:
            picking_id = pickings[0]['id']
            print(f"      Found Receipt Picking: {picking_id}")
            # Validate the receipt
            validate_picking(client, picking_id)
        else:
            print("      ⚠️ No picking found for Purchase Order!")

    # 5. CREATE INTERNAL TRANSFERS BETWEEN ALMACEN GRANDE (AGR) AND ALMACEN TIENDA (ATI)
    print("\n🔄 Step 5: Creating Internal Transfers from AGR to ATI...")
    # Find internal transfer picking type for ALMACEN GRANDE (AGR, ID 3)
    picking_types_agr_internal = client.search_read(
        'stock.picking.type',
        domain=[['code', '=', 'internal'], ['warehouse_id', '=', wh_agr_id]],
        fields=['id', 'name']
    )
    if not picking_types_agr_internal:
        print("   ❌ Error: Internal transfer picking type for ALMACEN GRANDE not found!")
        sys.exit(1)
        
    picking_type_agr_int = picking_types_agr_internal[0]['id']
    print(f"   Internal Transfer Picking Type for AGR: {picking_type_agr_int} ({picking_types_agr_internal[0]['name']})")
    
    # We will do 3 separate transfers of different products to simulate stock refills
    transfers = [
        # Transfer 1: Refill Polos and Camisas
        [
            (product_variant_ids[0], 80),  # 80 Polos
            (product_variant_ids[1], 40),  # 40 Camisas
        ],
        # Transfer 2: Refill Pantalones and Casacas
        [
            (product_variant_ids[2], 30),  # 30 Pantalones
            (product_variant_ids[3], 20),  # 20 Casacas
        ],
        # Transfer 3: Refill Poleras and more Polos
        [
            (product_variant_ids[4], 50),  # 50 Poleras
            (product_variant_ids[0], 40),  # 40 Polos
        ]
    ]
    
    for idx, trans_items in enumerate(transfers, 1):
        print(f"   Creating Internal Transfer #{idx}...")
        # Create picking
        picking_id = client.create('stock.picking', {
            'picking_type_id': picking_type_agr_int,
            'location_id': loc_agr_id,
            'location_dest_id': loc_ati_id,
            'origin': f'Simulación Reabastecimiento #{idx}'
        })
        
        # Create stock moves
        for prod_id, qty in trans_items:
            client.create('stock.move', {
                'picking_id': picking_id,
                'product_id': prod_id,
                'product_uom_qty': qty,
                'uom_id': product_map[prod_id]['uom_id'],
                'location_id': loc_agr_id,
                'location_dest_id': loc_ati_id
            })
            
        print(f"      Picking internal transfer created with ID: {picking_id}")
        validate_picking(client, picking_id)

    # 6. CREATE OUTGOING DELIVERY ORDERS FROM ALMACEN TIENDA (ATI) TO CLIENTS (Simulating Sales)
    print("\n🛍️ Step 6: Creating Delivery Orders (Sales Simulation from ATI)...")
    # Find delivery picking type for ALMACEN TIENDA (ATI, ID 4)
    picking_types_ati_delivery = client.search_read(
        'stock.picking.type',
        domain=[['code', '=', 'outgoing'], ['warehouse_id', '=', wh_ati_id], ['name', 'not ilike', 'pos'], ['name', 'not ilike', 'pdv']],
        fields=['id', 'name']
    )
    if not picking_types_ati_delivery:
        print("   ❌ Error: Delivery picking type for ALMACEN TIENDA not found!")
        sys.exit(1)
        
    picking_type_ati_del = picking_types_ati_delivery[0]['id']
    print(f"   Delivery Picking Type for ATI: {picking_type_ati_del} ({picking_types_ati_delivery[0]['name']})")
    
    # Create 5 delivery orders, one for each client
    # We will pick random products and random quantities (within transfer limit)
    sales = [
        # Client 1: Juan Carlos Quispe
        (client_ids[0], [
            (product_variant_ids[0], 5), # 5 Polos
            (product_variant_ids[1], 2)  # 2 Camisas
        ]),
        # Client 2: Ana Maria Condori
        (client_ids[1], [
            (product_variant_ids[1], 4), # 4 Camisas
            (product_variant_ids[4], 3)  # 3 Poleras
        ]),
        # Client 3: Carlos Alberto Sanchez
        (client_ids[2], [
            (product_variant_ids[2], 10), # 10 Pantalones
            (product_variant_ids[0], 8)   # 8 Polos
        ]),
        # Client 4: Patricia Fiorella Torres
        (client_ids[3], [
            (product_variant_ids[3], 2), # 2 Casacas
            (product_variant_ids[4], 5)  # 5 Poleras
        ]),
        # Client 5: Victor Raul Haya
        (client_ids[4], [
            (product_variant_ids[0], 12), # 12 Polos
            (product_variant_ids[1], 5),  # 5 Camisas
            (product_variant_ids[2], 4)   # 4 Pantalones
        ])
    ]
    
    for idx, (cid, sale_items) in enumerate(sales, 1):
        cname = client.search_read('res.partner', domain=[['id', '=', cid]], fields=['name'])[0]['name']
        print(f"   Creating Delivery Order #{idx} for Client '{cname}'...")
        
        # Create picking
        picking_id = client.create('stock.picking', {
            'picking_type_id': picking_type_ati_del,
            'partner_id': cid,
            'location_id': loc_ati_id,
            'location_dest_id': loc_customer_id,
            'origin': f'Venta Corporativa #{idx}'
        })
        
        # Create stock moves
        for prod_id, qty in sale_items:
            client.create('stock.move', {
                'picking_id': picking_id,
                'product_id': prod_id,
                'product_uom_qty': qty,
                'uom_id': product_map[prod_id]['uom_id'],
                'location_id': loc_ati_id,
                'location_dest_id': loc_customer_id
            })
            
        print(f"      Delivery picking created with ID: {picking_id}")
        validate_picking(client, picking_id)

    print("\n==============================================")
    print("🎉 ALL TEST DATA GENERATED SUCCESSFULLY 🎉")
    print("==============================================")

if __name__ == '__main__':
    main()
