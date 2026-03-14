import sys
import os

# Ensure we can import odoo_cli from parent directory
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, root_path)

from odoo_cli import OdooClient

def force_edi_processing():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    invoice_id = 13
    print(f"Forcing EDI processing for Invoice ID: {invoice_id}")
    
    # Try the standard EDI process method
    try:
        client.execute("account.move", "action_process_edi_web_services", [invoice_id])
        print("EDI Processing triggered.")
    except Exception as e:
        print(f"Error triggering EDI: {e}")

    # Check status again
    import time
    time.sleep(3)
    status = client.search_read("account.move", [["id", "=", invoice_id]], ["name", "edi_state", "edi_error_message"])[0]
    print(f"Invoice Name: {status['name']}")
    print(f"EDI State: {status['edi_state']}")
    print(f"EDI Error: {status['edi_error_message']}")

if __name__ == "__main__":
    force_edi_processing()
