import sys
import os

# Ensure we can import odoo_cli from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from odoo_cli import OdooClient

def fe_logic_guide():
    """
    This script serves as a technical guide to understand how Odoo Peru
    manages Electronic Invoicing (FE) through XML-RPC.
    """
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo. User ID: {uid}")

    print("\n=== ELECTRONIC INVOICING CORE CONCEPTS (PERU) ===")

    print("\n1. THE EDI DOCUMENT (account.edi.document)")
    print("Every invoice (account.move) generated in Odoo has a linked EDI Document.")
    print("This document tracks the status of the XML generation and submission.")
    
    # Let's check available states in account.edi.document
    edi_fields = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", "account.edi.document"], ["name", "=", "state"]],
        fields=["selection"]
    )
    if edi_fields:
        print(f"EDI States: {edi_fields[0]['selection']}")

    print("\n2. PERUVIAN SPECIFIC FIELDS (l10n_pe_edi)")
    print("Odoo Peru adds specific fields to account.move to handle SUNAT requirements:")
    pe_fields = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", "account.move"], ["name", "like", "l10n_pe_edi_"]],
        fields=["name", "field_description"]
    )
    for field in pe_fields[:10]: # Just first 10 for brevity
        print(f"- {field['name']}: {field['field_description']}")

    print("\n3. SUBMISSION WORKFLOW")
    print("When an invoice is posted (action_post):")
    print("a. account_edi automatically creates an account.edi.document in 'to_send' state.")
    print("b. A scheduled action (Cron) or manual 'Process Now' sends it to SUNAT/OSE.")
    print("c. On success, the state moves to 'sent' and 'edi_content' contains the signed XML.")
    print("d. SUNAT returns a CDR (Constancia de Recepción) which is stored in Odoo.")

    print("\n4. KEY MODELS FOR RESEARCH")
    print("- account.move: The invoice itself.")
    print("- account.edi.document: Links the move with the EDI process.")
    print("- account.edi.format: Defines the XML standard (e.g., UBL 2.1).")
    print("- l10n_pe_edi.certificate: Your Digital Certificate management.")

if __name__ == "__main__":
    fe_logic_guide()
