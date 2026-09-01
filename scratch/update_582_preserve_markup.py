from odoo_cli.client import OdooClient

client = OdooClient()

with open('scratch/action_582_backup.py', 'r') as f:
    orig_code_582 = f.read()

old_header_block = """try:
    # --- AGREGADO ESPECIAL PARA EL FORMULARIO DE CONTACTO WEB ---
    # Interceptamos si el PHP de WordPress mandó el HTML directo en la descripción
    if record.description and 'DETALLES DEL TOUR (FORMULARIO CUSTOM)' in record.description:
        html_desc = record.description
        record.write({'description': ''}) # Limpiamos la caja de notas
        
        def post_contact_msg():
            env['crm.lead'].browse(record.id).message_post(
                body=html_desc, 
                message_type='comment', 
                subtype_xmlid='mail.mt_note'
            )
        env.cr.postcommit.add(post_contact_msg)
        
        payload_raw = ''"""

new_header_block = """try:
    # --- AGREGADO ESPECIAL PARA EL FORMULARIO DE CONTACTO WEB ---
    # Interceptamos si el PHP de WordPress mando el HTML directo en la descripcion
    if record.description and 'DETALLES DEL TOUR (FORMULARIO CUSTOM)' in record.description:
        raw_markup = record.description
        record.write({'description': ''})

        # Extraer nombre del lead
        rec_name = str(record.name or '').strip()
        client_name = rec_name
        if client_name.lower().startswith('cliente:'):
            client_name = client_name[8:].strip()
        elif client_name.lower().startswith('cliente :'):
            client_name = client_name[9:].strip()

        # Inyectar Cliente, Email y Telefono usando replace sobre el objeto Markup de Odoo
        target_header = '<strong>DETALLES DEL TOUR (FORMULARIO CUSTOM)</strong>'
        if target_header in raw_markup:
            extra_lines = []
            if client_name:
                extra_lines.append('<strong>Cliente:</strong> ' + str(client_name))
            if record.email_from:
                extra_lines.append('<strong>Email:</strong> ' + str(record.email_from))
            if record.phone:
                extra_lines.append('<strong>Telefono:</strong> ' + str(record.phone))

            if extra_lines:
                replacement = target_header + '<br>' + '<br>'.join(extra_lines) + '<br>'
                html_desc = raw_markup.replace(target_header, replacement)
            else:
                html_desc = raw_markup
        else:
            html_desc = raw_markup

        def post_contact_msg(body_to_post=html_desc):
            env['crm.lead'].browse(record.id).message_post(
                body=body_to_post, 
                message_type='comment', 
                subtype_xmlid='mail.mt_note'
            )
        env.cr.postcommit.add(post_contact_msg)
        
        payload_raw = ''"""

final_code_582 = orig_code_582.replace(old_header_block, new_header_block)
compile(final_code_582, '<string>', 'exec')

res_582 = client.write('ir.actions.server', [582], {'code': final_code_582})
print("Action 582 write result:", res_582)
