import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    try:
        client = OdooClient()
        client.connect()
        
        # Customer Data matches SUNAT exactly
        customer_data = {
            'name': 'HUAMAN ARIAS JESSICA',
            'vat': '10425620687', # RUC number
            'email': 'contactorogeris@gmail.com',
            'street': 'Arequipa', # Placeholder address as specific one wasn't provided but is required for invoice printing often
            'country_id': client.search_read('res.country', [['code', '=', 'PE']], ['id'])[0]['id'], # Ensure Peru
        }
        
        print(f"🔍 Searching for RUC Identification Type...")
        # Find the correct identification type ID for RUC (Code 6)
        # We look for l10n_latam.identification.type with code '6' (standard for RUC in Peru localization)
        # Note: In some DBs it might be 'l10n_pe.identification.type', but usually it's standard l10n_latam now.
        # We'll search by code '6' which is the SUNAT code for RUC.
        
        identity_types = client.search_read(
            'l10n_latam.identification.type', 
            [['code', '=', '6']], 
            ['id', 'name']
        )
        
        if not identity_types:
            print("❌ Critical Error: Could not find Identification Type for RUC (Code 6).")
            print("   Please check your localization installation.")
            return
            
        ruc_type_id = identity_types[0]['id']
        print(f"✅ Found RUC Type ID: {ruc_type_id} ({identity_types[0]['name']})")
        
        customer_data['l10n_latam_identification_type_id'] = ruc_type_id
        
        print(f"🚀 Creating customer: {customer_data['name']}...")
        
        # Check if exists first (to avoid duplicates if run multiple times)
        existing = client.search_read(
            'res.partner',
            [['vat', '=', customer_data['vat']]],
            ['id', 'name']
        )
        
        if existing:
            print(f"⚠️  Customer already exists with ID {existing[0]['id']}. Updating...")
            client.write('res.partner', [existing[0]['id']], customer_data)
            print(f"✅ Customer {existing[0]['id']} updated successfully.")
        else:
            new_id = client.create('res.partner', customer_data)
            print(f"✅ Customer created successfully with ID: {new_id}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
