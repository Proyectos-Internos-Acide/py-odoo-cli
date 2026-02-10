from odoo_cli import OdooClient
import json

try:
    client = OdooClient()
    client.connect()
    partners = client.search_read(
        'res.partner',
        domain=[['name', 'ilike', 'Jessica Huaman Arias']],
        fields=['name', 'vat', 'l10n_latam_identification_type_id', 'id']
    )
    print(json.dumps(partners, indent=2))
except Exception as e:
    print(f"Error: {e}")
