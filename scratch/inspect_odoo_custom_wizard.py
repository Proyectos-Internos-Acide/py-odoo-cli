import sys
import os
import json
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    print("=== Searching ir.model for custom models, transient models (wizards), or quote/sale models ===")
    
    # 1. Fetch transient models (wizards)
    transient_models = client.search_read(
        'ir.model',
        domain=[('transient', '=', True)],
        fields=['id', 'model', 'name', 'state']
    )
    print(f"\nFound {len(transient_models)} transient (wizard) models.")
    
    # Filter interesting ones (non-standard Odoo standard system wizards or custom ones)
    interesting_keywords = ['sale', 'quote', 'quotation', 'custom', 'wayki', 'trek', 'x_', 'tour', 'booking', 'itinerary', 'calc']
    filtered_wizards = [
        m for m in transient_models 
        if any(kw in m['model'].lower() or kw in (m['name'] or '').lower() for kw in interesting_keywords)
    ]
    print("\n--- Transient models matching keywords ---")
    for m in filtered_wizards:
        print(f"ID: {m['id']} | Model: {m['model']} | Name: {m['name']} | State: {m['state']}")

    # 2. Fetch all custom models (state = 'manual' or starting with 'x_')
    custom_models = client.search_read(
        'ir.model',
        domain=['|', ('state', '=', 'manual'), ('model', '=like', 'x_%')],
        fields=['id', 'model', 'name', 'state', 'transient']
    )
    print(f"\n--- Custom models (state='manual' or x_%) ---")
    for m in custom_models:
        print(f"ID: {m['id']} | Model: {m['model']} | Name: {m['name']} | Transient: {m['transient']}")

    # 3. Search for models containing 'sale', 'quote', 'tour', 'itinerary', 'wayki'
    sale_quote_models = client.search_read(
        'ir.model',
        domain=['|', '|', '|', ('model', 'ilike', 'quote'), ('model', 'ilike', 'tour'), ('model', 'ilike', 'itinerary'), ('model', 'ilike', 'wayki')],
        fields=['id', 'model', 'name', 'state', 'transient']
    )
    print(f"\n--- Models related to quote, tour, itinerary, wayki ---")
    for m in sale_quote_models:
        print(f"ID: {m['id']} | Model: {m['model']} | Name: {m['name']} | Transient: {m['transient']}")

if __name__ == '__main__':
    main()
