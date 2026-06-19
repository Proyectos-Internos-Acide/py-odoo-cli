#!/usr/bin/env python3
"""
Script to generate and confirm multiple Sales Orders (sale.order) for Atlas.
"""

import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    print("==============================================")
    print("🚀 GENERATING SALES ORDERS FOR ATLAS 🚀")
    print("==============================================")
    
    # Check if sale.order exists
    models = client.search_read('ir.model', domain=[['model', '=', 'sale.order']], fields=['model', 'name'])
    if not models:
        print("❌ Error: sale.order model not found. Is the 'sale' module installed?")
        sys.exit(1)
        
    print(f"✅ Found model sale.order: {models[0]['name']}")
    
    # Get clients
    clients = client.search_read('res.partner', domain=[['customer_rank', '>', 0]], fields=['id', 'name'])
    client_ids = [c['id'] for c in clients]
    if len(client_ids) < 5:
        print("❌ Error: Less than 5 clients found. Run generate_all_data.py first.")
        sys.exit(1)
        
    # Get products
    products = client.search_read(
        'product.product',
        domain=[['default_code', 'in', ['POLO-PIQUE', 'CAMISA-OXFORD', 'PANTALON-CHINO', 'CASACA-CORTAVIENTO', 'POLERA-CAPUCHA']]],
        fields=['id', 'name', 'default_code', 'list_price']
    )
    product_map = {}
    for p in products:
        product_map[p['default_code']] = {
            'id': p['id'],
            'name': p['name'],
            'list_price': p['list_price']
        }
        
    # Sales orders data (Quotations to create)
    sales_orders_data = [
        # Sale 1: Juan Carlos Quispe - Large order of Polos & Camisas
        {
            'partner_id': client_ids[0],
            'warehouse_id': 1, # Almacén Tienda
            'date_order': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'lines': [
                (product_map['POLO-PIQUE']['id'], 50, product_map['POLO-PIQUE']['list_price']),
                (product_map['CAMISA-OXFORD']['id'], 20, product_map['CAMISA-OXFORD']['list_price'])
            ]
        },
        # Sale 2: Ana María Condori - Order of Pantalones & Casacas
        {
            'partner_id': client_ids[1],
            'warehouse_id': 1,
            'date_order': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'lines': [
                (product_map['PANTALON-CHINO']['id'], 15, product_map['PANTALON-CHINO']['list_price']),
                (product_map['CASACA-CORTAVIENTO']['id'], 10, product_map['CASACA-CORTAVIENTO']['list_price'])
            ]
        },
        # Sale 3: Carlos Alberto Sánchez - Large corporate order of Poleras
        {
            'partner_id': client_ids[2],
            'warehouse_id': 1,
            'date_order': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'lines': [
                (product_map['POLERA-CAPUCHA']['id'], 40, product_map['POLERA-CAPUCHA']['list_price']),
                (product_map['POLO-PIQUE']['id'], 30, product_map['POLO-PIQUE']['list_price'])
            ]
        },
        # Sale 4: Patricia Fiorella Torres - Mixed order
        {
            'partner_id': client_ids[3],
            'warehouse_id': 1,
            'date_order': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'lines': [
                (product_map['CAMISA-OXFORD']['id'], 12, product_map['CAMISA-OXFORD']['list_price']),
                (product_map['PANTALON-CHINO']['id'], 8, product_map['PANTALON-CHINO']['list_price']),
                (product_map['POLERA-CAPUCHA']['id'], 10, product_map['POLERA-CAPUCHA']['list_price'])
            ]
        }
    ]
    
    # Check if warehouse_id is in fields
    sale_fields = client.execute('sale.order', 'fields_get', [], {})
    has_warehouse = 'warehouse_id' in sale_fields
    print(f"ℹ️ Model sale.order has warehouse_id field: {has_warehouse}")

    # Create and confirm
    for idx, so_data in enumerate(sales_orders_data, 1):
        print(f"Creating Sales Order #{idx}...")
        order_lines = []
        for prod_id, qty, price in so_data['lines']:
            # Find product name
            pname = [p['name'] for p in products if p['id'] == prod_id][0]
            order_lines.append((0, 0, {
                'product_id': prod_id,
                'product_uom_qty': qty,
                'price_unit': price,
                'name': pname
            }))
            
        create_vals = {
            'partner_id': so_data['partner_id'],
            'date_order': so_data['date_order'],
            'order_line': order_lines
        }
        if has_warehouse:
            create_vals['warehouse_id'] = so_data['warehouse_id']

        so_id = client.create('sale.order', create_vals)
        print(f"  Quotation created with ID: {so_id}")
        
        # Confirm quotation to make it a Sales Order
        print(f"  Confirming Sales Order {so_id}...")
        client.execute('sale.order', 'action_confirm', [so_id])
        print(f"  ✅ Sales Order {so_id} confirmed.")

    print("\n==============================================")
    print("🎉 ALL SALES ORDERS GENERATED SUCCESSFULLY 🎉")
    print("==============================================")

if __name__ == '__main__':
    main()
