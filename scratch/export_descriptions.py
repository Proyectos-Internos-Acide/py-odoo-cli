import sys
import os
import json
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    templates = client.search_read('product.template', [], ['id', 'name', 'description_sale'])
    data = {}
    for t in templates:
        data[t['name']] = t.get('description_sale') or ""
    with open('scratch/descriptions.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Exported to scratch/descriptions.json")

if __name__ == "__main__":
    main()
