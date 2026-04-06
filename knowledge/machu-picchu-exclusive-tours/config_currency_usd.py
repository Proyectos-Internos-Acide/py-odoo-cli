"""
Script to configure Odoo to strictly use USD and deactivate PEN.
Designed to be executed with the active py-odoo-cli environment.
"""
from odoo_cli import OdooClient
from odoo_cli.exceptions import OdooFaultError

def main():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected as User ID {uid}.")
    
    # 1. Activate USD (ID 1)
    print("Activating USD (ID: 1)...")
    client.write('res.currency', [1], {'active': True})
    
    # 2. Change Company currency to USD
    # The default company usually is ID 1
    print("Changing company (ID: 1) base currency to USD...")
    try:
        client.write('res.company', [1], {'currency_id': 1})
        print("Company currency updated successfully.")
    except OdooFaultError as e:
        print(f"Error setting company currency: {e.fault_string}")
        print("Note: This can happen if accounting entries exist. Make sure to remove any existing journal entries in PEN before doing this.")
        raise
    
    # 3. Update all pricelists to USD
    pricelists = client.search_read('product.pricelist', [], fields=['id', 'name'])
    pricelist_ids = [p['id'] for p in pricelists]
    if pricelist_ids:
        print(f"Updating {len(pricelist_ids)} pricelists to use USD...")
        client.write('product.pricelist', pricelist_ids, {'currency_id': 1})
        for p in pricelists:
            print(f"- {p['name']} (ID {p['id']}) updated.")
    
    # 4. Deactivate PEN (ID 157)
    print("Deactivating PEN (ID: 157)...")
    try:
        client.write('res.currency', [157], {'active': False})
        print("PEN deactivated successfully.")
    except OdooFaultError as e:
        print(f"Error deactivating PEN: {e.fault_string}")
        print("This might happen if PEN is still referenced in other critical models. Double check your configuration.")
        raise
        
    print("\nSUCCESS: The Odoo instance is now configured to only use USD.")

if __name__ == "__main__":
    main()
