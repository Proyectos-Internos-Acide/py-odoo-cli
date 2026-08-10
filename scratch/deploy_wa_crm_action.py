import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    print("==================================================================")
    print(" Deploying WA -> CRM Opportunity Action to Odoo (Production) ")
    print("==================================================================")
    
    client = OdooClient()
    client.connect()

    # -------------------------------------------------------------------------
    # Python code for the Server Action (RestrictedPython sandbox compliant)
    # -------------------------------------------------------------------------
    code_wa_to_crm = """# =============================================================
# ACCIÓN: Crear/Vincular Oportunidad CRM desde WhatsApp
# Modelo Soporte: discuss.channel, whatsapp.message, res.partner
# =============================================================

# 1. Determinar contexto y obtener Canal / Contacto / Teléfono
channel = False
partner = False
raw_phone = False
client_name = "Cliente WhatsApp"

target_record = record or (records[0] if records else False)

if target_record:
    if target_record._name == 'discuss.channel':
        channel = target_record
        partner = channel.whatsapp_partner_id
        raw_phone = channel.whatsapp_number or (partner.phone if partner else False)
        client_name = partner.name if partner else channel.name
    elif target_record._name == 'whatsapp.message':
        wa_msg = target_record
        raw_phone = wa_msg.mobile_number
        channel = env['discuss.channel'].search([('whatsapp_number', 'ilike', raw_phone)], limit=1)
        if channel:
            partner = channel.whatsapp_partner_id
    elif target_record._name == 'res.partner':
        partner = target_record
        raw_phone = partner.phone
        client_name = partner.name
        channel = env['discuss.channel'].search([('whatsapp_partner_id', '=', partner.id)], limit=1)

# Normalizar teléfono (extraer solo dígitos sin 'import re')
digits = ''.join(c for c in (raw_phone or '') if c.isdigit())
if len(digits) >= 9:
    search_digits = digits[-9:]  # Últimos 9 dígitos significativos
else:
    search_digits = digits

# 2. Control Anti-Duplicidad de Contacto (res.partner)
if not partner and search_digits:
    partners = env['res.partner'].search([('phone', 'ilike', search_digits)], limit=1)
    if partners:
        partner = partners[0]

if not partner and raw_phone:
    # Crear nuevo contacto si no existía
    partner_name = client_name if client_name and not client_name.startswith('51') and not client_name.startswith('+') else ("Contacto WA " + str(raw_phone))
    partner = env['res.partner'].create({
        'name': partner_name,
        'phone': raw_phone,
    })

# Asignar partner al canal si estaba desvinculado
if channel and partner and not channel.whatsapp_partner_id:
    channel.write({'whatsapp_partner_id': partner.id})

# 3. Transcribir Mensajes del Chat de WhatsApp (HTML)
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
                    "<td style='padding:4px; font-size:12px; color:#888;'>" + date_str + "</td>" +
                    "<td style='padding:4px; font-weight:bold; font-size:12px;'>" + str(author) + ":</td>" +
                    "<td style='padding:4px; font-size:12px;'>" + str(body) + "</td>" +
                    "</tr>")
    
    if rows:
        chat_html = (
            "<h4>💬 Historial de WhatsApp (" + str(len(msgs)) + " mensajes)</h4>" +
            "<table style='width:100%; border-collapse:collapse;'>" +
            "".join(rows) +
            "</table>"
        )

# 4. Control Anti-Duplicidad de Oportunidad CRM (crm.lead)
existing_lead = False

# Buscar por partner o por teléfono en leads no perdidos/cancelados
lost_stages = env['crm.stage'].search([('name', 'in', ['Cancelado', 'Clientes Perdidos', 'PERDIDO TOTALMENTE'])])
lost_stage_ids = lost_stages.ids if lost_stages else []

domain_lead = [('type', '=', 'opportunity')]
if lost_stage_ids:
    domain_lead.append(('stage_id', 'not in', lost_stage_ids))

if partner:
    lead_by_partner = env['crm.lead'].search(domain_lead + [('partner_id', '=', partner.id)], limit=1)
    if lead_by_partner:
        existing_lead = lead_by_partner[0]

if not existing_lead and search_digits:
    lead_by_phone = env['crm.lead'].search(domain_lead + [('phone', 'ilike', search_digits)], limit=1)
    if lead_by_phone:
        existing_lead = lead_by_phone[0]

# 5. Ejecutar Acción (Crear Nueva o Actualizar Existente)
target_lead = False

if existing_lead:
    # ── CASO A: Ya existe una Oportunidad activa (Actualizar) ──
    target_lead = existing_lead
    note_body = (
        "<b>🔄 Sincronización de WhatsApp:</b><br/>" +
        "Se solicitó vincular la conversación de WhatsApp (" + str(raw_phone or '') + ") a esta Oportunidad.<br/><br/>" +
        (chat_html or "")
    )
    target_lead.message_post(body=note_body, message_type='comment')
    
    if channel:
        channel.message_post(
            body="📌 <i>Se vinculó el chat a la Oportunidad existente: <b>#" + str(target_lead.id) + " - " + str(target_lead.name) + "</b></i>",
            message_type='comment'
        )
else:
    # ── CASO B: Crear Nueva Oportunidad CRM ──
    stage_new = env['crm.stage'].search([('name', 'ilike', 'Nuevo')], limit=1)
    if not stage_new:
        stage_new = env['crm.stage'].search([], order='sequence asc', limit=1)

    lead_name = "[WhatsApp] " + str(partner.name if partner else (client_name or raw_phone))
    
    lead_vals = {
        'name': lead_name,
        'partner_id': partner.id if partner else False,
        'phone': raw_phone or (partner.phone if partner else False),
        'type': 'opportunity',
        'stage_id': stage_new.id if stage_new else False,
        'user_id': env.user.id,
        'description': chat_html or "<i>Lead generado desde WhatsApp</i>",
    }
    
    target_lead = env['crm.lead'].create(lead_vals)
    
    if channel:
        channel.message_post(
            body="📌 <i>Nueva Oportunidad CRM creada: <b>#" + str(target_lead.id) + " - " + str(target_lead.name) + "</b> asignada a @" + str(env.user.name) + "</i>",
            message_type='comment'
        )

# 6. Devolver acción act_window para ABRIR la Oportunidad en pantalla
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

    action_name = "➕ Crear/Vincular Oportunidad CRM"
    model_dc_id = 231  # discuss.channel
    model_wm_id = 786  # whatsapp.message
    model_rp_id = 90   # res.partner

    # 1. Action for discuss.channel
    existing_sa = client.search_read(
        'ir.actions.server',
        domain=[('name', '=', action_name), ('model_id', '=', model_dc_id)],
        fields=['id']
    )

    if existing_sa:
        sa_id = existing_sa[0]['id']
        client.write('ir.actions.server', [sa_id], {
            'code': code_wa_to_crm,
            'binding_model_id': model_dc_id,
            'binding_view_types': 'form,list',
        })
        print(f"Updated existing Server Action ID: {sa_id} on discuss.channel")
    else:
        sa_id = client.create('ir.actions.server', {
            'name': action_name,
            'model_id': model_dc_id,
            'state': 'code',
            'code': code_wa_to_crm,
            'binding_model_id': model_dc_id,
            'binding_view_types': 'form,list',
        })
        print(f"Created new Server Action ID: {sa_id} on discuss.channel")

    # 2. Update/create for whatsapp.message (ID 656)
    existing_sa_wm = client.search_read(
        'ir.actions.server',
        domain=[('id', '=', 656)],
        fields=['id']
    )
    if existing_sa_wm:
        client.write('ir.actions.server', [656], {
            'code': code_wa_to_crm,
            'binding_model_id': model_wm_id,
            'binding_view_types': 'form,list',
        })
        print("Updated Server Action 656 on whatsapp.message")

    # 3. Action for res.partner
    existing_sa_rp = client.search_read(
        'ir.actions.server',
        domain=[('name', '=', action_name), ('model_id', '=', model_rp_id)],
        fields=['id']
    )
    if existing_sa_rp:
        client.write('ir.actions.server', [existing_sa_rp[0]['id']], {
            'code': code_wa_to_crm,
            'binding_model_id': model_rp_id,
            'binding_view_types': 'form,list',
        })
        print(f"Updated Server Action on res.partner (ID {existing_sa_rp[0]['id']})")
    else:
        sa_rp_id = client.create('ir.actions.server', {
            'name': action_name,
            'model_id': model_rp_id,
            'state': 'code',
            'code': code_wa_to_crm,
            'binding_model_id': model_rp_id,
            'binding_view_types': 'form,list',
        })
        print(f"Created new Server Action on res.partner (ID {sa_rp_id})")

    print("\n==================================================================")
    print(" DEPLOYMENT COMPLETE: Action bound to discuss.channel & partner ")
    print("==================================================================")

if __name__ == '__main__':
    main()
