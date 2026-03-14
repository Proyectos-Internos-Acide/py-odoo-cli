import sys
import os

# Ensure we can import odoo_cli from parent directory
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, root_path)

from odoo_cli import OdooClient

def create_valid_test_invoice():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    # Use existing test partner (ID 9) or create a new one
    partner_id = 9
    
    # 1. Product
    product_id = 1 # Lapiz
    
    # 2. Correct Tax (ID 5: VAT 18%)
    tax_id = 5

    # 3. Create Invoice (ID 12)
    journal = client.search_read("account.journal", [["type", "=", "sale"]], ["id"])[0]
    
    invoice_vals = {
        'move_type': 'out_invoice',
        'partner_id': partner_id,
        'journal_id': journal['id'],
        'invoice_date': '2026-02-12',
        'invoice_line_ids': [
            (0, 0, {
                'product_id': product_id,
                'name': 'Prueba Final Automatizada (IGV 18%)',
                'quantity': 1,
                'price_unit': 50.0,
                'tax_ids': [(6, 0, [tax_id])]
            })
        ]
    }
    
    invoice_id = client.create("account.move", invoice_vals)
    print(f"Invoice Created (ID: {invoice_id})")

    # 4. Post
    client.execute("account.move", "action_post", [invoice_id])
    print("Invoice Posted.")

    # 5. Process EDI
    print("Processing EDI...")
    try:
        # We ignore return because XML-RPC marshals None as error
        client.execute("account.move", "action_process_edi_web_services", [invoice_id])
    except Exception:
        pass
    
    # Wait and Check
    import time
    time.sleep(5)
    status = client.search_read("account.move", [["id", "=", invoice_id]], ["name", "edi_state", "edi_error_message"])[0]
    print(f"Invoice Name: {status['name']}")
    print(f"EDI State: {status['edi_state']}")
    print(f"EDI Error: {status['edi_error_message']}")

if __name__ == "__main__":
    create_valid_test_invoice()
