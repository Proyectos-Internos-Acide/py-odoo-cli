from odoo_cli.client import OdooClient

client = OdooClient()

# -------------------------------------------------------------------------
# ACTION 582: Keep raw HTML from WordPress and inject Cliente/Email/Telefono
# -------------------------------------------------------------------------
a582 = client.search_read('ir.actions.server', [('id', '=', 582)], ['id', 'name', 'code'])[0]
curr_code_582 = a582['code']

replacement_code_582 = """try:
    # --- AGREGADO ESPECIAL PARA EL FORMULARIO DE CONTACTO WEB ---
    # Interceptamos si el PHP de WordPress mando el HTML directo en la descripcion
    if record.description and 'DETALLES DEL TOUR (FORMULARIO CUSTOM)' in record.description:
        html_desc = record.description
        record.write({'description': ''})

        # Extraer nombre del lead
        rec_name = str(record.name or '').strip()
        client_name = rec_name
        if client_name.lower().startswith('cliente:'):
            client_name = client_name[8:].strip()
        elif client_name.lower().startswith('cliente :'):
            client_name = client_name[9:].strip()

        # Inyectar Cliente, Email y Telefono al HTML original sin romper etiquetas
        target_header = '<strong>DETALLES DEL TOUR (FORMULARIO CUSTOM)</strong>'
        if target_header in html_desc:
            extra_lines = []
            if client_name:
                extra_lines.append('<strong>Cliente:</strong> ' + str(client_name))
            if record.email_from:
                extra_lines.append('<strong>Email:</strong> ' + str(record.email_from))
            if record.phone:
                extra_lines.append('<strong>Telefono:</strong> ' + str(record.phone))

            if extra_lines:
                replacement = target_header + '<br>' + '<br>'.join(extra_lines) + '<br>'
                html_desc = html_desc.replace(target_header, replacement)

        def post_contact_msg():
            env['crm.lead'].browse(record.id).message_post(
                body=html_desc, 
                message_type='comment', 
                subtype_xmlid='mail.mt_note'
            )
        env.cr.postcommit.add(post_contact_msg)
        
        payload_raw = ''
    else:
        # Leemos el payload del campo dedicado o de description
        payload_raw = record.x_wayki_sync_payload"""

idx_else = curr_code_582.find("    else:\n        # Leemos el payload")
assert idx_else != -1, "Could not find 'else:' anchor in action 582"

final_code_582 = replacement_code_582 + curr_code_582[idx_else + len("    else:\n        # Leemos el payload") - len("        # Leemos el payload"):]
compile(final_code_582, '<string>', 'exec')

res_582 = client.write('ir.actions.server', [582], {'code': final_code_582})
print("Action 582 update result:", res_582)
