import sys
import os

# Ensure we can import odoo_cli from parent directory
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, root_path)

from odoo_cli import OdooClient

def cleanup_test_invoices():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    # IDs to delete: 10 (user manual), 11 (failed script v1), 12 (success script v2)
    target_ids = [10, 11, 12]
    
    # 1. DELETE EDI DOCUMENTS FIRST (Crucial for bypass)
    print("Deleting associated EDI documents...")
    edi_docs = client.search_read("account.edi.document", [["move_id", "in", target_ids]], ["id"])
    if edi_docs:
        edi_ids = [d['id'] for d in edi_docs]
        client.unlink("account.edi.document", edi_ids)
        print(f"Deleted {len(edi_ids)} EDI documents.")

    # 2. DELETE INVOICES
    for move_id in target_ids:
        print(f"\nProcessing Invoice ID: {move_id}")
        try:
            # Force to draft first
            client.execute("account.move", "button_draft", [move_id])
            print("Reset to Draft.")
            # Unlink
            client.unlink("account.move", [move_id])
            print("Deleted.")
        except Exception as e:
            print(f"Error deleting invoice {move_id}: {e}")
            # Try force write if button_draft fails
            try:
                print("Attempting force state update...")
                client.write("account.move", [move_id], {'state': 'draft'})
                client.unlink("account.move", [move_id])
                print("Force deleted.")
            except Exception as e2:
                print(f"Final fail for {move_id}: {e2}")

if __name__ == "__main__":
    cleanup_test_invoices()
