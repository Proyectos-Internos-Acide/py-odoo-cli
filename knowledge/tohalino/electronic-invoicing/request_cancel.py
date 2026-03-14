import sys
import os

# Ensure we can import odoo_cli from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from odoo_cli import OdooClient

def request_cancellation():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    invoice_id = 13
    print(f"Requesting EDI cancellation for Invoice ID: {invoice_id}")
    
    # In Odoo 16/17, the method to request EDI cancellation is often button_request_cancel
    try:
        # We call the method on the move
        res = client.execute("account.move", "button_request_cancel", [invoice_id])
        print(f"Cancellation requested. Result: {res}")
        
        # Check new state
        status = client.search_read("account.move", [["id", "=", invoice_id]], ["name", "edi_state", "edi_error_message"])[0]
        print(f"Invoice Name: {status['name']}")
        print(f"EDI State: {status['edi_state']}")
        print(f"EDI Error: {status['edi_error_message']}")

    except Exception as e:
        print(f"Error requesting cancellation: {e}")

if __name__ == "__main__":
    request_cancellation()
