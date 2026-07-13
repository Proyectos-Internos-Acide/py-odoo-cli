import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    # Read Leo Cusi (ID: 13)
    leo = client.search_read('res.users', [['id', '=', 13]], ['name', 'group_ids', 'role'])[0]
    print(f"Leo Cusi original: {leo}")

    # Read Amaru Cusi (ID: 2)
    amaru = client.search_read('res.users', [['id', '=', 2]], ['name', 'group_ids', 'role'])[0]
    print(f"Amaru Cusi original: {amaru}")

    # Prepare values to write
    vals = {
        'group_ids': [(6, 0, leo['group_ids'])],
    }
    if 'role' in leo:
        vals['role'] = leo['role']

    print(f"Updating Amaru Cusi with values: {vals}")
    client.write('res.users', [2], vals)

    # Read Amaru Cusi again to verify
    amaru_updated = client.search_read('res.users', [['id', '=', 2]], ['name', 'group_ids', 'role'])[0]
    print(f"Amaru Cusi updated: {amaru_updated}")

if __name__ == '__main__':
    main()
