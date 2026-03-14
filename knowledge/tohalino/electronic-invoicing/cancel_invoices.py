import sys
import os
import time

# Ensure we can import odoo_cli from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from odoo_cli import OdooClient

def cancel_invoices():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    invoice_ids = [1, 2, 3]
    reason = "Solicitud del cliente (Cancelación)"
    refund_reason_code = '01' # Cancellation of the operation

    for invoice_id in invoice_ids:
        print(f"\nProcessing Invoice ID: {invoice_id}")
        
        # 1. Check if invoice exists and is posted
        invoices = client.search_read(
            "account.move", 
            domain=[["id", "=", invoice_id]], 
            fields=["name", "state", "payment_state", "move_type", "amount_total", "journal_id"]
        )
        
        if not invoices:
            print(f"Invoice {invoice_id} not found.")
            continue
            
        inv = invoices[0]
        print(f"Found Invoice: {inv['name']} State: {inv['state']} Payment: {inv['payment_state']}")

        if inv['state'] != 'posted':
            print(f"Invoice {inv['name']} is not posted (State: {inv['state']}), skipping/cannot reverse.")
            continue

        if inv['payment_state'] in ['paid', 'reversed']:
            print(f"Invoice {inv['name']} is already paid or reversed.")
            continue

        try:
            # 2. Create Reversal Wizard
            # Fields for typical Peruvian localization setup
            # journal_id comes as [id, 'Name']
            journal_id = inv['journal_id'][0] if inv['journal_id'] else None
            
            wizard_vals = {
                'move_ids': [[6, 0, [invoice_id]]],
                'reason': reason,
                'l10n_pe_edi_refund_reason': refund_reason_code,
                'journal_id': journal_id, # Mandatory field
            }
            
            wizard_id = client.create('account.move.reversal', wizard_vals)
            print(f"Created Reversal Wizard ID: {wizard_id}")

            # 3. Execute 'reverse_moves' method
            result = client.execute('account.move.reversal', 'reverse_moves', [wizard_id])
            print(f"Reversal executed. Type: {result.get('type')}")

            # 4. Find the created Credit Note
            time.sleep(1) 
            
            credit_notes = client.search_read(
                "account.move",
                domain=[["reversed_entry_id", "=", invoice_id], ["move_type", "=", "out_refund"]],
                fields=["id", "name", "state", "payment_state"]
            )

            if not credit_notes:
                print(f"Could not find created Credit Note for invoice {invoice_id}.")
                continue
            
            cn = credit_notes[0]
            print(f"Found Credit Note: {cn['name']} (ID: {cn['id']}) State: {cn['state']}")

            # 5. Post the Credit Note if draft
            if cn['state'] == 'draft':
                print(f"Posting Credit Note {cn['name']}...")
                client.execute("account.move", "action_post", [cn['id']])
                print("Credit Note posted.")
            
            # 6. Check final status
            updated_inv = client.search_read("account.move", domain=[["id", "=", invoice_id]], fields=["payment_state"])[0]
            print(f"Invoice {inv['name']} new payment state: {updated_inv['payment_state']}")

        except Exception as e:
            print(f"Error processing invoice {invoice_id}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    cancel_invoices()
