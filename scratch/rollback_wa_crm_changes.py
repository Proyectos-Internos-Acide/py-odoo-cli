import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    print("==================================================================")
    print(" Rolling Back All WhatsApp -> CRM Created Actions & Views       ")
    print("==================================================================")
    
    client = OdooClient()
    client.connect()

    # 1. Delete ir.asset ID 115
    assets = client.search_read('ir.asset', domain=[('id', '=', 115)], fields=['id'])
    if assets:
        client.execute('ir.asset', 'unlink', [115])
        print("Unlinked ir.asset ID 115")

    # 2. Delete ir.attachment ID 3184
    atts = client.search_read('ir.attachment', domain=[('id', '=', 3184)], fields=['id'])
    if atts:
        client.execute('ir.attachment', 'unlink', [3184])
        print("Unlinked ir.attachment ID 3184")

    # 3. Delete inherited view ID 2698
    views = client.search_read('ir.ui.view', domain=[('id', '=', 2698)], fields=['id'])
    if views:
        client.execute('ir.ui.view', 'unlink', [2698])
        print("Unlinked ir.ui.view ID 2698")

    # 4. Delete menus 415 and 416
    menus = client.search_read('ir.ui.menu', domain=[('id', 'in', [415, 416])], fields=['id'])
    if menus:
        m_ids = [m['id'] for m in menus]
        client.execute('ir.ui.menu', 'unlink', m_ids)
        print(f"Unlinked ir.ui.menu IDs {m_ids}")

    # 5. Delete window action 695
    act_wins = client.search_read('ir.actions.act_window', domain=[('id', '=', 695)], fields=['id'])
    if act_wins:
        client.execute('ir.actions.act_window', 'unlink', [695])
        print("Unlinked ir.actions.act_window ID 695")

    # 6. Delete server actions 693 and 694
    sa = client.search_read('ir.actions.server', domain=[('id', 'in', [693, 694])], fields=['id'])
    if sa:
        sa_ids = [s['id'] for s in sa]
        client.execute('ir.actions.server', 'unlink', sa_ids)
        print(f"Unlinked ir.actions.server IDs {sa_ids}")

    # 7. Reset action 656 binding
    sa656 = client.search_read('ir.actions.server', domain=[('id', '=', 656)], fields=['id'])
    if sa656:
        client.write('ir.actions.server', [656], {
            'binding_model_id': False,
        })
        print("Reset binding on Server Action 656")

    print("\n==================================================================")
    print(" ROLLBACK COMPLETE: All changes clean and removed ")
    print("==================================================================")

if __name__ == '__main__':
    main()
