#!/usr/bin/env python3
"""
Test script to verify warehouse, partner, and product creation, and a basic PO workflow.
"""

import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    print("=== TESTING CREATIONS ===")
    
    # 1. Create a Supplier Partner
    print("\n1. Creating a supplier...")
    supplier_vals = {
        'name': 'PROVEEDOR TEXTIL LIMA S.A.C.',
        'is_company': True,
        'supplier_rank': 1,
        'vat': '20609876543',
        'street': 'Av. Industrial 123, Ate, Lima',
        'phone': '987654321',
        'email': 'contacto@textillima.com'
    }
    supplier_id = client.create('res.partner', supplier_vals)
    print(f"   Supplier created with ID: {supplier_id}")
    
    # 2. Create a Product
    print("\n2. Creating a product...")
    product_vals = {
        'name': 'Polo de Algodón Pima - Test',
        'default_code': 'POLO-PIMA-TEST',
        'type': 'consu', # Goods
        'is_storable': True,
        'list_price': 45.0,
        'standard_price': 20.0,
    }
    # Create product template
    template_id = client.create('product.template', product_vals)
    print(f"   Product template created with ID: {template_id}")
    
    # Read product.product ID corresponding to the template
    products = client.search_read(
        'product.product',
        domain=[['product_tmpl_id', '=', template_id]],
        fields=['id', 'name']
    )
    product_id = products[0]['id']
    print(f"   Product variant (product.product) ID: {product_id}")
    
    # 3. Create Warehouses
    print("\n3. Creating Warehouses...")
    try:
        wh_grande_id = client.create('stock.warehouse', {
            'name': 'ALMACEN GRANDE',
            'code': 'AGR'
        })
        print(f"   ALMACEN GRANDE created with ID: {wh_grande_id}")
        
        # Read the warehouse locations
        wh_grande = client.search_read('stock.warehouse', domain=[['id', '=', wh_grande_id]], fields=['name', 'code', 'lot_stock_id'])
        print(f"   Warehouse details: {wh_grande[0]}")
        loc_grande_id = wh_grande[0]['lot_stock_id'][0]
        print(f"   Stock Location for AGR: {loc_grande_id} ({wh_grande[0]['lot_stock_id'][1]})")
    except Exception as e:
        print(f"   Error creating ALMACEN GRANDE: {e}")

    try:
        wh_tienda_id = client.create('stock.warehouse', {
            'name': 'ALMACEN TIENDA',
            'code': 'ATI'
        })
        print(f"   ALMACEN TIENDA created with ID: {wh_tienda_id}")
        
        wh_tienda = client.search_read('stock.warehouse', domain=[['id', '=', wh_tienda_id]], fields=['name', 'code', 'lot_stock_id'])
        print(f"   Warehouse details: {wh_tienda[0]}")
        loc_tienda_id = wh_tienda[0]['lot_stock_id'][0]
        print(f"   Stock Location for ATI: {loc_tienda_id} ({wh_tienda[0]['lot_stock_id'][1]})")
    except Exception as e:
        print(f"   Error creating ALMACEN TIENDA: {e}")

if __name__ == '__main__':
    main()
