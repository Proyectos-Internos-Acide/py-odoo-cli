import sys
import os
import base64
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    print("==================================================================")
    print(" JS v7: Channel Map + Sidebar Hover Text Matching (Definitive Fix)")
    print("==================================================================")

    client = OdooClient()
    client.connect()

    m_dc = client.search_read('ir.model', domain=[('model', '=', 'discuss.channel')], fields=['id'])[0]['id']
    sa697_id = client.search_read('ir.actions.server', domain=[('name', '=', 'WTK - Abrir Wizard Oportunidad desde WA')], fields=['id'])[0]['id']
    wview_id = 2700
    print(f"SA697 ID: {sa697_id}")

    # -------------------------------------------------------------------------
    # JS Strategy v7:
    # 1. On load: fetch ALL WhatsApp channels via JSON-RPC and build a lookup Map
    #    { phone: id, name.toLowerCase(): id, last9digits: id }
    # 2. Track mouseover on sidebar items to capture hovered item innerText
    # 3. When popover is detected, resolve channelId from hovered text (phone or name match)
    # 4. Close the channelId in the click handler at INJECTION TIME
    # 5. Fallback: URL parse
    # -------------------------------------------------------------------------
    js_v7 = f"""/** @odoo-module **/
(function () {{
    "use strict";
    console.log("=== WTK WhatsApp Thread Action v7 — Channel Map Loaded ===");

    // ---- Channel Lookup Map ----
    const wtkChannelMap = new Map();  // key -> channelId
    let mapLoaded = false;

    function buildChannelMap() {{
        // Use Odoo's session cookie/CSRF from meta tag or window.odoo
        const csrfToken = (window.odoo && window.odoo.csrf_token) || '';

        fetch('/web/dataset/call_kw', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                jsonrpc: '2.0', method: 'call', id: 1,
                params: {{
                    model: 'discuss.channel',
                    method: 'search_read',
                    args: [[['channel_type', '=', 'whatsapp']]],
                    kwargs: {{
                        fields: ['id', 'name', 'whatsapp_number'],
                        limit: 1000,
                        context: {{}}
                    }}
                }}
            }})
        }})
        .then(r => r.json())
        .then(data => {{
            if (!data.result) return;
            for (const ch of data.result) {{
                // By full name (lowercase)
                wtkChannelMap.set(ch.name.toLowerCase(), ch.id);

                if (ch.whatsapp_number) {{
                    // By full phone number
                    wtkChannelMap.set(ch.whatsapp_number, ch.id);

                    // By digits only
                    const digits = ch.whatsapp_number.replace(/\D/g, '');
                    wtkChannelMap.set(digits, ch.id);

                    // By last 9 digits
                    if (digits.length >= 9) {{
                        wtkChannelMap.set(digits.slice(-9), ch.id);
                    }}
                }}
            }}
            mapLoaded = true;
            console.log('[WTK] Channel map built:', wtkChannelMap.size, 'entries for', data.result.length, 'channels');
        }})
        .catch(e => console.error('[WTK] Channel map build error:', e));
    }}

    // Build map at load and refresh periodically
    buildChannelMap();
    setInterval(buildChannelMap, 120000); // refresh every 2 minutes

    // ---- Track hovered sidebar item text ----
    let hoveredSidebarText = null;
    let lastClickedSidebarText = null;

    document.addEventListener('mouseover', function (e) {{
        const item = e.target.closest(
            '.o-mail-DiscussSidebarCategoryItem, ' +
            '.o-mail-DiscussSidebarItem, ' +
            '[class*="SidebarChannel"], ' +
            '[class*="SidebarThread"]'
        );
        if (item) {{
            hoveredSidebarText = item.innerText.trim();
        }}
    }}, true);

    document.addEventListener('mousedown', function (e) {{
        const item = e.target.closest(
            '.o-mail-DiscussSidebarCategoryItem, ' +
            '.o-mail-DiscussSidebarItem, ' +
            '[class*="SidebarChannel"], ' +
            '[class*="SidebarThread"]'
        );
        if (item) {{
            lastClickedSidebarText = item.innerText.trim();
        }}
    }}, true);

    // ---- Resolve channelId from text ----
    function resolveChannelFromText(text) {{
        if (!text || !mapLoaded) return null;

        // Extract phone number from text: "Dennis (32477514418)" → "32477514418"
        const phoneMatch = text.match(/\((\d{{6,}})\)/);
        if (phoneMatch) {{
            const phone = phoneMatch[1];
            if (wtkChannelMap.has(phone)) return wtkChannelMap.get(phone);
            const digits = phone.replace(/\D/g, '');
            if (wtkChannelMap.has(digits)) return wtkChannelMap.get(digits);
            if (digits.length >= 9 && wtkChannelMap.has(digits.slice(-9))) {{
                return wtkChannelMap.get(digits.slice(-9));
            }}
        }}

        // Try full name (lowercase)
        const lower = text.toLowerCase().trim();
        if (wtkChannelMap.has(lower)) return wtkChannelMap.get(lower);

        // Partial: find first line (channel name) and match
        const firstLine = lower.split('\\n')[0].trim();
        if (firstLine && wtkChannelMap.has(firstLine)) return wtkChannelMap.get(firstLine);

        // Substring match (the text might contain the channel name)
        for (const [key, id] of wtkChannelMap.entries()) {{
            if (key.length > 3 && lower.includes(key)) return id;
        }}

        return null;
    }}

    // ---- URL-based fallback ----
    function resolveChannelFromUrl() {{
        const url = window.location.href;
        let m;
        m = url.match(/discuss\/channel-(\d+)/); if (m) return parseInt(m[1]);
        m = url.match(/discuss\/(\d+)/); if (m) return parseInt(m[1]);
        m = url.match(/[#&?]active_id[=%](\d+)/); if (m) return parseInt(m[1]);
        return null;
    }}

    // ---- OWL store fallback ----
    function resolveChannelFromStore() {{
        try {{
            const debug = window.odoo && window.odoo.__WOWL_DEBUG__;
            if (!debug) return null;
            const env = debug.root.env;
            const services = env.services;

            // Try messaging/store
            const store = services.store || services.messaging;
            if (!store) return null;

            const discuss = store.discuss || store['mail.discuss'];
            if (!discuss) return null;

            const t = discuss.thread || discuss.activeThread || discuss.channel;
            if (t && t.id) return t.id;
        }} catch(e) {{}}
        return null;
    }}

    // ---- Main Popover Injection ----
    function injectMenuOptionInPopover() {{
        const popovers = document.querySelectorAll('.o-popover, .dropdown-menu');
        if (!popovers.length) return;

        popovers.forEach((pop) => {{
            if (pop.querySelector('.o_wtk_thread_action_item')) return;

            const text = pop.innerText || '';
            const isDiscussMenu = (
                text.includes('Silenciar') ||
                text.includes('Invitar personas') ||
                text.includes('Renombrar hilo') ||
                text.includes('Agregar a favoritos') ||
                text.includes('Ocultar hasta nuevo mensaje') ||
                text.includes('Ajustes avanzados')
            );
            if (!isDiscussMenu) return;

            // Resolve channelId using all strategies at injection time
            let channelId = null;

            // 1. From hovered/clicked sidebar text (PRIMARY strategy)
            channelId = resolveChannelFromText(hoveredSidebarText || lastClickedSidebarText);
            if (channelId) console.log('[WTK] channelId from sidebar text:', channelId, '| text:', hoveredSidebarText);

            // 2. From URL
            if (!channelId) {{
                channelId = resolveChannelFromUrl();
                if (channelId) console.log('[WTK] channelId from URL:', channelId);
            }}

            // 3. From OWL store
            if (!channelId) {{
                channelId = resolveChannelFromStore();
                if (channelId) console.log('[WTK] channelId from OWL store:', channelId);
            }}

            console.log('[WTK] Final resolved channelId:', channelId, '| mapLoaded:', mapLoaded);

            const item = document.createElement('a');
            item.className = 'dropdown-item o_wtk_thread_action_item';
            item.href = '#';
            item.setAttribute('role', 'menuitem');
            item.innerHTML = '<i class="fa fa-handshake-o"></i> Crear Oportunidad CRM';

            // Closure: capture channelId at INJECTION time
            const finalChannelId = channelId;
            item.onclick = function (e) {{
                e.preventDefault();
                e.stopPropagation();
                pop.style.display = 'none';

                console.log('[WTK] Click: finalChannelId =', finalChannelId);

                if (!finalChannelId) {{
                    // Last resort: re-resolve at click time
                    const retryId = resolveChannelFromText(hoveredSidebarText || lastClickedSidebarText)
                                 || resolveChannelFromUrl()
                                 || resolveChannelFromStore();
                    if (!retryId) {{
                        console.error('[WTK] Could not resolve channelId at click time either');
                        return;
                    }}
                    triggerAction(retryId);
                    return;
                }}
                triggerAction(finalChannelId);
            }};

            pop.appendChild(item);
        }});
    }}

    function triggerAction(channelId) {{
        let svc = null;
        try {{ svc = window.odoo.__WOWL_DEBUG__.root.env.services.action; }} catch(e) {{}}
        if (!svc && window.owl && window.owl.Component) {{
            try {{ svc = owl.Component.env.services.action; }} catch(e) {{}}
        }}

        const ctx = {{
            active_id: channelId,
            active_ids: [channelId],
            active_model: 'discuss.channel',
        }};

        if (svc) {{
            svc.doAction({sa697_id}, {{ additionalContext: ctx }});
        }} else {{
            window.location.href = '/web#action={sa697_id}&active_id=' + channelId;
        }}
    }}

    setInterval(injectMenuOptionInPopover, 400);
}})();
"""

    b64_js = base64.b64encode(js_v7.encode('utf-8')).decode('utf-8')

    atts = client.search_read('ir.attachment', domain=[('name', '=', 'wa_thread_action_wizard_menu.js')], fields=['id'])
    att_id = atts[0]['id']
    client.write('ir.attachment', [att_id], {'datas': b64_js, 'mimetype': 'application/javascript', 'public': True})
    print(f"Updated ir.attachment ID {att_id} (JS v7)")

    print("\n==================================================================")
    print(" JS v7 DEPLOYED — Channel Map + Sidebar Hover Text Matching      ")
    print("==================================================================")

if __name__ == '__main__':
    main()
