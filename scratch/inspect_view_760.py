#!/usr/bin/env python3
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    print("Conectado a Odoo.")

    v = client.search_read('ir.ui.view', [['id', '=', 1602]], ['name', 'model', 'type', 'inherit_id', 'arch_db'])
    if v:
        print("View 1602 details:")
        print(v[0]['name'])
        print(v[0]['arch_db'])
    else:
        print("View 760 not found!")

if __name__ == "__main__":
    main()
