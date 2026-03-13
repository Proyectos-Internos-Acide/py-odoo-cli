import sys
import os

# Ensure we can import odoo_cli from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from odoo_cli import OdooClient

def verify_fe_config():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    print("\n--- 1. Verification of Modules ---")
    modules_to_check = ['l10n_pe', 'l10n_pe_edi', 'account_edi']
    modules = client.search_read(
        "ir.module.module", 
        domain=[["name", "in", modules_to_check], ["state", "=", "installed"]],
        fields=["name", "shortdesc", "installed_version"]
    )
    installed_modules = {m['name']: m for m in modules}
    for m_name in modules_to_check:
        if m_name in installed_modules:
            print(f"[OK] Module {m_name} is installed ({installed_modules[m_name]['installed_version']})")
        else:
            print(f"[MISSING] Module {m_name} is NOT installed")

    print("\n--- 2. Verification of Company Data ---")
    company = client.search_read(
        "res.company",
        domain=[],
        fields=["name", "vat", "street", "city", "l10n_pe_edi_address_type_code", "country_id"],
        limit=1
    )[0]
    
    print(f"Company Name: {company.get('name')}")
    print(f"VAT (RUC): {company.get('vat') or 'NOT SET'}")
    print(f"Address: {company.get('street') or 'NOT SET'}, {company.get('city') or ''}")
    # L10n PE specific
    print(f"Address Type Code (Establishment): {company.get('l10n_pe_edi_address_type_code') or 'NOT SET'}")

    print("\n--- 3. Verification of Sales Journals ---")
    journals = client.search_read(
        "account.journal",
        domain=[["type", "=", "sale"]],
        fields=["name", "code", "l10n_latam_use_documents", "edi_format_ids"]
    )
    for j in journals:
        print(f"Journal: {j['name']} ({j['code']})")
        print(f"  Uses Latam Documents: {j.get('l10n_latam_use_documents')}")
        # Note: edi_format_ids is a m2m, usually 01 (Factura), 03 (Boleta), etc. in Peru
        print(f"  EDI Formats: {j.get('edi_format_ids')}")

    print("\n--- 4. Verification of EDI Provider ---")
    # This varies by Odoo version. In newer versions (v14+), it's often in account.edi.format or res.company
    # Let's check company for specific Peruvian settings
    pe_config = client.search_read(
        "res.company",
        domain=[["id", "=", company['id']]],
        fields=["l10n_pe_edi_provider", "l10n_pe_edi_certificate_id"]
    )[0]
    print(f"EDI Provider: {pe_config.get('l10n_pe_edi_provider') or 'NOT SET'}")
    print(f"Certificate Configured: {'YES' if pe_config.get('l10n_pe_edi_certificate_id') else 'NO'}")

if __name__ == "__main__":
    verify_fe_config()
