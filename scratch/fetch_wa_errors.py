import json
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    # Let's get the fields of whatsapp.message first to see what's available
    fields_info = client.search_read("ir.model.fields", [["model", "=", "whatsapp.message"]], ["name", "ttype"])
    field_names = [f["name"] for f in fields_info]
    
    interesting_fields = [f for f in ["id", "state", "failure_type", "failure_reason", "error_msg", "body", "mobile_number_formatted"] if f in field_names]
    if not interesting_fields:
        interesting_fields = ["id", "state"] # Fallback
        
    messages = client.search_read(
        "whatsapp.message", 
        [["state", "=", "error"]], 
        interesting_fields, 
        limit=5, 
        order="id desc"
    )
    
    print(json.dumps(messages, indent=2))

if __name__ == "__main__":
    main()
