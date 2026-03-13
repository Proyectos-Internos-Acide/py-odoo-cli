import sys
import os

# Ensure we can import odoo_cli from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from odoo_cli import OdooClient

def verify_fe_details():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    print("\n--- Detailed Configuration Check ---")
    
    # Check Company Partner
    company = client.search_read("res.company", [], ["partner_id"], limit=1)[0]
    partner_id = company['partner_id'][0]
    
    partner = client.search_read(
        "res.partner",
        domain=[["id", "=", partner_id]],
        fields=["name", "vat", "street", "city", "zip", "state_id", "country_id", "l10n_pe_district"]
    )[0]
    
    print(f"Partner Name: {partner.get('name')}")
    print(f"RUC: {partner.get('vat')}")
    print(f"Street: {partner.get('street') or '[MISSING]'}")
    print(f"District: {partner.get('l10n_pe_district')[1] if partner.get('l10n_pe_district') else '[MISSING]'}")
    print(f"State: {partner.get('state_id')[1] if partner.get('state_id') else '[MISSING]'}")
    print(f"Zip (Ubigeo): {partner.get('zip') or '[MISSING]'}")

    print("\n--- SOL / OSE Credentials ---")
    pe_settings = client.search_read(
        "res.company",
        domain=[["id", "=", company['id']]],
        fields=["l10n_pe_edi_provider_username", "l10n_pe_edi_provider_password", "l10n_pe_edi_test_env"]
    )[0]
    
    print(f"SOL/OSE User: {pe_settings.get('l10n_pe_edi_provider_username') or '[MISSING]'}")
    print(f"SOL/OSE Password: {'[SET]' if pe_settings.get('l10n_pe_edi_provider_password') else '[MISSING]'}")
    print(f"Test Environment: {pe_settings.get('l10n_pe_edi_test_env')}")

if __name__ == "__main__":
    verify_fe_details()
