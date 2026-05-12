from odoo_cli import OdooClient
import json

def main():
    client = OdooClient()
    client.connect()
    fields = client.search_read("ir.model.fields", [["model", "=", "whatsapp.template.variable"]], ["name", "ttype"])
    print(json.dumps(fields, indent=2))

if __name__ == "__main__":
    main()
