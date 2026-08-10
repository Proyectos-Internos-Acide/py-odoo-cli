import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    print("=== Testing New Number & Existing Number Contact Resolution ===")
    
    # Test 1: Channel 27 (Antonio Ramirez - 51984463021)
    res1 = client.execute('ir.actions.server', 'run', [697], context={'active_id': 27, 'active_ids': [27], 'active_model': 'discuss.channel'})
    print("\nTest 1 (Existing contact match):")
    print("Action Result:", res1)
    if res1 and 'res_id' in res1:
        wiz1 = client.search_read('x_wtk_wa_create_opportunity_wizard', domain=[('id', '=', res1['res_id'])], fields=['x_name', 'x_partner_id', 'x_phone'])
        print("Wizard Pre-fill:", wiz1)

    # Test 2: Channel 8 (rderoger_ - 51977312592)
    res2 = client.execute('ir.actions.server', 'run', [697], context={'active_id': 8, 'active_ids': [8], 'active_model': 'discuss.channel'})
    print("\nTest 2 (New number with WhatsApp display name 'rderoger_'):")
    print("Action Result:", res2)
    if res2 and 'res_id' in res2:
        wiz2 = client.search_read('x_wtk_wa_create_opportunity_wizard', domain=[('id', '=', res2['res_id'])], fields=['x_name', 'x_partner_id', 'x_phone'])
        print("Wizard Pre-fill:", wiz2)

if __name__ == '__main__':
    main()
