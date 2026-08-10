import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    print("==================================================================")
    print(" Simplifying WA Opportunity Wizard (No Transcript, Clean Name)   ")
    print("==================================================================")
    
    client = OdooClient()
    client.connect()

    model_name = 'x_wtk_wa_create_opportunity_wizard'
    model_id = client.search_read('ir.model', domain=[('model', '=', model_name)], fields=['id'])[0]['id']
    m_dc = client.search_read('ir.model', domain=[('model', '=', 'discuss.channel')], fields=['id'])[0]['id']

    # -------------------------------------------------------------------------
    # 1. Update Server Action 696 (Process Wizard)
    # -------------------------------------------------------------------------
    code_process_wizard = """target_wiz = record or (records[0] if records else False)
if target_wiz:
    channel = target_wiz.x_channel_id
    partner = target_wiz.x_partner_id
    raw_phone = target_wiz.x_phone
    op_name = target_wiz.x_name
    revenue = target_wiz.x_expected_revenue or 0.0
    stage = target_wiz.x_stage_id
    salesperson = target_wiz.x_user_id or env.user
    chat_html = target_wiz.x_description or ""

    # Garantizar prefijo [WhatsApp] - en el nombre
    if op_name and not op_name.startswith('[WhatsApp] -'):
        op_name = "[WhatsApp] - " + op_name

    digits = ''.join(c for c in (raw_phone or '') if c.isdigit())
    search_digits = digits[-9:] if len(digits) >= 9 else digits

    # Anti-duplicidad: Buscar Oportunidad activa
    lost_stages = env['crm.stage'].search([('name', 'in', ['Cancelado', 'Clientes Perdidos', 'PERDIDO TOTALMENTE'])])
    lost_stage_ids = lost_stages.ids if lost_stages else []

    domain_lead = [('type', '=', 'opportunity')]
    if lost_stage_ids:
        domain_lead.append(('stage_id', 'not in', lost_stage_ids))

    existing_lead = False
    if partner:
        lead_by_partner = env['crm.lead'].search(domain_lead + [('partner_id', '=', partner.id)], limit=1)
        if lead_by_partner:
            existing_lead = lead_by_partner[0]

    if not existing_lead and search_digits:
        lead_by_phone = env['crm.lead'].search(domain_lead + [('phone', 'ilike', search_digits)], limit=1)
        if lead_by_phone:
            existing_lead = lead_by_phone[0]

    target_lead = False
    if existing_lead:
        # Caso A: Vincular a Oportunidad existente
        target_lead = existing_lead
        note_body = (
            "<b>🔄 Sincronización desde WhatsApp:</b><br/>" +
            "Se vinculó la conversación de WhatsApp a esta Oportunidad.<br/><br/>" +
            (chat_html or "")
        )
        target_lead.message_post(body=note_body, message_type='comment')
        if revenue > 0:
            target_lead.write({'expected_revenue': revenue})
        
        if channel:
            channel.message_post(
                body="📌 <i>Chat vinculado a Oportunidad existente: <b>#" + str(target_lead.id) + " - " + str(target_lead.name) + "</b></i>",
                message_type='comment'
            )
    else:
        # Caso B: Crear nueva Oportunidad con prefijo [WhatsApp] - y sin Cotización
        stage_new = env['crm.stage'].search([('name', 'ilike', 'Nuevo')], limit=1)
        if not stage_new:
            stage_new = env['crm.stage'].search([], order='sequence asc', limit=1)

        lead_vals = {
            'name': op_name or ("[WhatsApp] - " + str(partner.name if partner else raw_phone)),
            'partner_id': partner.id if partner else False,
            'phone': raw_phone or (partner.phone if partner else False),
            'expected_revenue': revenue,
            'type': 'opportunity',
            'stage_id': stage_new.id if stage_new else False,
            'user_id': salesperson.id,
            'description': chat_html or "<i>Oportunidad creada desde WhatsApp</i>",
        }
        target_lead = env['crm.lead'].create(lead_vals)
        
        if channel:
            channel.message_post(
                body="📌 <i>Nueva Oportunidad CRM creada: <b>#" + str(target_lead.id) + " - " + str(target_lead.name) + "</b> asignada a @" + str(salesperson.name) + "</i>",
                message_type='comment'
            )

    if target_lead:
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Oportunidad CRM',
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'res_id': target_lead.id,
            'target': 'current',
        }
"""

    existing_sa696 = client.search_read('ir.actions.server', domain=[('name', '=', 'WTK - Procesar Wizard Oportunidad WA')], fields=['id'])
    if existing_sa696:
        sa696_id = existing_sa696[0]['id']
        client.write('ir.actions.server', [sa696_id], {'code': code_process_wizard, 'model_id': model_id})
    else:
        sa696_id = client.create('ir.actions.server', {
            'name': 'WTK - Procesar Wizard Oportunidad WA',
            'model_id': model_id,
            'state': 'code',
            'code': code_process_wizard,
        })

    # -------------------------------------------------------------------------
    # 2. Update Wizard Form View (SUPER SIMPLE: NO transcript tab, NO extra groups)
    # -------------------------------------------------------------------------
    view_name = "wtk.wa.create.opportunity.wizard.form"
    existing_wview = client.search_read('ir.ui.view', domain=[('name', '=', view_name)], fields=['id'])

    arch_wizard_form = f"""<form string="Crear Oportunidad CRM desde WhatsApp">
        <sheet>
            <div class="oe_title">
                <label for="x_name" string="Nombre de la Oportunidad"/>
                <h1>
                    <field name="x_name" placeholder="Ej: [WhatsApp] - Antonio Ramirez" required="1"/>
                </h1>
            </div>
            <group>
                <field name="x_partner_id"/>
                <field name="x_phone"/>
                <field name="x_channel_id" readonly="1"/>
            </group>
        </sheet>
        <footer>
            <button name="{sa696_id}" string="🚀 Crear / Vincular Oportunidad" type="action" class="btn-primary"/>
            <button string="Cancelar" class="btn-secondary" special="cancel"/>
        </footer>
    </form>"""

    if existing_wview:
        client.write('ir.ui.view', [existing_wview[0]['id']], {'arch_db': arch_wizard_form})
        wview_id = existing_wview[0]['id']
        print(f"Updated simplified wizard view ID {wview_id}")
    else:
        wview_id = client.create('ir.ui.view', {
            'name': view_name,
            'model': model_name,
            'type': 'form',
            'arch_db': arch_wizard_form,
        })

    # -------------------------------------------------------------------------
    # 3. Update Server Action 697 (Pre-fill [WhatsApp] - Partner Name WITHOUT 'Cotización')
    # -------------------------------------------------------------------------
    code_open_wizard = f"""# Server Action 697: Abrir Wizard Modal Ultra-Simple
channel = False

target_rec = record or (records[0] if records else False)
if target_rec and target_rec._name == 'discuss.channel':
    channel = target_rec

if not channel:
    active_id = env.context.get('active_id')
    if active_id and isinstance(active_id, int):
        ch = env['discuss.channel'].browse(active_id)
        if ch and ch.exists():
            channel = ch

if not channel:
    act_name = env.context.get('active_channel_name')
    act_phone = env.context.get('active_phone')
    if act_phone:
        chs = env['discuss.channel'].search([('whatsapp_number', 'ilike', act_phone)], limit=1)
        if chs:
            channel = chs[0]
    if not channel and act_name:
        chs = env['discuss.channel'].search([('name', 'ilike', act_name)], limit=1)
        if chs:
            channel = chs[0]

if not channel:
    chs = env['discuss.channel'].search([('channel_type', '=', 'whatsapp')], order='write_date desc, id desc', limit=1)
    if chs:
        channel = chs[0]

raw_phone = channel.whatsapp_number if channel else ''
partner = channel.whatsapp_partner_id if channel else False

digits = ''.join(c for c in (raw_phone or '') if c.isdigit())
search_digits = digits[-9:] if len(digits) >= 9 else digits

if not partner and search_digits:
    partners = env['res.partner'].search([('phone', 'ilike', search_digits)], limit=1)
    if partners:
        partner = partners[0]

if not partner and raw_phone:
    p_name = channel.name if channel and not channel.name.startswith('51') and not channel.name.startswith('+') else ("Contacto WA " + str(raw_phone))
    partner = env['res.partner'].create({{'name': p_name, 'phone': raw_phone}})

if channel and partner and not channel.whatsapp_partner_id:
    channel.write({{'whatsapp_partner_id': partner.id}})

# Transcribir Chat WA para guardar en la descripción de la Oportunidad en segundo plano
chat_html = ""
if channel:
    msgs = env['mail.message'].search([
        ('model', '=', 'discuss.channel'),
        ('res_id', '=', channel.id)
    ], order='date asc', limit=50)

    rows = []
    for m in msgs:
        date_str = str(m.date)[:16] if m.date else ''
        author = m.author_id.name if m.author_id else (m.email_from or 'Cliente')
        body = m.body or ''
        rows.append("<tr style='border-bottom: 1px solid #eee;'>" +
                    "<td style='padding:6px; font-size:12px; color:#888; white-space:nowrap; vertical-align:top;'>" + date_str + "</td>" +
                    "<td style='padding:6px; font-weight:bold; font-size:12px; color:#333; vertical-align:top;'>" + str(author) + ":</td>" +
                    "<td style='padding:6px; font-size:12px; color:#444; vertical-align:top;'>" + str(body) + "</td>" +
                    "</tr>")
    if rows:
        chat_html = (
            "<h4>💬 Historial de WhatsApp (" + str(len(msgs)) + " mensajes)</h4>" +
            "<table style='width:100%; border-collapse:collapse;'>" +
            "".join(rows) +
            "</table>"
        )

# Pre-llenar nombre SIN Cotización: [WhatsApp] - Nombre Cliente
op_name = "[WhatsApp] - " + str(partner.name if partner else (channel.name if channel else raw_phone))

stage_new = env['crm.stage'].search([('name', 'ilike', 'Nuevo')], limit=1)

wiz_vals = {{
    'x_channel_id': channel.id if channel else False,
    'x_partner_id': partner.id if partner else False,
    'x_phone': raw_phone or (partner.phone if partner else ''),
    'x_name': op_name,
    'x_expected_revenue': 0.0,
    'x_stage_id': stage_new.id if stage_new else False,
    'x_user_id': env.user.id,
    'x_description': chat_html or "<i>Conversación de WhatsApp</i>",
}}

wiz = env['x_wtk_wa_create_opportunity_wizard'].create(wiz_vals)

action = {{
    'type': 'ir.actions.act_window',
    'name': 'Crear Oportunidad CRM desde WhatsApp',
    'res_model': 'x_wtk_wa_create_opportunity_wizard',
    'view_mode': 'form',
    'res_id': wiz.id,
    'view_id': {wview_id},
    'target': 'new',
    'context': {{'dialog_size': 'small'}},
}}
"""

    existing_sa697 = client.search_read('ir.actions.server', domain=[('name', '=', 'WTK - Abrir Wizard Oportunidad desde WA')], fields=['id'])
    if existing_sa697:
        sa693_id = existing_sa697[0]['id']
        client.write('ir.actions.server', [sa693_id], {'code': code_open_wizard, 'model_id': m_dc})
        print(f"Updated Server Action ID {sa693_id}")

    print("\n==================================================================")
    print(" SIMPLIFIED WIZARD DEPLOYMENT COMPLETE ")
    print("==================================================================")

if __name__ == '__main__':
    main()
