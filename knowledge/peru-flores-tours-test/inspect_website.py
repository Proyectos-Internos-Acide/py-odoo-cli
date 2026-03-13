#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from odoo_cli import OdooClient

def main():
    try:
        client = OdooClient()
        client.connect()
        
        print("--- Websites ---")
        websites = client.search_read('website', [], ['id', 'name', 'domain'])
        for w in websites:
            print(f"ID: {w['id']} - Name: {w['name']} - Domain: {w.get('domain')}")

        print("\n--- Pages ---")
        pages = client.search_read('website.page', [], ['id', 'name', 'url', 'view_id', 'website_id'])
        for p in pages:
            print(f"ID: {p['id']} - Name: {p['name']} - URL: {p['url']} - View ID: {p['view_id']} - Website ID: {p.get('website_id')}")
            
        # Try to find the homepage view specifically for Website ID 1
        homepage = next((p for p in pages if p['url'] == '/' and (not p.get('website_id') or p.get('website_id')[0] == 1)), None)
        if homepage:
            view_id = homepage['view_id'][0]
            print(f"\n--- Homepage View (ID: {view_id}) ---")
            view = client.search_read('ir.ui.view', [['id', '=', view_id]], ['name', 'key', 'arch_db', 'arch_base'])
            if view:
                print(f"Name: {view[0]['name']}")
                print(f"Key: {view[0]['key']}")
                content = view[0].get('arch_db') or view[0].get('arch_base')
                print("Arch Content:")
                print(content)
        
        print("\n--- Recent Attachments (Images) ---")
        attachments = client.search_read('ir.attachment', [['mimetype', 'ilike', 'image']], ['id', 'name', 'mimetype'], limit=20)
        for a in attachments:
            print(f"ID: {a['id']} - Name: {a['name']} - Type: {a['mimetype']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
