import sys
import os
import base64
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    print("==================================================================")
    print(" Fixing JS: Channel ID from OWL Component & URL — No DOM attributes")
    print("==================================================================")

    client = OdooClient()
    client.connect()

    sa697_id = client.search_read('ir.actions.server', domain=[('name', '=', 'WTK - Abrir Wizard Oportunidad desde WA')], fields=['id'])[0]['id']
    print(f"Server Action 697 ID: {sa697_id}")

    # -------------------------------------------------------------------------
    # New JS Strategy:
    # 1. When the options "..." button is pressed, walk up DOM to find the nearest
    #    OWL component node (__owl__) and read thread.id from it.
    # 2. Fallback: parse URL hash
    # 3. Fallback: read the active thread title from the chat header and match by name
    # -------------------------------------------------------------------------
    js_thread_action = f"""/** @odoo-module **/
(function () {{
    "use strict";
    console.log("=== WTK WhatsApp Thread Action Options Menu v5 Loaded ===");

    let capturedChannelId = null;

    // Helper: walk up DOM tree and try to extract channel ID from OWL component
    function getChannelIdFromEl(el) {{
        let node = el;
        while (node && node !== document.body) {{
            // Check OWL component instance
            if (node.__owl__) {{
                try {{
                    const comp = node.__owl__;
                    // Try thread.id directly
                    if (comp.component && comp.component.thread && comp.component.thread.id) {{
                        return comp.component.thread.id;
                    }}
                    if (comp.component && comp.component.props && comp.component.props.thread && comp.component.props.thread.id) {{
                        return comp.component.props.thread.id;
                    }}
                    if (comp.component && comp.component.channel && comp.component.channel.id) {{
                        return comp.component.channel.id;
                    }}
                }} catch(e) {{}}
            }}
            // Check for direct data attributes (just in case)
            const tid = node.getAttribute('data-thread-id') || node.getAttribute('data-id') || node.getAttribute('data-channel-id');
            if (tid && !isNaN(parseInt(tid))) {{
                return parseInt(tid);
            }}
            node = node.parentElement;
        }}
        return null;
    }}

    // Helper: get active channel ID from URL
    function getChannelIdFromUrl() {{
        const url = window.location.href;
        // Odoo 17 SPA format: /odoo/discuss/channel-NNN or ?id=NNN
        let m = url.match(/discuss\/channel-(\d+)/);
        if (m) return parseInt(m[1]);
        m = url.match(/discuss\/(\d+)/);
        if (m) return parseInt(m[1]);
        m = url.match(/[#&?]id=(\d+)/);
        if (m) return parseInt(m[1]);
        m = url.match(/discuss\.channel\/(\d+)/);
        if (m) return parseInt(m[1]);
        return null;
    }}

    // Helper: get the active channel ID from OWL root env store
    function getChannelIdFromOWLStore() {{
        try {{
            const root = window.odoo.__WOWL_DEBUG__.root;
            const env = root.env;
            if (env && env.store) {{
                const store = env.store;
                // Try to find the active thread from the store
                if (store.discuss && store.discuss.thread && store.discuss.thread.id) {{
                    return store.discuss.thread.id;
                }}
                if (store.discuss && store.discuss.activeThread && store.discuss.activeThread.id) {{
                    return store.discuss.activeThread.id;
                }}
            }}
        }} catch(e) {{}}
        return null;
    }}

    // Track mousedown on the options "..." button and immediately capture the channel
    document.addEventListener('mousedown', function (e) {{
        const btn = e.target.closest('button, i.fa-ellipsis');
        if (!btn) return;

        // Only capture when clicking the 3-dots options button (has ellipsis icon)
        const hasEllipsis = btn.querySelector('i.fa-ellipsis, i.fa-ellipsis-v, i.fa-ellipsis-h') ||
                            btn.classList.contains('fa-ellipsis') ||
                            btn.classList.contains('fa-ellipsis-v') ||
                            btn.matches('[title*="opciones"], [title*="Options"], [aria-label*="opciones"], [aria-label*="More"]');

        // Try to get channel from OWL component tree starting from this button
        const fromOwl = getChannelIdFromEl(btn);
        if (fromOwl) {{
            capturedChannelId = fromOwl;
            console.log("[WTK] Captured channelId from OWL component:", capturedChannelId);
            return;
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
                // When popover is visible, also try to get channel from URL or OWL store
                const fromUrl = getChannelIdFromUrl();
                const fromStore = getChannelIdFromOWLStore();
                
                if (fromUrl && !capturedChannelId) capturedChannelId = fromUrl;
                if (fromStore && !capturedChannelId) capturedChannelId = fromStore;

                const item = document.createElement('a');
                item.className = 'dropdown-item o_wtk_thread_action_item d-flex align-items-center gap-2';
                item.href = '#';
                item.style.cssText = 'cursor: pointer; padding: 8px 12px; color: #333; font-weight: 500; text-decoration: none; display: flex; align-items: center; gap: 8px; border-top: 1px solid #f0f0f0;';
                item.innerHTML = '<i class="fa fa-briefcase text-primary" style="font-size:14px; width:16px;"></i> <span>➕ Crear Oportunidad CRM</span>';

                item.onclick = function (e) {{
                    e.preventDefault();
                    e.stopPropagation();
                    pop.style.display = 'none';

                    // Resolve channel ID at click time (all 3 strategies)
                    const channelId = capturedChannelId || getChannelIdFromUrl() || getChannelIdFromOWLStore();
                    console.log("[WTK] Final channelId at click:", channelId, "| captured:", capturedChannelId, "| url:", getChannelIdFromUrl(), "| store:", getChannelIdFromOWLStore());

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

    # -------------------------------------------------------------------------
    # Server Action 697: Keep strict resolution but allow URL context too
    # -------------------------------------------------------------------------
    m_dc = client.search_read('ir.model', domain=[('model', '=', 'discuss.channel')], fields=['id'])[0]['id']
    wview_id = 2700

    code_open_wizard = f"""# Server Action 697: Abrir Wizard - Resolución Robusta del Canal
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
    raise UserError('No se pudo determinar la conversación de WhatsApp. Por favor abre el chat directamente y usa las opciones desde dentro de la conversación.')

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
    print(f"Updated Server Action {sa697_id}")

    print("\n==================================================================")
    print(" JS FIX v5 DEPLOYED — OWL Component + URL + Store strategies  ")
    print("==================================================================")

if __name__ == '__main__':
    main()
