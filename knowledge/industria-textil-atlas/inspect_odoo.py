#!/usr/bin/env python3
"""
Inspect Odoo data for Industria Textil Atlas E.I.R.L.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    print("=== INSPECTING ODOO INSTANCE ===")
    
    # 1. Modules
    print("\n--- Checking installed modules (sale, purchase, stock, mrp) ---")
    modules = client.search_read(
        'ir.module.module',
        domain=[['name', 'in', ['sale', 'purchase', 'stock', 'mrp']]],
        fields=['name', 'state']
    )
    for m in modules:
        print(f"  Module {m['name']}: {m['state']}")
        
    # 2. Warehouses
    print("\n--- Current Warehouses ---")
    try:
        warehouses = client.search_read(
            'stock.warehouse',
            domain=[],
            fields=['name', 'code', 'lot_stock_id', 'view_location_id']
        )
        for w in warehouses:
            print(f"  Warehouse: {w['name']} [{w['code']}] (Stock Location ID: {w['lot_stock_id']}, View Location ID: {w['view_location_id']})")
    except Exception as e:
        print(f"  Error reading warehouses: {e}")

    # 3. Locations
    print("\n--- Current Locations (top 20) ---")
    try:
        locations = client.search_read(
            'stock.location',
            domain=[['usage', '=', 'internal']],
            fields=['complete_name', 'usage', 'location_id'],
            limit=20
        )
        for l in locations:
            print(f"  Location: {l['complete_name']} (ID: {l['id']})")
    except Exception as e:
        print(f"  Error reading locations: {e}")

    # 4. Products
    print("\n--- Current Products (top 10) ---")
    try:
        products = client.search_read(
            'product.product',
            domain=[],
            fields=['name', 'default_code', 'lst_price', 'qty_available', 'type'],
            limit=10
        )
        for p in products:
            print(f"  Product: {p['name']} [{p.get('default_code')}] - Price: {p['lst_price']} - Qty: {p.get('qty_available')} - Type: {p['type']}")
    except Exception as e:
        print(f"  Error reading products: {e}")

    # 5. Partners (Customers and Suppliers)
    print("\n--- Current Partners (top 10) ---")
    try:
        partners = client.search_read(
            'res.partner',
            domain=[],
            fields=['name', 'is_company', 'customer_rank', 'supplier_rank', 'phone', 'vat'],
            limit=10
        )
        for pt in partners:
            print(f"  Partner: {pt['name']} - Company: {pt['is_company']} - Cust Rank: {pt.get('customer_rank')} - Supp Rank: {pt.get('supplier_rank')} - VAT: {pt.get('vat')}")
    except Exception as e:
        print(f"  Error reading partners: {e}")

if __name__ == '__main__':
    main()
