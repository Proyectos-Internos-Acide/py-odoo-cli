import sys
import os
import base64
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    print("==================================================================")
    print(" Deploying Discuss Chat Header Button Script to Odoo (Production)  ")
    print("==================================================================")
    
    client = OdooClient()
    client.connect()

    js_code = r"""/** @odoo-module **/
(function () {
    "use strict";

    console.log("=== WTK WhatsApp CRM Header Button Script Loaded ===");

    function getActiveChannelId() {
        const hash = window.location.hash || "";
        const match = hash.match(/discuss\.channel\/(\d+)/) || hash.match(/channel_id=(\d+)/) || hash.match(/#id=(\d+)/);
        if (match) {
            return parseInt(match[1]);
        }
        return null;
    }

    function injectButtonIfNeeded() {
        // Target headers in Discuss App and Chat Windows
        const selectors = [
            '.o-mail-Discuss-header',
            '.o-mail-Thread-header',
            '.o_thread_title',
            '.o-discuss-ChannelHeader',
            '.o_mail_chat_content .o_chat_title',
            '.o-mail-ChatWindow-header'
        ];
        
        let container = null;
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el) {
                container = el;
                break;
            }
        }

        if (!container) {
            // Fallback: look for top control panel or thread header
            container = document.querySelector('header.o_control_panel') || document.querySelector('.o_control_panel');
        }

        if (!container) return;
        if (container.querySelector('.o_wtk_create_crm_btn')) return;

        const btn = document.createElement('button');
        btn.className = 'btn btn-sm btn-primary ms-2 me-2 o_wtk_create_crm_btn';
        btn.style.cssText = 'background-color: #714B67 !important; border-color: #714B67 !important; color: #ffffff !important; font-weight: bold !important; padding: 4px 12px !important; border-radius: 4px !important; z-index: 99999 !important; cursor: pointer !important; display: inline-flex !important; align-items: center !important; gap: 6px !important; margin-left: 10px !important; font-size: 13px !important; shadow: 0 2px 4px rgba(0,0,0,0.2);';
        btn.innerHTML = '<i class="fa fa-briefcase" style="font-size:14px;"></i> <span>➕ Crear Oportunidad CRM</span>';

        btn.onclick = function (e) {
            e.preventDefault();
            e.stopPropagation();

            const channelId = getActiveChannelId();
            console.log("[WTK] Executing WA CRM action for channel ID:", channelId);

            // Access Odoo OWL Action Service
            let actionService = null;
            if (window.odoo && window.odoo.__WOWL_DEBUG__ && window.odoo.__WOWL_DEBUG__.root) {
                try {
                    actionService = window.odoo.__WOWL_DEBUG__.root.env.services.action;
                } catch (err) {}
            }

            if (!actionService && window.owl && window.owl.Component) {
                try {
                    actionService = owl.Component.env.services.action;
                } catch (err) {}
            }

            if (actionService) {
                actionService.doAction(693, {
                    additionalContext: {
                        active_id: channelId,
                        active_ids: channelId ? [channelId] : [],
                        active_model: "discuss.channel",
                    },
                });
            } else {
                // Fallback: trigger via window location or XML-RPC call
                window.location.href = "/web#action=693&active_id=" + (channelId || '');
            }
        };

        container.appendChild(btn);
    }

    setInterval(injectButtonIfNeeded, 800);
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        injectButtonIfNeeded();
    } else {
        document.addEventListener('DOMContentLoaded', injectButtonIfNeeded);
    }
})();
"""

    b64_data = base64.b64encode(js_code.encode('utf-8')).decode('utf-8')

    # Update attachment ID 3184
    client.write('ir.attachment', [3184], {
        'datas': b64_data,
        'mimetype': 'application/javascript',
        'public': True,
    })
    print("Updated ir.attachment ID 3184 with JS code")

    # Update ir.asset ID 115
    client.write('ir.asset', [115], {
        'bundle': 'web.assets_backend',
        'directive': 'append',
        'path': '/web/content/3184/wa_crm_discuss_action.js',
    })
    print("Updated ir.asset ID 115 pointing to /web/content/3184/wa_crm_discuss_action.js")

    print("\n==================================================================")
    print(" DISCUSS HEADER BUTTON DEPLOYMENT COMPLETE ")
    print("==================================================================")

if __name__ == '__main__':
    main()
