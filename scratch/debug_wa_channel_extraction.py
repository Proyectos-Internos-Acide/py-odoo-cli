import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    print("=== Checking recent discuss.channel records ===")
    channels = client.search_read('discuss.channel', domain=[], fields=['id', 'name', 'whatsapp_number', 'whatsapp_partner_id'], limit=10, order='id desc')
    for c in channels:
        print(c)

    print("\n=== Testing message extraction for Channel 27 (Antonio Ramirez) ===")
    msgs = client.search_read('mail.message', domain=[('model', '=', 'discuss.channel'), ('res_id', '=', 27)], fields=['id', 'date', 'author_id', 'body', 'email_from'], order='date asc', limit=20)
    for m in msgs:
        author = m['author_id'][1] if m['author_id'] else m['email_from'] or 'Cliente'
        print(f"[{m['date']}] {author}: {m['body']}")

if __name__ == '__main__':
    main()
