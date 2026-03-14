import sys
import os
from dotenv import load_dotenv

# Ensure we can import odoo_cli from parent directory
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, root_path)

from odoo_cli import OdooClient

def update_sol_credentials():
    load_dotenv()
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    # 1. Extract from Env
    sol_user = os.getenv("SUNAT_SOL_USER")
    sol_password = os.getenv("SUNAT_SOL_PASSWORD")

    if not sol_user or not sol_password:
        print("Error: SUNAT_SOL_USER or SUNAT_SOL_PASSWORD not found in .env")
        return

    # 2. Find Company
    company = client.search_read("res.company", [], ["id", "name"], limit=1)[0]
    company_id = company['id']
    
    print(f"Updating SOL credentials for company: {company['name']} (ID: {company_id})")
    print(f"New User: {sol_user}")

    # 3. Update Company
    vals = {
        'l10n_pe_edi_provider_username': sol_user,
        'l10n_pe_edi_provider_password': sol_password,
    }
    
    client.write("res.company", [company_id], vals)
    print("SOL credentials updated successfully in Odoo.")

if __name__ == "__main__":
    update_sol_credentials()
