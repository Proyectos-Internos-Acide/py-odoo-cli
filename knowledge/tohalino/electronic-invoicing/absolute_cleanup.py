import sys
import os

# Ensure we can import odoo_cli from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from odoo_cli import OdooClient

def full_cleanup():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    # 1. Target Move IDs
    move_ids = [13, 14]
    print(f"Targeting moves for deletion: {move_ids}")

    # 2. Cleanup EDI Documents
    edi_docs = client.search_read("account.edi.document", [["move_id", "in", move_ids]], ["id"])
    if edi_docs:
        edi_ids = [d['id'] for d in edi_docs]
        print(f"  Deleting EDI Documents: {edi_ids}")
        client.execute("account.edi.document", "unlink", edi_ids)
    
    # 3. Cleanup Attachments
    attachments = client.search_read("ir.attachment", [
        ["res_model", "=", "account.move"], 
        ["res_id", "in", move_ids]
    ], ["id"])
    if attachments:
        attach_ids = [a['id'] for a in attachments]
        print(f"  Deleting Attachments: {attach_ids}")
        client.execute("ir.attachment", "unlink", attach_ids)

    # 4. Cleanup Mail Messages
    messages = client.search_read("mail.message", [
        ["model", "=", "account.move"],
        ["res_id", "in", move_ids]
    ], ["id"])
    if messages:
        msg_ids = [m['id'] for m in messages]
        print(f"  Deleting Mail Messages: {msg_ids}")
        client.execute("mail.message", "unlink", msg_ids)

    # 5. Cleanup Invoices (Moves)
    # Note: In Odoo, you might need to move them to draft before deleting if they are posted
    print(f"  Moving invoices to draft to allow deletion...")
    try:
        client.execute("account.move", "button_draft", move_ids)
    except Exception as e:
        print(f"  Note during button_draft: {e}")

    print(f"  Deleting account.move records...")
    client.execute("account.move", "unlink", move_ids)
    print("Cleanup completed.")

if __name__ == "__main__":
    full_cleanup()
