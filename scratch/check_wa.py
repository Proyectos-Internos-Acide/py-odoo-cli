from odoo_cli import OdooClient
import json

client = OdooClient()
client.connect()
t = client.search_read("whatsapp.template", [["active","=",False]], ["name","model_id","phone_field"])
print(json.dumps(t, indent=2))
