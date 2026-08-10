import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    print("=== Testing feasibility of extracting messages from a discuss.channel ===")
    channel_id = 9  # Antonio Ramirez whatsapp channel
    channel = client.search_read('discuss.channel', domain=[('id', '=', channel_id)], fields=['id', 'name', 'whatsapp_number', 'whatsapp_partner_id'])
    print("Channel:", channel)

    if channel:
        msgs = client.search_read(
            'mail.message',
            domain=[('model', '=', 'discuss.channel'), ('res_id', '=', channel_id)],
            fields=['id', 'date', 'author_id', 'body', 'email_from'],
            order='date asc',
            limit=20
        )
        print(f"Found {len(msgs)} messages in channel:")
        for m in msgs:
            author = m['author_id'][1] if m['author_id'] else m['email_from'] or 'Cliente'
            print(f"  • [{m['date']}] {author}: {m['body'][:100]}")

    print("\n=== Checking CRM stages available for new Opportunity ===")
    stages = client.search_read('crm.stage', domain=[], fields=['id', 'name', 'sequence'], order='sequence asc')
    for s in stages:
        print(s)

if __name__ == '__main__':
    main()
