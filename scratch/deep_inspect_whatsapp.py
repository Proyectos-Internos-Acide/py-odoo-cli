import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    print("=== Inspecting discuss.channel for whatsapp channels ===")
    channels = client.search_read(
        'discuss.channel',
        domain=[('channel_type', '=', 'whatsapp')],
        fields=['id', 'name', 'channel_type', 'whatsapp_partner_id', 'whatsapp_number', 'description', 'create_date'],
        limit=5
    )
    print(f"Found {len(channels)} whatsapp discuss channels:")
    for c in channels:
        print(c)

    print("\n=== Inspecting fields on discuss.channel related to whatsapp or lead ===")
    fields_dc = client.search_read(
        'ir.model.fields',
        domain=[('model', '=', 'discuss.channel')],
        fields=['name', 'field_description', 'ttype', 'relation']
    )
    wa_dc_fields = [f for f in fields_dc if 'wa' in f['name'] or 'lead' in f['name'] or 'crm' in f['name'] or 'whatsapp' in f['name']]
    for f in wa_dc_fields:
        print(f"Field: {f['name']} | Desc: {f['field_description']} | Type: {f['ttype']} | Rel: {f.get('relation')}")

    print("\n=== Inspecting whatsapp.message fields ===")
    fields_wm = client.search_read(
        'ir.model.fields',
        domain=[('model', '=', 'whatsapp.message')],
        fields=['name', 'field_description', 'ttype', 'relation']
    )
    for f in fields_wm:
        print(f"Field: {f['name']} | Desc: {f['field_description']} | Type: {f['ttype']} | Rel: {f.get('relation')}")

    print("\n=== Inspecting recent whatsapp.message records ===")
    wa_msgs = client.search_read(
        'whatsapp.message',
        domain=[],
        fields=['id', 'body', 'mobile_number', 'state', 'create_date', 'mail_message_id'],
        limit=5,
        order='create_date desc'
    )
    for m in wa_msgs:
        print(m)

if __name__ == '__main__':
    main()
