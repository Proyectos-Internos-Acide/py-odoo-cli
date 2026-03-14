import sys
import os
import json

# Ensure we can import odoo_cli from parent directory
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, root_path)

from odoo_cli import OdooClient

def create_test_invoice():
    client = OdooClient()
    uid = client.connect()
    print(f"Connected to Odoo with User ID: {uid}")

    # 1. Create a Test Partner with RUC
    print("Creating Test Partner...")
    # Using a known valid RUC format (e.g. SUNAT's demo RUC 20100066603)
    partner_id = client.create("res.partner", {
        'name': 'CLIENTE PRUEBA ANTIGRAVITY SAC',
        'vat': '20100066603',
        'l10n_latam_identification_type_id': client.search_read("l10n_latam.identification.type", [["name", "=", "RUC"]], ["id"])[0]['id'],
        'street': 'Calle de Pruebas 456',
        'city': 'Lima',
        'country_id': client.search_read("res.country", [["code", "=", "PE"]], ["id"])[0]['id'],
    })
    print(f"Partner Created (ID: {partner_id})")

    # 2. Find a Product
    products = client.search_read("product.product", domain=[["active", "=", True]], fields=["id", "name"], limit=1)
    if not products:
         print("Creating Test Product...")
         product_id = client.create("product.product", {'name': 'Servicio de Prueba FE', 'type': 'service'})
    else:
        product_id = products[0]['id']
        print(f"Using Product: {products[0]['name']} (ID: {product_id})")

    # 3. Create Invoice (account.move)
    print("Creating Invoice...")
    # move_type: 'out_invoice' for Sales Invoice
    # journal_id: we'll use the one found previously (Sales INV)
    journal = client.search_read("account.journal", [["type", "=", "sale"]], ["id"])[0]
    
    invoice_vals = {
        'move_type': 'out_invoice',
        'partner_id': partner_id,
        'journal_id': journal['id'],
        'invoice_date': '2026-02-12',
        'invoice_line_ids': [
            (0, 0, {
                'product_id': product_id,
                'name': 'Consultoría de Implementación FE',
                'quantity': 1,
                'price_unit': 100.0,
                'tax_ids': [(6, 0, [client.search_read("account.tax", [["name", "ilike", "IGV"], ["type_tax_use", "=", "sale"]], ["id"])[0]['id']])]
            })
        ]
    }
    
    invoice_id = client.create("account.move", invoice_vals)
    print(f"Invoice Created (ID: {invoice_id})")

    # 4. Post the Invoice
    print("Posting Invoice...")
    client.execute("account.move", "action_post", [invoice_id])
    print("Invoice Posted.")

    # 5. Check EDI status
    print("Waiting for EDI processing (may take a few seconds)...")
    import time
    time.sleep(5)
    
    status = client.search_read("account.move", [["id", "=", invoice_id]], ["name", "edi_state", "edi_error_message"])[0]
    print(f"Invoice Name: {status['name']}")
    print(f"EDI State: {status['edi_state']}")
    print(f"EDI Error: {status['edi_error_message']}")

if __name__ == "__main__":
    create_test_invoice()
