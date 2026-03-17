import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    # Test a simple create
    print("Testing simple create on crm.tag...")
    try:
        tag_id = client.execute('crm.tag', 'create', {'name': 'Test Debug Tag'})
        print(f"Success: {tag_id}")
    except Exception as e:
        print(f"Error on crm.tag create: {e}")

    # Test the wizard call that failed
    print("\nTesting sale.advance.payment.inv create...")
    try:
        # Usar un ID de SO existente (vimos que era 1)
        so_id = 1 
        wizard_id = client.execute('sale.advance.payment.inv', 'create', {
            'sale_order_ids': [(6, 0, [so_id])],
            'advance_payment_method': 'delivered',
        })
        print(f"Success: {wizard_id}")
    except Exception as e:
        print(f"Error on wizard create: {e}")

if __name__ == "__main__":
    main()
