import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    print("=== Testing execution of Server Action 693 on discuss.channel ID 9 ===")
    channel_id = 9
    
    # Execute Server Action 693 using run / Server Action execution
    res = client.execute('ir.actions.server', 'run', [693], {'active_id': channel_id, 'active_ids': [channel_id], 'active_model': 'discuss.channel'})
    print("Execution Result:")
    print(res)

    print("\n=== Checking created/updated CRM Lead ===")
    leads = client.search_read('crm.lead', domain=[('phone', 'ilike', '984463021')], fields=['id', 'name', 'partner_id', 'phone', 'stage_id', 'user_id', 'description'])
    for l in leads:
        print("Lead ID:", l['id'])
        print("Name:", l['name'])
        print("Partner:", l['partner_id'])
        print("Phone:", l['phone'])
        print("Stage:", l['stage_id'])
        print("User:", l['user_id'])
        print("Description snippet:", l['description'][:200] if l['description'] else 'None')

if __name__ == '__main__':
    main()
