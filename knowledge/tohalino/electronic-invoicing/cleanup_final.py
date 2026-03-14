import sys
import os

# Ensure we can import odoo_cli from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from odoo_cli import OdooClient

def final_cleanup():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    remaining_ids = [1, 2]
    
    # 1. Delete EDI documents first
    print("Checking for EDI documents...")
    edi_docs = client.search_read(
        "account.edi.document",
        domain=[["move_id", "in", remaining_ids]],
        fields=["id"]
    )
    if edi_docs:
        edi_ids = [d['id'] for d in edi_docs]
        print(f"Found {len(edi_ids)} EDI documents. Deleting...")
        try:
            client.unlink("account.edi.document", edi_ids)
            print("EDI documents deleted.")
        except Exception as e:
            print(f"Error deleting EDI docs: {e}")

    # 2. Delete Moves
    print("Deleting remaining moves...")
    try:
        client.unlink("account.move", remaining_ids)
        print("Moves 1 and 2 deleted successfully.")
    except Exception as e:
        print(f"Error deleting moves: {e}")

if __name__ == "__main__":
    final_cleanup()
