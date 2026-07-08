# Plan de Implementación: Matriz de Roles y Permisos en Odoo

Este plan detalla cómo configurar los accesos de Odoo a través de `py-odoo-cli` para cumplir exactamente con la distribución de roles y visibilidad solicitada.

---

## 📋 1. Estado Actual vs. Estado Objetivo

Actualmente, **todos los usuarios** tienen acceso total (`base.group_system`). Esto hace que todos vean el menú "Ajustes", "Aplicaciones" y tengan control absoluto.

### Configuración requerida por usuario:

1. **`leocusi@waykitrek.net` (Rol: Admin):**
   * **Objetivo:** Acceso a **todo** (CRM, Ventas, Redes Sociales, Marketing, Whatsapp, Tableros, Ajustes, Aplicaciones, Facturación).
   * **Acción:** Mantener todos sus grupos actuales intactos, incluyendo `base.group_system` y `base.group_erp_manager`.

2. **`network@waykitrek.net` (Rol: Marketing):**
   * **Objetivo:** Ver CRM, Ventas, Conversaciones, Calendario, Contactos, Whatsapp, Tableros, Redes Sociales, Marketing por correo, Automatización de Marketing.
   * **Ocultar:** Aplicaciones, Ajustes, Facturación.
   * **Acción:** 
     * **Quitar:** `base.group_system` y `base.group_erp_manager` (oculta Ajustes y Aplicaciones).
     * **Quitar:** `account.group_account_manager` y grupos de facturación (oculta Facturación).
     * **Mantener:** `social.group_social_manager`, `mass_mailing.group_mass_mailing_user`, `marketing_automation.group_marketing_automation_user`, `sales_team.group_sale_manager`, `whatsapp.group_whatsapp_admin`.

3. **`sales@waykitrek.net` (Rol: Ventas):**
   * **Objetivo:** Ver CRM, Ventas, Conversaciones, Calendario, Contactos, Whatsapp, Tableros.
   * **Ocultar:** Redes Sociales, Marketing, Automatización, Aplicaciones, Ajustes, Facturación.
   * **Acción:**
     * **Quitar:** `base.group_system` y `base.group_erp_manager` (oculta Ajustes y Aplicaciones).
     * **Quitar:** `social.group_social_manager`, `mass_mailing.group_mass_mailing_user`, `marketing_automation.group_marketing_automation_user` (oculta Redes y Marketing).
     * **Quitar:** Grupos de facturación/contabilidad.
     * **Mantener:** `sales_team.group_sale_manager`, `whatsapp.group_whatsapp_admin`.

4. **`coordinator@waykitrek.net` (Rol: Postventas / Coordinador):**
   * **Objetivo:** Ver CRM, Ventas, Conversaciones, Calendario, Contactos, Whatsapp, Tableros.
   * **Ocultar:** Redes Sociales, Marketing, Automatización, Aplicaciones, Ajustes, Facturación.
   * **Acción:**
     * **Quitar:** `base.group_system` y `base.group_erp_manager` (oculta Ajustes y Aplicaciones).
     * **Quitar:** `mass_mailing.group_mass_mailing_user`, `social.group_social_manager` si lo tuviera.
     * **Quitar:** `account.group_account_manager` (oculta Facturación).
     * **Mantener:** `sales_team.group_sale_manager`, `whatsapp.group_whatsapp_admin`.

---

## 🛠️ 2. Scripts de Ejecución (Python)

Crearemos un script de automatización en `cleanup/configurar_roles.py` para realizar estas desasociaciones de grupos de forma segura.

### Código del Script (`cleanup/configurar_roles.py`):

```python
import sys
sys.path.insert(0, '../knowledge/wayki-trek-develop/29_custom_quote_app')
from odoo_cli import OdooClient
client = OdooClient()
client.connect()

# Mapeo de grupos a remover por usuario
users_config = {
    "network@waykitrek.net": [
        "base.group_system",
        "base.group_erp_manager",
        "account.group_account_manager",
        "account.group_account_invoice",
        "account.group_account_user",
        "account.group_account_readonly"
    ],
    "sales@waykitrek.net": [
        "base.group_system",
        "base.group_erp_manager",
        "social.group_social_manager",
        "social.group_social_user",
        "mass_mailing.group_mass_mailing_user",
        "mass_mailing.group_mass_mailing_campaign",
        "marketing_automation.group_marketing_automation_user",
        "account.group_account_manager",
        "account.group_account_invoice",
        "account.group_account_user",
        "account.group_account_readonly"
    ],
    "coordinator@waykitrek.net": [
        "base.group_system",
        "base.group_erp_manager",
        "social.group_social_manager",
        "social.group_social_user",
        "mass_mailing.group_mass_mailing_user",
        "mass_mailing.group_mass_mailing_campaign",
        "marketing_automation.group_marketing_automation_user",
        "account.group_account_manager",
        "account.group_account_invoice",
        "account.group_account_user",
        "account.group_account_readonly"
    ]
}

for login, group_xml_ids in users_config.items():
    print(f"Configurando usuario: {login}...")
    user = client.search_read('res.users', [('login', '=', login)], ['id'])
    if not user:
        print(f"⚠️ Usuario {login} no encontrado.")
        continue
    user_id = user[0]['id']

    # Obtener IDs reales de los grupos que queremos remover
    groups = client.search_read('ir.model_data', [
        ('model', '=', 'res.groups'),
        ('module', 'in', [x.split('.')[0] for x in group_xml_ids]),
        ('name', 'in', [x.split('.')[1] for x in group_xml_ids])
    ], ['res_id'])
    
    group_ids_to_remove = [g['res_id'] for g in groups]
    if group_ids_to_remove:
        # Comando Odoo para desasociar relaciones Many2Many: (3, group_id)
        # O (4, group_id) para asociar
        # Se envía como una lista de tuplas [(3, gid1), (3, gid2), ...]
        commands = [(3, gid) for gid in group_ids_to_remove]
        client.write('res.users', [user_id], {'groups_id': commands})
        print(f"✅ Removidos {len(group_ids_to_remove)} grupos de {login}.")
    else:
        print(f"ℹ️ Nada que remover para {login}.")

print("\nConfiguración finalizada.")
```

---

## 🚦 3. Plan de Verificación

Una vez ejecutado el script, validaremos el resultado:
1. Comprobando en base de datos que `network@`, `sales@` y `coordinator@` ya no tengan el grupo `base.group_system`.
2. Confirmando que `leocusi@` siga manteniendo el grupo `base.group_system` intacto.
3. El cliente podrá refrescar su navegador con cada usuario y verificar visualmente que las aplicaciones en la sección roja (Ajustes, Facturación, Aplicaciones, etc.) han desaparecido de su vista.
