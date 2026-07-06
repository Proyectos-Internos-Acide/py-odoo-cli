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
        # Se envía como una lista de tuplas [(3, gid1), (3, gid2), ...]
        commands = [(3, gid) for gid in group_ids_to_remove]
        client.write('res.users', [user_id], {'groups_id': commands})
        print(f"✅ Removidos {len(group_ids_to_remove)} grupos de {login}.")
    else:
        print(f"ℹ️ Nada que remover para {login}.")

print("\nConfiguración finalizada.")
