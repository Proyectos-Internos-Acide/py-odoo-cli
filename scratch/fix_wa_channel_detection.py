import sys
import os
import base64
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    print("==================================================================")
    print(" Fixing Channel Detection: JS Anchored to Trigger Button Context ")
    print("==================================================================")

    client = OdooClient()
    client.connect()

    m_dc = client.search_read('ir.model', domain=[('model', '=', 'discuss.channel')], fields=['id'])[0]['id']
    wview_id = 2700
    sa697_id = client.search_read('ir.actions.server', domain=[('name', '=', 'WTK - Abrir Wizard Oportunidad desde WA')], fields=['id'])[0]['id']
    print(f"Server Action 697 ID: {sa697_id}")

    # -------------------------------------------------------------------------
    # Rebuild JS: Capture channelId anchored to the trigger button's DOM context
    # when the popover opens, NOT from URL hash or last clicked sidebar item
    # -------------------------------------------------------------------------
    js_thread_action = f"""/** @odoo-module **/
(function () {{
    "use strict";
    console.log("=== WTK WhatsApp Thread Action Options Menu v4 Loaded ===");

    // Store the channel ID captured at the moment the options "..." button is pressed
    let capturedChannelId = null;

    // Intercept every mousedown to catch which "..." button triggered the popover
    document.addEventListener('mousedown', function (e) {{
        const btn = e.target.closest('button, .btn, .o-dropdown--item, .o-mail-Discuss-sidebar-menu-button, [data-action], .fa-ellipsis-v');
        if (!btn) return;

        // Walk up the DOM from the button to find the parent thread/channel container
        const threadContainer = btn.closest(
            '[data-thread-id], [data-id], ' +
            '.o-mail-DiscussSidebarCategoryItem, ' +
            '.o-mail-Thread, ' +
            '.o-mail-DiscussSidebarItem, ' +
            '.o-mail-ChatWindow'
        );

        if (threadContainer) {{
            const tid = threadContainer.getAttribute('data-thread-id') || threadContainer.getAttribute('data-id');
            if (tid) {{
                capturedChannelId = parseInt(tid);
                console.log("[WTK] Captured channel ID from button context:", capturedChannelId);
                return;
            }}

            // Try dataset.threadId or dataset.id
            if (threadContainer.dataset && (threadContainer.dataset.threadId || threadContainer.dataset.id)) {{
                capturedChannelId = parseInt(threadContainer.dataset.threadId || threadContainer.dataset.id);
                console.log("[WTK] Captured channel ID from dataset:", capturedChannelId);
                return;
            }}
        }}

        // Fallback: capture from sidebar item text (channel name match)
        const sidebarItem = btn.closest('.o-mail-DiscussSidebarCategoryItem, .o-mail-DiscussSidebarItem');
        if (sidebarItem) {{
            const nameEl = sidebarItem.querySelector('span, .o-mail-DiscussSidebarCategoryItem-name');
            console.log("[WTK] Sidebar item found, name:", nameEl ? nameEl.innerText : 'n/a');
        }}

    }}, true);

    function injectMenuOptionInPopover() {{
        const popovers = document.querySelectorAll('.o-popover, .dropdown-menu, .o-mail-Discuss-popover');
        if (!popovers || popovers.length === 0) return;

        popovers.forEach((pop) => {{
            if (pop.querySelector('.o_wtk_thread_action_item')) return;

            const text = pop.innerText || "";
            if (
                text.includes("Silenciar conversación") ||
                text.includes("Invitar personas") ||
                text.includes("Renombrar hilo") ||
                text.includes("Agregar a favoritos")
            ) {{
                const item = document.createElement('a');
                item.className = 'dropdown-item o_wtk_thread_action_item d-flex align-items-center gap-2';
                item.href = '#';
                item.style.cssText = 'cursor: pointer; padding: 8px 12px; color: #333; font-weight: 500; text-decoration: none; display: flex; align-items: center; gap: 8px; border-top: 1px solid #f0f0f0;';
                item.innerHTML = '<i class="fa fa-briefcase text-primary" style="font-size:14px; width:16px;"></i> <span>➕ Crear Oportunidad CRM</span>';

                item.onclick = function (e) {{
                    e.preventDefault();
                    e.stopPropagation();
                    pop.style.display = 'none';

                    // Use the captured channel ID from the moment the "..." button was pressed
                    const channelId = capturedChannelId;
                    console.log("[WTK] Using captured channelId:", channelId);

                    let actionService = null;
                    try {{ actionService = window.odoo.__WOWL_DEBUG__.root.env.services.action; }} catch (err) {{}}
                    if (!actionService && window.owl && window.owl.Component) {{
                        try {{ actionService = owl.Component.env.services.action; }} catch (err) {{}}
                    }}

                    const context = {{
                        active_id: channelId || false,
                        active_ids: channelId ? [channelId] : [],
                        active_model: "discuss.channel",
                    }};

                    if (actionService) {{
                        actionService.doAction({sa697_id}, {{ additionalContext: context }});
                    }} else {{
                        window.location.href = "/web#action={sa697_id}&active_id=" + (channelId || '');
                    }}
                }};

                pop.appendChild(item);
            }}
        }});
    }}

    setInterval(injectMenuOptionInPopover, 400);
}})();
"""

    b64_js = base64.b64encode(js_thread_action.encode('utf-8')).decode('utf-8')

    atts = client.search_read('ir.attachment', domain=[('name', '=', 'wa_thread_action_wizard_menu.js')], fields=['id'])
    if atts:
        att_id = atts[0]['id']
        client.write('ir.attachment', [att_id], {'datas': b64_js, 'mimetype': 'application/javascript', 'public': True})
        print(f"Updated ir.attachment ID {att_id}")
    else:
        att_id = client.create('ir.attachment', {'name': 'wa_thread_action_wizard_menu.js', 'type': 'binary', 'datas': b64_js, 'mimetype': 'application/javascript', 'public': True})
        print(f"Created ir.attachment ID {att_id}")

    assets = client.search_read('ir.asset', domain=[('name', '=', 'wtk_wa_thread_action_wizard_menu')], fields=['id'])
    if assets:
        client.write('ir.asset', [assets[0]['id']], {'bundle': 'web.assets_backend', 'directive': 'append', 'path': f'/web/content/{att_id}/wa_thread_action_wizard_menu.js'})
        print(f"Updated ir.asset ID {assets[0]['id']}")
    else:
        asset_id = client.create('ir.asset', {'name': 'wtk_wa_thread_action_wizard_menu', 'bundle': 'web.assets_backend', 'directive': 'append', 'path': f'/web/content/{att_id}/wa_thread_action_wizard_menu.js'})
        print(f"Created ir.asset ID {asset_id}")

    # -------------------------------------------------------------------------
    # Server Action 697: Strict channel resolution - NO fallback to write_date desc
    # -------------------------------------------------------------------------
    code_open_wizard = f"""# Server Action 697: Abrir Wizard - Resolución Estricta del Canal
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
    raise UserError('No se pudo determinar la conversación de WhatsApp. Por favor haz clic en el menú de opciones directamente desde el chat.')

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

# Transcribir Chat para guardar en descripcion de oportunidad (invisible en el modal)
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
        rows.append("<tr style='border-bottom:1px solid #eee;'>" +
                    "<td style='padding:6px;font-size:12px;color:#888;white-space:nowrap;vertical-align:top;'>" + date_str + "</td>" +
                    "<td style='padding:6px;font-weight:bold;font-size:12px;color:#333;vertical-align:top;'>" + str(author) + ":</td>" +
                    "<td style='padding:6px;font-size:12px;color:#444;vertical-align:top;'>" + str(body) + "</td>" +
                    "</tr>")
    if rows:
        chat_html = (
            "<h4>Historial de WhatsApp (" + str(len(msgs)) + " mensajes)</h4>" +
            "<table style='width:100%;border-collapse:collapse;'>" +
            "".join(rows) +
            "</table>"
        )

# Pre-llenar nombre con el partner del canal abierto
partner_name = partner.name if partner else (channel.name if channel else raw_phone)
op_name = "[WhatsApp] - " + str(partner_name)

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

    client.write('ir.actions.server', [sa697_id], {'code': code_open_wizard, 'model_id': m_dc})
    print(f"Updated Server Action {sa697_id} - Strict channel resolution (no write_date fallback)")

    print("\n==================================================================")
    print(" CHANNEL DETECTION FIX COMPLETE ")
    print("==================================================================")

if __name__ == '__main__':
    main()
