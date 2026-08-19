# Ocultación del Ícono de Actividades / Reloj en la Barra Superior (Navbar) - Wayki Trek

## 📌 Diagnóstico del Caso y Causa Raíz

En las versiones de **Odoo 19 / SaaS**, la plantilla principal de la interfaz web (`web.webclient_bootstrap`) utiliza el bundle **`web.assets_web`** en lugar de `web.assets_backend`. 

Debido a esto, los assets inyectados previamente solo en `web.assets_backend` no se cargaban en la barra de navegación superior.

---

## 🛠️ Solución Aplicada

Se vincularon los adjuntos CSS y JS a ambos bundles principales (`web.assets_web` y `web.assets_backend`):

1. **Assets CSS**:
   - `wtk_hide_activities_css_web_assets_web` (bundle: `web.assets_web`, ID: 119)
   - `wtk_hide_activities_css_web_assets_backend` (bundle: `web.assets_backend`, ID: 121)

2. **Assets JavaScript**:
   - `wtk_hide_activities_js_web_assets_web` (bundle: `web.assets_web`, ID: 120)
   - `wtk_hide_activities_js_web_assets_backend` (bundle: `web.assets_backend`, ID: 122)

---

## 🚀 Script de Despliegue

Script en el repositorio:
📂 [`knowledge/wayki-trek-develop/38_hide_navbar_activities.py`](file:///home/roger/Escritorio/work/py-odoo-cli/knowledge/wayki-trek-develop/38_hide_navbar_activities.py)

```bash
.venv/bin/python3 knowledge/wayki-trek-develop/38_hide_navbar_activities.py
```

---

## 🔄 Recargar la Página

Al abrir Odoo en el navegador, realizar un refresco completo (`Ctrl + F5` o `Ctrl + Shift + R`).
