import sys
import os
import base64
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    print("==================================================================")
    print(" JS v9: elementsFromPoint on trigger button + broad sidebar scan  ")
    print("==================================================================")

    client = OdooClient()
    client.connect()

    sa697_id = client.search_read('ir.actions.server', domain=[('name', '=', 'WTK - Abrir Wizard Oportunidad desde WA')], fields=['id'])[0]['id']
    print(f"SA697 ID: {sa697_id}")

    js_v9 = f"""/** @odoo-module **/
(function () {{
    "use strict";
    console.log("=== WTK WhatsApp Thread Action v9 ===");

    // ---- Channel Lookup Map ----
    const wtkMap = new Map();   // phone/name -> channelId
    let mapLoaded = false;

    function buildMap() {{
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
            wtkMap.clear();
            for (const ch of data.result) {{
                wtkMap.set(ch.name.toLowerCase().trim(), ch.id);
                if (ch.whatsapp_number) {{
                    const d = ch.whatsapp_number.replace(/[^0-9]/g, '');
                    wtkMap.set(ch.whatsapp_number, ch.id);
                    wtkMap.set(d, ch.id);
                    if (d.length >= 9) wtkMap.set(d.slice(-9), ch.id);
                }}
            }}
            mapLoaded = true;
            console.log('[WTK] Map ready:', wtkMap.size, 'keys for', data.result.length, 'channels');
        }})
        .catch(e => console.error('[WTK] Map error:', e));
    }}
    buildMap();
    setInterval(buildMap, 120000);

    // ---- Resolve from any text block ----
    function resolveFromText(text) {{
        if (!text || !mapLoaded) return null;
        // Extract phone like (51969614372) or (969614372)
        const phones = text.match(/\((\d{{7,15}})\)/g) || [];
        for (const p of phones) {{
            const num = p.replace(/[^0-9]/g, '');
            if (wtkMap.has(num)) return wtkMap.get(num);
            if (num.length >= 9 && wtkMap.has(num.slice(-9))) return wtkMap.get(num.slice(-9));
        }}
        // Try full lines as channel name
        for (const line of text.split('\\n')) {{
            const l = line.trim().toLowerCase();
            if (l.length > 2 && wtkMap.has(l)) return wtkMap.get(l);
        }}
        return null;
    }}

    // ---- URL fallback ----
    function resolveFromUrl() {{
        const u = window.location.href;
        let m;
        m = u.match(/discuss\/channel-(\d+)/); if (m) return parseInt(m[1]);
        m = u.match(/discuss\/(\d+)/);          if (m) return parseInt(m[1]);
        return null;
    }}

    // ---- Main: resolve channel for a given popover ----
    function resolveChannelForPopover(pop) {{
        const pr = pop.getBoundingClientRect();

        // Strategy 1: elementsFromPoint to the LEFT of the popover
        // (where the ... button / sidebar item is)
        const checkPoints = [
            [pr.left - 15, pr.top + 5],
            [pr.left - 30, pr.top + 5],
            [pr.left - 50, pr.top + 5],
            [pr.left - 80, pr.top + 5],
            [pr.left - 15, (pr.top + pr.bottom) / 2],
            [pr.left - 50, (pr.top + pr.bottom) / 2],
        ];

        for (const [x, y] of checkPoints) {{
            const els = document.elementsFromPoint(x, y);
            for (const el of els) {{
                if (el === pop || pop.contains(el)) continue;
                const txt = el.innerText || el.textContent || '';
                const id = resolveFromText(txt.trim());
                if (id) {{
                    console.log('[WTK] S1 elementsFromPoint [' + x + ',' + y + ']:', id, '| text:', txt.trim().split('\\n')[0]);
                    return id;
                }}
            }}
        }}

        // Strategy 2: Scan all visible elements in the left sidebar area
        const allEls = document.querySelectorAll('*');
        let bestId = null;
        let bestDist = 999999;
        const targetY = (pr.top + pr.bottom) / 2;

        for (const el of allEls) {{
            // Only look at elements in the left sidebar zone (x < 350)
            const r = el.getBoundingClientRect();
            if (r.right > 350 || r.width < 10 || r.height < 10) continue;
            const elCenterY = (r.top + r.bottom) / 2;
            const dist = Math.abs(elCenterY - targetY);
            if (dist > 60) continue;

            const txt = (el.innerText || el.textContent || '').trim();
            if (!txt || txt.length < 3) continue;

            const id = resolveFromText(txt);
            if (id && dist < bestDist) {{
                bestDist = dist;
                bestId = id;
            }}
        }}
        if (bestId) {{
            console.log('[WTK] S2 sidebar scan:', bestId, 'dist:', bestDist);
            return bestId;
        }}

        // Strategy 3: URL
        const fromUrl = resolveFromUrl();
        if (fromUrl) {{
            console.log('[WTK] S3 from URL:', fromUrl);
            return fromUrl;
        }}

        console.warn('[WTK] All strategies failed. mapLoaded:', mapLoaded, 'wtkMap.size:', wtkMap.size);
        return null;
    }}

    // ---- Popover Injection ----
    function injectMenuOption() {{
        const popovers = document.querySelectorAll('.o-popover, .dropdown-menu');
        popovers.forEach((pop) => {{
            if (pop.querySelector('.o_wtk_thread_action_item')) return;

            const text = pop.innerText || '';
            const isDiscussMenu = (
                text.includes('Silenciar') ||
                text.includes('Invitar personas') ||
                text.includes('Renombrar') ||
                text.includes('Agregar a favoritos') ||
                text.includes('Ocultar hasta') ||
                text.includes('Ajustes avanzados')
            );
            if (!isDiscussMenu) return;

            // Resolve channelId at injection time
            const channelId = resolveChannelForPopover(pop);

            const item = document.createElement('a');
            item.className = 'dropdown-item o_wtk_thread_action_item';
            item.href = '#';
            item.setAttribute('role', 'menuitem');
            item.innerHTML = '<i class="fa fa-handshake-o"></i> Crear Oportunidad CRM';

            item.onclick = function (e) {{
                e.preventDefault();
                e.stopPropagation();
                pop.style.display = 'none';

                console.log('[WTK] Click: channelId =', channelId);

                if (!channelId) {{
                    console.warn('[WTK] channelId null at click');
                    return;
                }}

                let svc = null;
                try {{ svc = window.odoo.__WOWL_DEBUG__.root.env.services.action; }} catch(e) {{}}

                const ctx = {{
                    active_id: channelId,
                    active_ids: [channelId],
                    active_model: 'discuss.channel'
                }};

                if (svc) {{
                    svc.doAction({sa697_id}, {{ additionalContext: ctx }});
                }} else {{
                    window.location.href = '/web#action={sa697_id}&active_id=' + channelId;
                }}
            }};

            pop.appendChild(item);
        }});
    }}

    setInterval(injectMenuOption, 400);
}})();
"""

    b64_js = base64.b64encode(js_v9.encode('utf-8')).decode('utf-8')

    atts = client.search_read('ir.attachment', domain=[('name', '=', 'wa_thread_action_wizard_menu.js')], fields=['id'])
    att_id = atts[0]['id']
    client.write('ir.attachment', [att_id], {'datas': b64_js, 'mimetype': 'application/javascript', 'public': True})
    print(f"Updated ir.attachment ID {att_id} (JS v9)")

    print("\n==================================================================")
    print(" JS v9 DEPLOYED — elementsFromPoint + sidebar scan               ")
    print("==================================================================")

if __name__ == '__main__':
    main()
