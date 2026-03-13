import sys
import os

# Ensure we can import odoo_cli from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from odoo_cli import OdooClient

def mass_annul():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    # 1. Find all invoices that are not cancelled in Odoo
    # We look for posted invoices
    moves = client.search_read("account.move", [["state", "=", "posted"]], ["id", "name", "edi_state"])
    
    for move in moves:
        mid = move['id']
        name = move['name']
        edi_state = move['edi_state']
        
        print(f"Processing Move: {name} (ID: {mid}, EDI: {edi_state})")
        
        if edi_state == 'sent':
            print(f"  Requesting cancellation for {name}...")
            try:
                client.execute("account.move", "button_request_cancel", [mid])
                print("  Cancellation requested.")
            except Exception as e:
                print(f"  Error requesting cancellation for {name}: {e}")
        elif edi_state == 'to_cancel':
            print(f"  {name} is already in 'to_cancel' state. Will be processed soon.")
        else:
            print(f"  {name} is in state {edi_state}. No special EDI action taken.")

    # 2. Trigger EDI processing to send the Baja to SUNAT
    print("\nTriggering EDI processing (sending Bajas to SUNAT)...")
    try:
        # This is the standard method to push EDI documents
        # We call it on account.edi.document
        docs = client.search_read("account.edi.document", [["state", "in", ["to_send", "to_cancel"]]], ["id"])
        if docs:
            doc_ids = [d['id'] for d in docs]
            print(f"  Found {len(doc_ids)} EDI documents to process.")
            client.execute("account.edi.document", "_process_documents_web_services", doc_ids)
            print("  EDI processing completed.")
        else:
            print("  No EDI documents pending processing.")
    except Exception as e:
        print(f"  Error processing EDI documents: {e}")

    # 3. Final Verification
    print("\nFinal Status Check:")
    final_moves = client.search_read("account.move", [], ["id", "name", "state", "edi_state"])
    for m in final_moves:
        print(f"  {m['name']}: State={m['state']}, EDI={m['edi_state']}")

if __name__ == "__main__":
    mass_annul()
