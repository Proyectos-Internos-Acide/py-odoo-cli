import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    # Test action_confirm
    print("\nTesting sale.order action_confirm...")
    try:
        # Use existing SO 1
        res = client.execute('sale.order', 'action_confirm', [1])
        print(f"Success: Result = {res}")
    except Exception as e:
        print(f"Error on action_confirm: {e}")

if __name__ == "__main__":
    main()
