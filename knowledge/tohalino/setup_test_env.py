import sys
import os

# Ensure we can import odoo_cli from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from odoo_cli import OdooClient

def setup_test_env():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    # 1. Find Company
    company = client.search_read("res.company", [], ["id", "partner_id"], limit=1)[0]
    company_id = company['id']
    partner_id = company['partner_id'][0]
    
    print(f"Targeting Company ID: {company_id}, Partner ID: {partner_id}")

    # 2. Enable Test Mode
    print("Enabling Test Environment (l10n_pe_edi_test_env)...")
    client.write("res.company", [company_id], {'l10n_pe_edi_test_env': True})
    print("Test Environment enabled.")

    # 3. Find IDs for State and District (Lima)
    # State: Lima (PE-LIM)
    states = client.search_read("res.country.state", [["code", "=", "LMA"], ["country_id.code", "=", "PE"]], ["id", "name"])
    if not states:
        # Fallback search by name
        states = client.search_read("res.country.state", [["name", "=", "Lima"]], ["id", "name"])
    
    state_id = states[0]['id'] if states else None
    print(f"Found State ID: {state_id} ({states[0]['name'] if states else 'NOT FOUND'})")

    # District: LIMA (Ubigeo starts with 150101)
    # Model in Odoo Peru is often l10n_pe.res.city.district
    districts = client.search_read("l10n_pe.res.city.district", [["name", "ilike", "Lima"]], ["id", "name", "code"], limit=1)
    district_id = districts[0]['id'] if districts else None
    print(f"Found District ID: {district_id} ({districts[0]['name'] if districts else 'NOT FOUND'})")

    # 4. Update Partner Address
    address_vals = {
        'street': 'Av. de Pruebas 123',
        'city': 'Lima',
        'zip': '150101', # Ubigeo
        'state_id': state_id,
        'country_id': client.search_read("res.country", [["code", "=", "PE"]], ["id"])[0]['id'],
        'l10n_pe_district': district_id
    }
    
    print(f"Updating Partner {partner_id} address...")
    client.write("res.partner", [partner_id], address_vals)
    print("Address updated.")

if __name__ == "__main__":
    setup_test_env()
