import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    print("==================================================================")
    print(" Adding UI Header Button & Menu Item for WhatsApp -> CRM Action  ")
    print("==================================================================")
    
    client = OdooClient()
    client.connect()

    # 1. Inherit res.partner.form to add header button
    view_name = "res.partner.form.wtk.wa_button"
    existing_view = client.search_read('ir.ui.view', domain=[('name', '=', view_name)], fields=['id'])
    
    arch_xml = """<data>
        <xpath expr="//form" position="inside">
            <header>
                <button name="694" string="➕ Crear Oportunidad CRM desde WhatsApp" type="action" class="oe_highlight"/>
            </header>
        </xpath>
    </data>"""

    if existing_view:
        client.write('ir.ui.view', [existing_view[0]['id']], {
            'arch_db': arch_xml
        })
        print(f"Updated inherited view ID: {existing_view[0]['id']}")
    else:
        v_id = client.create('ir.ui.view', {
            'name': view_name,
            'model': 'res.partner',
            'inherit_id': 127,  # res.partner.form
            'type': 'form',
            'arch_db': arch_xml,
            'priority': 16,
        })
        print(f"Created inherited view ID: {v_id} for res.partner.form button")

    # 2. Check / Create Window Action for whatsapp.message
    act_name = "💬 Mensajes de WhatsApp"
    existing_act = client.search_read('ir.actions.act_window', domain=[('name', '=', act_name)], fields=['id'])
    
    if existing_act:
        act_id = existing_act[0]['id']
        print(f"Existing window action ID: {act_id}")
    else:
        act_id = client.create('ir.actions.act_window', {
            'name': act_name,
            'res_model': 'whatsapp.message',
            'view_mode': 'list,form',
            'target': 'current',
            'context': '{}',
        })
        print(f"Created window action ID: {act_id}")

    # 3. Create Menu Items under WhatsApp (ID 381) and CRM
    # Find WhatsApp parent menu (ID 381)
    wa_parent = client.search_read('ir.ui.menu', domain=[('id', '=', 381)], fields=['id', 'name'])
    crm_parent = client.search_read('ir.ui.menu', domain=[('name', '=', 'CRM'), ('parent_id', '=', False)], fields=['id', 'name'])

    if wa_parent:
        existing_m1 = client.search_read('ir.ui.menu', domain=[('name', '=', '💬 Mensajes WhatsApp'), ('parent_id', '=', 381)], fields=['id'])
        if not existing_m1:
            m1_id = client.create('ir.ui.menu', {
                'name': '💬 Mensajes WhatsApp',
                'parent_id': 381,
                'action': f'ir.actions.act_window,{act_id}',
                'sequence': 5,
            })
            print(f"Created menu under WhatsApp: ID {m1_id}")
        else:
            print(f"Menu under WhatsApp already exists: ID {existing_m1[0]['id']}")

    if crm_parent:
        existing_m2 = client.search_read('ir.ui.menu', domain=[('name', '=', '💬 Mensajes WhatsApp'), ('parent_id', '=', crm_parent[0]['id'])], fields=['id'])
        if not existing_m2:
            m2_id = client.create('ir.ui.menu', {
                'name': '💬 Mensajes WhatsApp',
                'parent_id': crm_parent[0]['id'],
                'action': f'ir.actions.act_window,{act_id}',
                'sequence': 20,
            })
            print(f"Created menu under CRM: ID {m2_id}")

    print("\n==================================================================")
    print(" UI ACCESSIBILITY UPDATES COMPLETE ")
    print("==================================================================")

if __name__ == '__main__':
    main()
