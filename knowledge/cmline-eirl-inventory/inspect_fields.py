import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient

def main():
    try:
        client = OdooClient()
        client.connect()
        
        print("🔍 Inspecting fields of 'l10n_latam.identification.type'...")
        
        # We'll read the first record to see what fields come back in a broad read
        # Or better, we can read the 'ir.model.fields' to allow us to see the schema
        
        fields = client.search_read(
            'ir.model.fields',
            [['model', '=', 'l10n_latam.identification.type']],
            ['name', 'field_description', 'ttype']
        )
        
        print(f"Found {len(fields)} fields:")
        for f in fields:
            print(f"- {f['name']} ({f['ttype']}): {f['field_description']}")

        # Also try to read one record to see real data
        print("\n🔍 Sample Data (first record):")
        records = client.search_read('l10n_latam.identification.type', [], limit=1)
        if records:
            print(records[0])
        else:
            print("No records found in l10n_latam.identification.type")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
