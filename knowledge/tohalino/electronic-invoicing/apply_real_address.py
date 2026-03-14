import sys
import os
from dotenv import load_dotenv

# Ensure we can import odoo_cli from parent directory
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, root_path)

from odoo_cli import OdooClient

def apply_real_address():
    load_dotenv()
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    # 1. Find Company
    company = client.search_read("res.company", [], ["id", "partner_id"], limit=1)[0]
    partner_id = company['partner_id'][0]
    
    # 2. Extract from Env
    street = os.getenv("FISCAL_STREET", "CAL. DE PRUEBAS 123")
    district_name = os.getenv("FISCAL_DISTRICT", "MIRAFLORES")
    city_name = os.getenv("FISCAL_CITY", "LIMA")
    state_name = os.getenv("FISCAL_STATE", "LIMA")
    zip_code = os.getenv("FISCAL_ZIP", "150101")

    print(f"Applying address: {street}, {district_name}, {city_name}, {state_name}")

    # 3. Find IDs
    # State: AREQUIPA
    states = client.search_read("res.country.state", [["name", "ilike", state_name], ["country_id.code", "=", "PE"]], ["id", "name"])
    state_id = states[0]['id'] if states else None
    
    # District: MIRAFLORES in AREQUIPA (Title Case in Odoo)
    districts = client.search_read("l10n_pe.res.city.district", [["name", "=", district_name.title()], ["city_id.name", "ilike", city_name]], ["id", "name"])
    if not districts:
        districts = client.search_read("l10n_pe.res.city.district", [["name", "=", district_name.title()]], ["id", "name"])
    
    district_id = districts[0]['id'] if districts else None

    # 4. Update Partner
    address_vals = {
        'street': street,
        'city': city_name,
        'zip': zip_code,
        'state_id': state_id,
        'country_id': client.search_read("res.country", [["code", "=", "PE"]], ["id"])[0]['id'],
        'l10n_pe_district': district_id
    }
    
    print(f"Updating Partner {partner_id}...")
    client.write("res.partner", [partner_id], address_vals)
    print("Real fiscal address applied successfully.")

if __name__ == "__main__":
    apply_real_address()
