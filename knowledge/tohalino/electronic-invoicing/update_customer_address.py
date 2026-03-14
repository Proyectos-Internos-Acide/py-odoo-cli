import sys
import os

# Ensure we can import odoo_cli from parent directory
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, root_path)

from odoo_cli import OdooClient

def update_customer_test_address():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    partner_id = 8 # Test Customer
    
    # Address details for San Miguel, Lima (District ID 1316 verified)
    address_vals = {
        'street': 'Calle de Prueba 123',
        'city': 'Lima',
        'zip': '150136',
        'state_id': client.search_read("res.country.state", [["name", "=", "Lima"]], ["id"])[0]['id'],
        'country_id': client.search_read("res.country", [["code", "=", "PE"]], ["id"])[0]['id'],
        'l10n_pe_district': 1316 # San Miguel
    }
    
    print(f"Updating Partner {partner_id} with test address...")
    client.write("res.partner", [partner_id], address_vals)
    print("Address updated successfully.")

if __name__ == "__main__":
    update_customer_test_address()
