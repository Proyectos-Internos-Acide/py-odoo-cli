#!/usr/bin/env python3
"""
Verification script to print the final stock levels and generated records.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    print("=== FINAL VERIFICATION REPORT ===")
    
    # 1. Check warehouses
    print("\n🏢 Warehouses:")
    whs = client.search_read('stock.warehouse', domain=[], fields=['name', 'code', 'lot_stock_id'])
    for w in whs:
        print(f"  - {w['name']} [{w['code']}] (Location ID: {w['lot_stock_id'][0]})")
        
    # 2. Check clients
    print("\n👥 Clients:")
    clients = client.search_read(
        'res.partner',
        domain=[['customer_rank', '>', 0]],
        fields=['name', 'vat', 'street', 'phone']
    )
    for c in clients:
        print(f"  - {c['name']} (VAT/DNI: {c.get('vat')} | Telf: {c.get('phone')} | Dir: {c.get('street')})")
        
    # 3. Check products and stock
    print("\n👕 Products and Stock Levels:")
    products = client.search_read(
        'product.product',
        domain=[['default_code', 'in', ['POLO-PIQUE', 'CAMISA-OXFORD', 'PANTALON-CHINO', 'CASACA-CORTAVIENTO', 'POLERA-CAPUCHA']]],
        fields=['name', 'default_code', 'qty_available']
    )
    for p in products:
        # Check stock by location
        quants = client.search_read(
            'stock.quant',
            domain=[['product_id', '=', p['id']], ['location_id.usage', '=', 'internal']],
            fields=['location_id', 'quantity']
        )
        print(f"  - {p['name']} [{p['default_code']}] (Total Stock: {p['qty_available']})")
        for q in quants:
            print(f"      📍 {q['location_id'][1]}: {q['quantity']} units")
            
    # 4. Check reordering rules for our products
    print("\n⚙️ Reordering Rules (WH) for our products:")
    rules = client.search_read(
        'stock.warehouse.orderpoint',
        domain=[['warehouse_id', '=', 1], ['product_id', 'in', [p['id'] for p in products]]],
        fields=['product_id', 'location_id', 'product_min_qty', 'product_max_qty']
    )
    for r in rules:
        print(f"  - Product: {r['product_id'][1]} | Location: {r['location_id'][1]} | Min: {r['product_min_qty']} | Max: {r['product_max_qty']}")

if __name__ == '__main__':
    main()
