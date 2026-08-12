import sys
import os
import base64
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    print("==================================================================")
    print(" JS v8: Position-based channel detection + timestamp staleness guard")
    print("==================================================================")

    client = OdooClient()
    client.connect()

    m_dc = client.search_read('ir.model', domain=[('model', '=', 'discuss.channel')], fields=['id'])[0]['id']
    sa697_id = client.search_read('ir.actions.server', domain=[('name', '=', 'WTK - Abrir Wizard Oportunidad desde WA')], fields=['id'])[0]['id']
    wview_id = 2700
    print(f"SA697 ID: {sa697_id}")

    js_v8 = f"""/** @odoo-module **/
(function () {{
    "use strict";
    console.log("=== WTK WhatsApp Thread Action v8 — Position-Based Detection ===");

    // ---- Channel Lookup Map (phone / name -> channelId) ----
    const wtkChannelMap = new Map();
    let mapLoaded = false;

    function buildChannelMap() {{
        fetch('/web/dataset/call_kw', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                jsonrpc: '2.0', method: 'call', id: 1,
                params: {{
                    model: 'discuss.channel',
                    method: 'search_read',
                    args: [[['channel_type', '=', 'whatsapp']]],
                    kwargs: {{ fields: ['id', 'name', 'whatsapp_number'], limit: 1000, context: {{}} }}
                }}
            }})
        }})
        .then(r => r.json())
        .then(data => {{
            if (!data.result) return;
            wtkChannelMap.clear();
            for (const ch of data.result) {{
                wtkChannelMap.set(ch.name.toLowerCase(), ch.id);
                if (ch.whatsapp_number) {{
                    wtkChannelMap.set(ch.whatsapp_number, ch.id);
                    const digits = ch.whatsapp_number.replace(/[^0-9]/g, '');
                    wtkChannelMap.set(digits, ch.id);
                    if (digits.length >= 9) wtkChannelMap.set(digits.slice(-9), ch.id);
                }}
            }}
            mapLoaded = true;
            console.log('[WTK] Channel map built:', wtkChannelMap.size, 'entries for', data.result.length, 'channels');
        }})
        .catch(e => console.error('[WTK] Channel map error:', e));
    }}

    buildChannelMap();
    setInterval(buildChannelMap, 120000);

    // ---- Resolve channelId from text ----
    function resolveFromText(text) {{
        if (!text || !mapLoaded) return null;
        // Extract phone from "Name (phone)" pattern
        const m = text.match(/\((\d{{7,}})\)/);
        if (m) {{
            const ph = m[1];
            if (wtkChannelMap.has(ph)) return wtkChannelMap.get(ph);
            const d = ph.replace(/[^0-9]/g, '');
            if (wtkChannelMap.has(d)) return wtkChannelMap.get(d);
            if (d.length >= 9 && wtkChannelMap.has(d.slice(-9))) return wtkChannelMap.get(d.slice(-9));
        }}
        // Try by name (first line only)
        const first = text.split('\\n')[0].trim().toLowerCase();
        if (first && wtkChannelMap.has(first)) return wtkChannelMap.get(first);
        return null;
    }}

    // ---- URL fallback ----
    function resolveFromUrl() {{
        const url = window.location.href;
        let m;
        m = url.match(/discuss\/channel-(\d+)/); if (m) return parseInt(m[1]);
        m = url.match(/discuss\/(\d+)/);           if (m) return parseInt(m[1]);
        return null;
    }}

    // ---- Find sidebar item by Y position proximity to element ----
    // Searches all sidebar items and returns the one whose rect overlaps the given Y range
    function findSidebarItemNearY(targetY, tolerance) {{
        const candidates = document.querySelectorAll(
            '.o-mail-DiscussSidebarCategoryItem, ' +
            '.o-mail-DiscussSidebarItem, ' +
            '[class*="SidebarCategoryItem"], ' +
            '[class*="SidebarItem"]'
        );
        let best = null;
        let bestDist = tolerance;
        for (const el of candidates) {{
            const r = el.getBoundingClientRect();
            const centerY = (r.top + r.bottom) / 2;
            const dist = Math.abs(centerY - targetY);
            if (dist < bestDist) {{
                bestDist = dist;
                best = el;
            }}
        }}
        return best;
    }}

    // ---- Hovered sidebar item with TIMESTAMP (prevent stale capture) ----
    let hoverCapture = {{ text: null, ts: 0 }};

    document.addEventListener('mouseover', function (e) {{
        const si = e.target.closest(
            '.o-mail-DiscussSidebarCategoryItem, ' +
            '.o-mail-DiscussSidebarItem, ' +
            '[class*="SidebarCategoryItem"], ' +
            '[class*="SidebarItem"]'
        );
        if (si) {{
            hoverCapture = {{ text: si.innerText.trim(), ts: Date.now() }};
        }}
    }}, true);

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

            let channelId = null;
            let source = 'none';

            // Strategy 1: Position-based — find sidebar item closest to the popover
            const popRect = pop.getBoundingClientRect();
            const popCenterY = (popRect.top + popRect.bottom) / 2;

            // The popover appears to the RIGHT of the sidebar. Look for sidebar items
            // at approximately the same Y position.
            const nearItem = findSidebarItemNearY(popCenterY, 80);
            if (nearItem) {{
                const nearText = nearItem.innerText.trim();
                const id = resolveFromText(nearText);
                if (id) {{
                    channelId = id;
                    source = 'position-match:' + nearText.split('\\n')[0];
                }}
            }}

            // Strategy 2: Recent hover capture (only if < 3 seconds old)
            if (!channelId && hoverCapture.text && (Date.now() - hoverCapture.ts) < 3000) {{
                const id = resolveFromText(hoverCapture.text);
                if (id) {{
                    channelId = id;
                    source = 'hover:' + hoverCapture.text.split('\\n')[0];
                }}
            }}

            // Strategy 3: URL
            if (!channelId) {{
                const id = resolveFromUrl();
                if (id) {{ channelId = id; source = 'url'; }}
            }}

            console.log('[WTK] channelId =', channelId, '| source:', source, '| mapLoaded:', mapLoaded);

            const item = document.createElement('a');
            item.className = 'dropdown-item o_wtk_thread_action_item';
            item.href = '#';
            item.setAttribute('role', 'menuitem');
            item.innerHTML = '<i class="fa fa-handshake-o"></i> Crear Oportunidad CRM';

            const finalChannelId = channelId; // closure at injection time

            item.onclick = function (e) {{
                e.preventDefault();
                e.stopPropagation();
                pop.style.display = 'none';

                console.log('[WTK] Click: finalChannelId =', finalChannelId);

                if (!finalChannelId) {{
                    console.warn('[WTK] No channelId — cannot open wizard');
                    return;
                }}

                let svc = null;
                try {{ svc = window.odoo.__WOWL_DEBUG__.root.env.services.action; }} catch(e) {{}}
                if (!svc && window.owl && window.owl.Component) {{
                    try {{ svc = owl.Component.env.services.action; }} catch(e) {{}}
                }}

                const ctx = {{
                    active_id: finalChannelId,
                    active_ids: [finalChannelId],
                    active_model: 'discuss.channel',
                }};

                if (svc) {{
                    svc.doAction({sa697_id}, {{ additionalContext: ctx }});
                }} else {{
                    window.location.href = '/web#action={sa697_id}&active_id=' + finalChannelId;
                }}
            }};

            pop.appendChild(item);
        }});
    }}

    setInterval(injectMenuOptionInPopover, 400);
}})();
"""

    b64_js = base64.b64encode(js_v8.encode('utf-8')).decode('utf-8')

    atts = client.search_read('ir.attachment', domain=[('name', '=', 'wa_thread_action_wizard_menu.js')], fields=['id'])
    att_id = atts[0]['id']
    client.write('ir.attachment', [att_id], {'datas': b64_js, 'mimetype': 'application/javascript', 'public': True})
    print(f"Updated ir.attachment ID {att_id} (JS v8)")

    # SA 697 stays the same — no changes needed on server side
    print("\n==================================================================")
    print(" JS v8 DEPLOYED — Position-based sidebar item detection         ")
    print("==================================================================")

if __name__ == '__main__':
    main()
