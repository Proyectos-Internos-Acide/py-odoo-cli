#!/usr/bin/env python3
"""
Oculta de forma definitiva el ícono de Actividades (reloj/contador) y cualquier ícono de reloj/timer
en la barra superior del backend de Odoo para la instancia Wayki Trek.

Estrategia:
1. Inyección en QWeb HTML Views (ir.ui.view inheriting web.webclient_bootstrap y web.layout):
   Usa bloques CDATA para que Odoo compile e inyecte el HTML directo sin errores de parsing XML.
2. Inyección en Recursos de Assets (ir.asset para web.assets_web y web.assets_backend).
"""

import base64
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


VIEW_BOOTSTRAP_NAME = "wtk_hide_navbar_activities_view"
VIEW_LAYOUT_NAME = "wtk_hide_navbar_activities_web_layout"

CSS_ATTACHMENT_NAME = "hide_navbar_activities.css"
JS_ATTACHMENT_NAME = "hide_navbar_activities.js"

CSS_CONTENT = """
.o_activity_menu,
.o-mail-ActivityMenu,
.o_nav_entry_type_activity,
.o_mail_systray_item.o_activity_menu,
.o_systray_activity,
.o_timer_systray,
.o_timesheet_systray,
div[title*="Actividad" i],
div[title*="Activity" i],
button[title*="Actividad" i],
button[title*="Activity" i],
a[title*="Actividad" i],
a[title*="Activity" i],
div[aria-label*="Actividad" i],
div[aria-label*="Activity" i],
button[aria-label*="Actividad" i],
button[aria-label*="Activity" i],
div[title*="Reloj" i],
button[title*="Reloj" i],
div[title*="Timer" i],
button[title*="Timer" i] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
}
""".strip()

JS_CONTENT = """(function() {
    function hideNavbarActivityIcons() {
        try {
            var navbar = document.querySelector('.o_main_navbar') || document.querySelector('.o_menu_systray') || document;
            var items = navbar.querySelectorAll('.o_menu_systray > *, .o_systray > *, .d-flex > *');
            items.forEach(function(el) {
                var html = el.innerHTML || '';
                var title = (el.getAttribute('title') || '').toLowerCase();
                var aria = (el.getAttribute('aria-label') || '').toLowerCase();
                var cls = (el.className || '').toLowerCase();

                if (cls.includes('o_user_menu') || cls.includes('o_switch_company')) return;

                if (
                    title.includes('activid') || title.includes('activit') ||
                    aria.includes('activid') || aria.includes('activit') ||
                    title.includes('reloj') || title.includes('timer') ||
                    html.includes('fa-clock') || html.includes('oi-clock') ||
                    html.includes('oi-activity') || html.includes('fa-tasks') ||
                    html.includes('oi-tasks') || html.includes('ActivityMenu') ||
                    html.includes('o_activity_menu')
                ) {
                    el.style.setProperty('display', 'none', 'important');
                    el.style.setProperty('visibility', 'hidden', 'important');
                }
            });

            var icons = document.querySelectorAll('.oi-clock, .fa-clock, .fa-clock-o, .oi-activity, .oi-tasks, .fa-tasks');
            icons.forEach(function(icon) {
                var parent = icon.closest('.o_mail_systray_item') || icon.closest('.o_systray_item') || icon.closest('button') || icon.parentElement;
                if (parent && !parent.classList.contains('o_user_menu')) {
                    parent.style.setProperty('display', 'none', 'important');
                    parent.style.setProperty('visibility', 'hidden', 'important');
                }
            });
        } catch(e) {}
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            hideNavbarActivityIcons();
            setInterval(hideNavbarActivityIcons, 200);
        });
    } else {
        hideNavbarActivityIcons();
        setInterval(hideNavbarActivityIcons, 200);
    }
})();""".strip()


