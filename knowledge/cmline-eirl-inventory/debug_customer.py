import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient
import json

try:
    client = OdooClient()
    client.connect()
    
    # Check if there are other parter records with same name/vat that might be confused
    partners = client.search_read(
        'res.partner',
        domain=[['vat', '=', '10425620687']],
        fields=[
            'name', 
            'vat', 
            'l10n_latam_identification_type_id', 
            'country_id', 
            'l10n_pe_district',
            'street'
        ]
    )
    print(f"All partners with this VAT: {json.dumps(partners, indent=2)}")

except Exception as e:
    print(f"Error: {e}")
