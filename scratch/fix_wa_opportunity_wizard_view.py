import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    print("==================================================================")
    print(" Completely Removing Transcript Tab & Setting Button 'Crear Oportunidad' ")
    print("==================================================================")
    
    client = OdooClient()
    client.connect()

    model_name = 'x_wtk_wa_create_opportunity_wizard'
    model_id = client.search_read('ir.model', domain=[('model', '=', model_name)], fields=['id'])[0]['id']
    m_dc = client.search_read('ir.model', domain=[('model', '=', 'discuss.channel')], fields=['id'])[0]['id']
    wview_id = 2700

    # 1. Update View 2700 - NO Notebook, NO Transcript, Clean Button "🚀 Crear Oportunidad"
    arch_wizard_form = """<form string="Crear Oportunidad CRM desde WhatsApp">
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
            <button name="696" string="🚀 Crear Oportunidad" type="action" class="btn-primary"/>
            <button string="Cancelar" class="btn-secondary" special="cancel"/>
        </footer>
    </form>"""

    client.write('ir.ui.view', [wview_id], {'arch_db': arch_wizard_form})
    print(f"Updated view ID {wview_id} - Completely removed transcript notebook tab & updated button text")

    # 2. Update Server Action 697 to use medium dialog_size (NOT small/angosto)
    code_open_wizard = f"""# Server Action 697: Abrir Wizard Modal Limpio (Medium Size)
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

# Pre-llenar nombre SIN 'Cotización': [WhatsApp] - Nombre Cliente
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
    'context': {{'dialog_size': 'medium'}},
}}
"""

    client.write('ir.actions.server', [697], {'code': code_open_wizard, 'model_id': m_dc})
    print("Updated Server Action 697 (dialog_size: 'medium')")

    print("\n==================================================================")
    print(" WIZARD VIEW FIX COMPLETE ")
    print("==================================================================")

if __name__ == '__main__':
    main()
