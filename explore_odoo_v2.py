import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    print("--- Searching for ALL Currencies ---")
    currencies = client.search_read('res.currency', domain=[], fields=['name', 'active'])
    for c in currencies:
        if c['name'] in ['USD', 'PEN']:
            print(f"Match: {c}")
    
    print("\n--- Checking CRM Module specifically ---")
    crm_mod = client.search_read('ir.module.module', domain=[['name', '=', 'crm']], fields=['name', 'state'])
    print(f"CRM Module: {crm_mod}")

    print("\n--- Searching for Models with 'lead' or 'opportunity' in name ---")
    models = client.search_read('ir.model', domain=['|', ['model', 'ilike', 'lead'], ['model', 'ilike', 'opp']], fields=['model', 'name'])
    for m in models:
        print(f"Model: {m['model']} ({m['name']})")

    print("\n--- Searching for Models with 'stage' in name ---")
    models = client.search_read('ir.model', domain=[['model', 'ilike', 'stage']], fields=['model', 'name'])
    for m in models:
        print(f"Model: {m['model']} ({m['name']})")

if __name__ == "__main__":
    main()
