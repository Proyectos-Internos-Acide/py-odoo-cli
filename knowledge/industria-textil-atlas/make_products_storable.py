#!/usr/bin/env python3
"""
Script to update existing product templates to be storable (is_storable = True).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    codes = ['POLO-PIMA-TEST', 'POLO-PIQUE', 'CAMISA-OXFORD', 'PANTALON-CHINO', 'CASACA-CORTAVIENTO', 'POLERA-CAPUCHA']
    print(f"Finding templates for codes: {codes}")
    
    templates = client.search_read(
        'product.template',
        domain=[['default_code', 'in', codes]],
        fields=['id', 'name', 'default_code', 'is_storable']
    )
    
    for t in templates:
        print(f"Updating template '{t['name']}' (ID: {t['id']}) - is_storable currently: {t['is_storable']}")
        client.write('product.template', [t['id']], {'is_storable': True})
        print(f"  ✅ Updated successfully.")

if __name__ == '__main__':
    main()