def apply_qweb_views(client: OdooClient) -> None:
    # 1. Inherit web.webclient_bootstrap (ID 196)
    bootstrap_view = client.search_read("ir.ui.view", domain=[["key", "=", "web.webclient_bootstrap"]], fields=["id"], limit=1)
    if bootstrap_view:
        parent_id = bootstrap_view[0]["id"]
        arch = f"""<data>
    <xpath expr="//meta[@name='viewport']" position="before">
        <style>
            <![CDATA[
            {CSS_CONTENT}
            ]]>
        </style>
        <script type="text/javascript">
            <![CDATA[
            {JS_CONTENT}
            ]]>
        </script>
    </xpath>
</data>"""
        existing = client.search_read("ir.ui.view", domain=[["name", "=", VIEW_BOOTSTRAP_NAME]], fields=["id"], limit=1)
        if existing:
            client.write("ir.ui.view", [existing[0]["id"]], {"arch": arch, "active": True})
            print(f"✅ Vista QWeb de bootstrap actualizada (ir.ui.view ID: {existing[0]['id']})")
        else:
            vid = client.create("ir.ui.view", {"name": VIEW_BOOTSTRAP_NAME, "type": "qweb", "inherit_id": parent_id, "arch": arch, "active": True})
            print(f"✅ Vista QWeb de bootstrap creada (ir.ui.view ID: {vid})")

    # 2. Inherit web.layout (ID 184)
    layout_view = client.search_read("ir.ui.view", domain=[["key", "=", "web.layout"]], fields=["id"], limit=1)
    if layout_view:
        parent_id = layout_view[0]["id"]
        arch = f"""<data>
    <xpath expr="//head" position="inside">
        <style>
            <![CDATA[
            {CSS_CONTENT}
            ]]>
        </style>
        <script type="text/javascript">
            <![CDATA[
            {JS_CONTENT}
            ]]>
        </script>
    </xpath>
</data>"""
        existing = client.search_read("ir.ui.view", domain=[["name", "=", VIEW_LAYOUT_NAME]], fields=["id"], limit=1)
        if existing:
            client.write("ir.ui.view", [existing[0]["id"]], {"arch": arch, "active": True})
            print(f"✅ Vista QWeb de layout actualizada (ir.ui.view ID: {existing[0]['id']})")
        else:
            vid = client.create("ir.ui.view", {"name": VIEW_LAYOUT_NAME, "type": "qweb", "inherit_id": parent_id, "arch": arch, "active": True})
            print(f"✅ Vista QWeb de layout creada (ir.ui.view ID: {vid})")


def apply_assets(client: OdooClient) -> None:
    css_b64 = base64.b64encode(CSS_CONTENT.encode("utf-8")).decode("utf-8")
    js_b64 = base64.b64encode(JS_CONTENT.encode("utf-8")).decode("utf-8")

    # Attachment CSS
    att_css = client.search_read("ir.attachment", domain=[["name", "=", CSS_ATTACHMENT_NAME]], fields=["id"], limit=1)
    if att_css:
        css_id = att_css[0]["id"]
        client.write("ir.attachment", [css_id], {"datas": css_b64, "mimetype": "text/css", "public": True})
    else:
        css_id = client.create("ir.attachment", {"name": CSS_ATTACHMENT_NAME, "datas": css_b64, "mimetype": "text/css", "type": "binary", "public": True})

    # Attachment JS
    att_js = client.search_read("ir.attachment", domain=[["name", "=", JS_ATTACHMENT_NAME]], fields=["id"], limit=1)
    if att_js:
        js_id = att_js[0]["id"]
        client.write("ir.attachment", [js_id], {"datas": js_b64, "mimetype": "application/javascript", "public": True})
    else:
        js_id = client.create("ir.attachment", {"name": JS_ATTACHMENT_NAME, "datas": js_b64, "mimetype": "application/javascript", "type": "binary", "public": True})

    # Registros ir.asset para web.assets_web y web.assets_backend
    for b in ["web.assets_web", "web.assets_backend"]:
        css_name = f"wtk_hide_activities_css_{b.replace('.', '_')}"
        js_name = f"wtk_hide_activities_js_{b.replace('.', '_')}"
        
        ex_css = client.search_read("ir.asset", domain=[["name", "=", css_name]], fields=["id"], limit=1)
        if ex_css:
            client.write("ir.asset", [ex_css[0]["id"]], {"path": f"/web/content/{css_id}/{CSS_ATTACHMENT_NAME}", "bundle": b, "directive": "append", "active": True})
        else:
            client.create("ir.asset", {"name": css_name, "bundle": b, "directive": "append", "path": f"/web/content/{css_id}/{CSS_ATTACHMENT_NAME}", "sequence": 10, "active": True})

        ex_js = client.search_read("ir.asset", domain=[["name", "=", js_name]], fields=["id"], limit=1)
        if ex_js:
            client.write("ir.asset", [ex_js[0]["id"]], {"path": f"/web/content/{js_id}/{JS_ATTACHMENT_NAME}", "bundle": b, "directive": "append", "active": True})
        else:
            client.create("ir.asset", {"name": js_name, "bundle": b, "directive": "append", "path": f"/web/content/{js_id}/{JS_ATTACHMENT_NAME}", "sequence": 10, "active": True})

    print("✅ Registros ir.asset (web.assets_web y web.assets_backend) desplegados.")


def main() -> None:
    print("Iniciando aplicación directa de vistas QWeb (web.webclient_bootstrap y web.layout) e ir.asset...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado a Odoo (uid={uid})")

    apply_qweb_views(client)
    apply_assets(client)

    print("\n🎉 Proceso completado exitosamente. La inyección HTML directa se ha realizado.")


if __name__ == "__main__":
    main()
