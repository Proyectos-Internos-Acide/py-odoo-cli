import sys
import os
import base64

# Ensure we can import odoo_cli from parent directory
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, root_path)

from odoo_cli import OdooClient

def inspect_xml():
    client = OdooClient()
    uid = client.connect()
    
    invoice_id = 13
    edi_docs = client.search_read("account.edi.document", [["move_id", "=", invoice_id]], ["edi_content", "edi_format_name"])
    
    if not edi_docs or not edi_docs[0]['edi_content']:
        print("No EDI content found yet.")
        return

    content_b64 = edi_docs[0]['edi_content']
    xml_data = base64.b64decode(content_b64).decode('utf-8')
    
    with open("invoice_debug.xml", "w") as f:
        f.write(xml_data)
    
    print("XML saved to invoice_debug.xml for inspection.")
    # Quick check for key tags
    if "<cbc:ID>" in xml_data:
        print("Invoice ID found in XML.")
    if "<cac:AccountingSupplierParty>" in xml_data:
        print("Supplier party found.")
    if "<cac:AccountingCustomerParty>" in xml_data:
        print("Customer party found.")

if __name__ == "__main__":
    inspect_xml()
