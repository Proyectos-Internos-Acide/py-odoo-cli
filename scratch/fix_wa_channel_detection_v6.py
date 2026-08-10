import sys
import os
import base64
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    print("==================================================================")
    print(" JS v6: threadActionsRegistry approach + robust IIFE fallback     ")
    print("==================================================================")

    client = OdooClient()
    client.connect()

    m_dc = client.search_read('ir.model', domain=[('model', '=', 'discuss.channel')], fields=['id'])[0]['id']
    sa697_id = client.search_read('ir.actions.server', domain=[('name', '=', 'WTK - Abrir Wizard Oportunidad desde WA')], fields=['id'])[0]['id']
    wview_id = 2700
    print(f"SA697 ID: {sa697_id}")

    # -------------------------------------------------------------------------
    # Strategy:
    # 1. Try to register via threadActionsRegistry (proper Odoo 17 way)
    #    - gets thread.id directly, 100% reliable
    # 2. ALSO keep IIFE popover injection as fallback
    #    - capture channelId AT INJECTION TIME (when popover appears) using
    #      document.activeElement + OWL component traversal
    # -------------------------------------------------------------------------

    js_thread_action = f"""/** @odoo-module **/

// ============================================================
// Strategy A: Native threadActionsRegistry (Odoo 17/18)
// ============================================================
(function() {{
    "use strict";

    function tryRegisterThreadAction() {{
        try {{
            const {{ threadActionsRegistry }} = odoo.loader.modules.get("@mail/core/common/thread_actions") || {{}};
            if (!threadActionsRegistry) {{
                console.log("[WTK] threadActionsRegistry not available yet, will retry via IIFE fallback");
                return false;
            }}

            if (threadActionsRegistry.contains("wtk_create_opportunity_crm")) {{
                return true; // already registered
            }}

            threadActionsRegistry.add("wtk_create_opportunity_crm", {{
                condition: (component) => {{
                    try {{
                        return component.thread && component.thread.channel_type === "whatsapp";
                    }} catch(e) {{ return false; }}
                }},
                icon: "fa-briefcase",
                label: "➕ Crear Oportunidad CRM",
                sequence: 99,
                action: async (component) => {{
                    try {{
                        const channelId = component.thread.id;
                        console.log("[WTK] threadActionsRegistry: channelId =", channelId);
                        await component.env.services.action.doAction({sa697_id}, {{
                            additionalContext: {{
                                active_id: channelId,
                                active_ids: [channelId],
                                active_model: "discuss.channel",
                            }},
                        }});
                    }} catch(err) {{
                        console.error("[WTK] Error in threadActionsRegistry action:", err);
                    }}
                }},
            }});

            console.log("[WTK] Registered via threadActionsRegistry");
            return true;
        }} catch(e) {{
            console.log("[WTK] threadActionsRegistry registration failed:", e.message);
            return false;
        }}
    }}

    // Retry registration until modules are loaded
    let attempts = 0;
    const interval = setInterval(() => {{
        attempts++;
        if (tryRegisterThreadAction() || attempts > 30) {{
            clearInterval(interval);
        }}
    }}, 500);
}})();

// ============================================================
// Strategy B: IIFE Popover Injection Fallback
// Captures channel ID at injection time using multiple methods
// ============================================================
(function () {{
    "use strict";
    console.log("=== WTK WhatsApp Thread Action Popover Injection v6 Loaded ===");

    // Walk up from an element through OWL __owl__ component instances
    function getChannelIdFromOwlTree(startEl) {{
        let node = startEl;
        for (let i = 0; i < 30 && node && node !== document.body; i++) {{
            // Check __owl__ component (Odoo 17 OWL)
            if (node.__owl__) {{
                try {{
                    const comp = node.__owl__;
                    const c = comp.component;
                    if (!c) {{ node = node.parentElement; continue; }}

                    // Direct thread prop
                    if (c.thread && c.thread.id && c.thread.channel_type === "whatsapp") return c.thread.id;
                    if (c.props && c.props.thread && c.props.thread.id) return c.props.thread.id;

                    // State-based thread
                    if (c.state && c.state.thread && c.state.thread.id) return c.state.thread.id;

                    // Channel directly
                    if (c.channel && c.channel.id) return c.channel.id;
                    if (c.props && c.props.channel && c.props.channel.id) return c.props.channel.id;
                }} catch(e) {{}}
            }}
            node = node.parentElement;
        }}
        return null;
    }}

    // Get channel ID from OWL discuss store (active thread)
    function getChannelIdFromStore() {{
        try {{
            const env = window.odoo.__WOWL_DEBUG__.root.env;
            if (!env) return null;

            // Try env.store paths (varies by Odoo version)
            const store = env.store || (env.services && env.services.store);
            if (!store) return null;

            const discuss = store.discuss || store.messaging;
            if (!discuss) return null;

            const t = discuss.thread || discuss.activeThread || discuss.currentChannel;
            if (t && t.id && t.channel_type === "whatsapp") return t.id;
        }} catch(e) {{}}
        return null;
    }}

    // Parse channel ID from URL
    function getChannelIdFromUrl() {{
        const url = window.location.href;
        let m;
        m = url.match(/discuss\/channel-(\d+)/); if (m) return parseInt(m[1]);
        m = url.match(/discuss\/(\d+)/); if (m) return parseInt(m[1]);
        m = url.match(/[#&?]active_id=(\d+)/); if (m) return parseInt(m[1]);
        return null;
    }}

    function injectMenuOptionInPopover() {{
        const popovers = document.querySelectorAll('.o-popover, .dropdown-menu, .o-mail-Discuss-popover');
        if (!popovers || popovers.length === 0) return;

        popovers.forEach((pop) => {{
            if (pop.querySelector('.o_wtk_thread_action_item')) return;

            const text = pop.innerText || "";
            const isDiscussPopover = (
                text.includes("Silenciar conversación") ||
                text.includes("Invitar personas") ||
                text.includes("Renombrar hilo") ||
                text.includes("Agregar a favoritos") ||
                text.includes("Ocultar hasta nuevo mensaje")
            );
            if (!isDiscussPopover) return;

            // === Capture channel ID using all available strategies at injection time ===
            // 1. From active element (the button that triggered the popover is still activeElement)
            const activeEl = document.activeElement;
            let channelId = activeEl ? getChannelIdFromOwlTree(activeEl) : null;

            // 2. From OWL store (active discuss thread)
            if (!channelId) channelId = getChannelIdFromStore();

            // 3. From URL
            if (!channelId) channelId = getChannelIdFromUrl();

            // 4. From all visible sidebar items: find the one with .active/.bg-primary class
            if (!channelId) {{
                const activeItem = document.querySelector(
                    '.o-mail-DiscussSidebarCategoryItem.active, ' +
                    '.o-mail-DiscussSidebarCategoryItem.o-active, ' +
                    '.o-mail-DiscussSidebarCategoryItem.bg-primary, ' +
                    '.o-mail-DiscussSidebarItem.active'
                );
                if (activeItem) channelId = getChannelIdFromOwlTree(activeItem);
            }}

            // 5. From the popover's anchor position: find thread item under the popover
            if (!channelId) {{
                const rect = pop.getBoundingClientRect();
                const anchorX = rect.left - 50;
                const anchorY = rect.top + rect.height / 2;
                const elAtAnchor = document.elementFromPoint(anchorX, anchorY);
                if (elAtAnchor) channelId = getChannelIdFromOwlTree(elAtAnchor);
            }}

            console.log("[WTK] Injecting option, resolved channelId:", channelId);

            const item = document.createElement('a');
            item.className = 'dropdown-item o_wtk_thread_action_item d-flex align-items-center gap-2';
            item.href = '#';
            item.style.cssText = 'cursor:pointer;padding:8px 12px;color:#333;font-weight:500;text-decoration:none;display:flex;align-items:center;gap:8px;border-top:1px solid #f0f0f0;';
            item.innerHTML = '<i class="fa fa-briefcase text-primary" style="font-size:14px;width:16px;"></i> <span>➕ Crear Oportunidad CRM</span>';

            // Closure over channelId captured at injection time
            const resolvedId = channelId;
            item.onclick = function (e) {{
                e.preventDefault();
                e.stopPropagation();
                pop.style.display = 'none';

                console.log("[WTK] Click: using resolvedId =", resolvedId);

                let actionService = null;
                try {{ actionService = window.odoo.__WOWL_DEBUG__.root.env.services.action; }} catch(err) {{}}
                if (!actionService && window.owl && window.owl.Component) {{
                    try {{ actionService = owl.Component.env.services.action; }} catch(err) {{}}
                }}

                const ctx = {{
                    active_id: resolvedId || false,
                    active_ids: resolvedId ? [resolvedId] : [],
                    active_model: "discuss.channel",
                }};

                if (actionService && resolvedId) {{
                    actionService.doAction({sa697_id}, {{ additionalContext: ctx }});
                }} else if (!resolvedId) {{
                    alert("No se pudo detectar el canal. Por favor abre el chat y prueba desde dentro.");
                }} else {{
                    window.location.href = "/web#action={sa697_id}&active_id=" + resolvedId;
                }}
            }};

            pop.appendChild(item);
        }});
    }}

    setInterval(injectMenuOptionInPopover, 400);
}})();
"""

    b64_js = base64.b64encode(js_thread_action.encode('utf-8')).decode('utf-8')

    atts = client.search_read('ir.attachment', domain=[('name', '=', 'wa_thread_action_wizard_menu.js')], fields=['id'])
    att_id = atts[0]['id']
    client.write('ir.attachment', [att_id], {'datas': b64_js, 'mimetype': 'application/javascript', 'public': True})
    print(f"Updated ir.attachment ID {att_id} (JS v6)")

    # -------------------------------------------------------------------------
    # Server Action 697: Remove UserError — use fallback if no channel found
    # -------------------------------------------------------------------------
    code_open_wizard = f"""# Server Action 697: Abrir Wizard - Resolución Robusta
channel = False

target_rec = record or (records[0] if records else False)
if target_rec and target_rec._name == 'discuss.channel':
    channel = target_rec

if not channel:
    active_id = env.context.get('active_id')
    if active_id and isinstance(active_id, int):
        try:
            ch = env['discuss.channel'].browse(active_id)
            if ch and ch.exists():
                channel = ch
        except Exception:
            pass

# Fallback: last WhatsApp channel the current user interacted with
if not channel:
    member_channels = env['discuss.channel.member'].search([
        ('partner_id', '=', env.user.partner_id.id),
        ('channel_id.channel_type', '=', 'whatsapp'),
    ], order='last_seen_dt desc', limit=1)
    if member_channels:
        channel = member_channels[0].channel_id

if not channel:
    raise UserError('No se pudo determinar la conversación de WhatsApp.')

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
    print(" JS v6 DEPLOYED — threadActionsRegistry + 5-strategy IIFE fallback")
    print("==================================================================")

if __name__ == '__main__':
    main()
