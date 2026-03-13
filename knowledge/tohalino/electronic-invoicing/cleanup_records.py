import sys
import os
import time

# Ensure we can import odoo_cli from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from odoo_cli import OdooClient

def cleanup_records():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    invoice_ids = [1, 2, 3]
    move_ids_to_process = set(invoice_ids)
    
    # Find related credit notes
    credit_notes = client.search_read(
        "account.move",
        domain=[["reversed_entry_id", "in", invoice_ids]],
        fields=["id", "name"]
    )
    for cn in credit_notes:
        print(f"Found related Credit Note: {cn['name']} (ID: {cn['id']})")
        move_ids_to_process.add(cn['id'])

    sorted_ids = sorted(list(move_ids_to_process), reverse=True)
    print(f"Targeting moves: {sorted_ids}")

    # Step 1: Unreconcile everything first
    # We retrieve all lines for these moves
    print("\n--- Unreconciling ---")
    all_lines = client.search_read(
        "account.move.line",
        domain=[["move_id", "in", sorted_ids]],
        fields=["id"]
    )
    all_line_ids = [l['id'] for l in all_lines]
    
    # Find partial reconciliations involving these lines
    partials = client.search_read(
        "account.partial.reconcile",
        domain=["|", ["debit_move_id", "in", all_line_ids], ["credit_move_id", "in", all_line_ids]],
        fields=["id"]
    )
    if partials:
        partial_ids = [p['id'] for p in partials]
        print(f"Found {len(partial_ids)} partial reconciliations to delete.")
        try:
            client.unlink("account.partial.reconcile", partial_ids)
            print("Unreconciled successfully.")
        except Exception as e:
            print(f"Error unreconciling: {e}")

    # Step 2: Delete/Cancel Moves
    print("\n--- Deleting Moves ---")
    for move_id in sorted_ids:
        print(f"\nProcessing Move ID: {move_id}")
        
        try:
            moves = client.search_read("account.move", [["id", "=", move_id]], ["name", "state", "payment_state"])
            if not moves:
                print("Record not found.")
                continue
            
            move = moves[0]
            print(f"Current State: {move['state']}")

            if move['state'] == 'draft':
                 print("Deleting draft move...")
                 client.unlink("account.move", [move_id])
                 print("Deleted.")
                 continue

            if move['state'] == 'posted':
                print("Attempting to reset to Draft...")
                try:
                    client.execute("account.move", "button_draft", [move_id])
                    print("Reset to Draft successful.")
                    
                    print("Deleting...")
                    client.unlink("account.move", [move_id])
                    print("Deleted.")
                except Exception as e:
                    print(f"Standard reset failed: {e}")
                    # If standard reset fails (e.g. EDI lock), try to force delete the EDI document first
                    # l10n_pe_edi_document might be linked
                    print("Checking for EDI documents...")
                    # This implies we know the EDI model. In standard Odoo it might be account.edi.document
                    # In Peru localization it might optionally use `l10n_pe_edi.document` or similar, 
                    # OR standard `account.edi.document`.
                    
                    edi_docs = client.search_read("account.edi.document", [["move_id", "=", move_id]], ["id"])
                    if edi_docs:
                        edi_ids = [d['id'] for d in edi_docs]
                        print(f"Found {len(edi_ids)} EDI documents. Deleting them first...")
                        client.unlink("account.edi.document", edi_ids)
                        print("EDI docs deleted. Retrying reset to draft...")
                        
                        client.execute("account.move", "button_draft", [move_id])
                        client.unlink("account.move", [move_id])
                        print("Deleted after removing EDI docs.")
                    else:
                        print("No standard EDI docs found. Trying to force state to draft via write (risky)...")
                        client.write("account.move", [move_id], {'state': 'draft'})
                        client.unlink("account.move", [move_id])
                        print("Force deleted.")

        except Exception as e:
            print(f"Error processing move {move_id}: {e}")

if __name__ == "__main__":
    cleanup_records()
