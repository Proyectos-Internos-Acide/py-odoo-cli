import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    print("=== Inspecting CRM Stages ===")
    stages = client.search_read('crm.stage', domain=[], fields=['id', 'name', 'sequence'], order='sequence asc')
    for s in stages:
        print(s)

    print("\n=== Checking ir.model for any existing wtk wizards ===")
    models = client.search_read('ir.model', domain=[('model', 'like', 'wtk')], fields=['id', 'model', 'name'])
    for m in models:
        print(m)

if __name__ == '__main__':
    main()
