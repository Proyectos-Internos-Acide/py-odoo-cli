import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    print("--- Connected to Odoo. Fetching installed modules... ---")
    modules = client.search_read(
        'ir.module.module',
        [('state', '=', 'installed')],
        fields=['name', 'shortdesc', 'author', 'latest_version']
    )
    # Sort modules by name
    modules.sort(key=lambda m: m['name'])
    
    print(f"Total installed modules: {len(modules)}")
    for m in modules:
        print(f"- {m['name']}: {m['shortdesc']} (v{m['latest_version']}) by {m['author']}")

if __name__ == '__main__':
    main()
