import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    print("--- Fetching menu 127 (Invoicing) fields ---")
    menu = client.search_read(
        'ir.ui.menu',
        [('id', '=', 127)],
        limit=1
    )
    if menu:
        for k, v in menu[0].items():
            print(f"{k}: {v}")

if __name__ == '__main__':
    main()
