import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    print("=== Searching ir.model for WhatsApp related models ===")
    models = client.search_read(
        'ir.model',
        domain=['|', '|', ('model', 'like', 'wa'), ('model', 'like', 'whatsapp'), ('name', 'like', 'WhatsApp')],
        fields=['id', 'model', 'name']
    )
    for m in models:
        print(f"ID: {m['id']} | Model: '{m['model']}' | Name: '{m['name']}'")

    print("\n=== Checking views for WhatsApp models ===")
    if models:
        model_names = [m['model'] for m in models]
        views = client.search_read(
            'ir.ui.view',
            domain=[('model', 'in', model_names), ('type', '=', 'form')],
            fields=['id', 'name', 'model', 'type']
        )
        for v in views:
            print(f"View ID: {v['id']} | Name: '{v['name']}' | Model: '{v['model']}' | Type: '{v['type']}'")

if __name__ == '__main__':
    main()
