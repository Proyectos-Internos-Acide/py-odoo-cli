import json
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    views = client.search_read(
        "ir.ui.view",
        [["key", "=", "wtk.report_custom_quote_document"]],
        ["id", "arch_db"]
    )
    
    if views:
        print(views[0]["arch_db"])
    else:
        print("View not found!")

if __name__ == "__main__":
    main()
