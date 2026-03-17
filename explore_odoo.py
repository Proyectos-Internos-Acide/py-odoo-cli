import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    print("--- Searching for USD Currency ---")
    currencies = client.search_read('res.currency', domain=[], fields=['name', 'symbol', 'active'])
    usd = [c for c in currencies if 'USD' in c['name'] or '$' in c['symbol']]
    if usd:
        for u in usd:
            print(f"Found: {u}")
    else:
        print("USD not found in first set. Listing all active currencies:")
        active_curr = [c for c in currencies if c.get('active')]
        for c in active_curr:
            print(f"Active: {c}")

    print("\n--- Searching for CRM Models ---")
    models = client.search_read('ir.model', domain=[['model', 'ilike', 'crm']], fields=['model', 'name'])
    for m in models:
        print(f"Model: {m['model']} ({m['name']})")
        
    print("\n--- Checking for MRP ---")
    mrp = client.search_read('ir.module.module', domain=[['name', '=', 'mrp']], fields=['name', 'state'])
    print(f"MRP state: {mrp}")

if __name__ == "__main__":
    main()
