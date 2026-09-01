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
        raw_desc = str(record.description or '')
        record.write({'description': ''})

        # Extraer nombre del lead
        rec_name = str(record.name or '').strip()
        client_name = rec_name
        if client_name.lower().startswith('cliente:'):
            client_name = client_name[8:].strip()
        elif client_name.lower().startswith('cliente :'):
            client_name = client_name[9:].strip()

        # Limpiar tags para formatear HTML limpio
        clean_text = raw_desc.replace('<br/>', '\\n').replace('<br />', '\\n').replace('<br>', '\\n')
        for tag in ['<p>', '</p>', '<strong>', '</strong>', '<b>', '</b>', '<i>', '</i>', '<span>', '</span>', '<div>', '</div>']:
            clean_text = clean_text.replace(tag, '')
            clean_text = clean_text.replace(tag.upper(), '')

        lines = [l.strip() for l in clean_text.split('\\n') if l.strip()]

        html_lines = ['<p><strong>DETALLES DEL FORMULARIO DE CONTACTO</strong><br><br>']
        if client_name:
            html_lines.append('<strong>Cliente:</strong> ' + str(client_name) + '<br>')
        if record.email_from:
            html_lines.append('<strong>Email:</strong> ' + str(record.email_from) + '<br>')
        if record.phone:
            html_lines.append('<strong>Telefono:</strong> ' + str(record.phone) + '<br>')
        html_lines.append('<br>')

        msg_lines = []
        is_msg = False
        for line in lines:
            if 'DETALLES DEL TOUR' in line:
                continue
            if line.startswith('Mensaje:'):
                is_msg = True
                msg_val = line[8:].strip()
                if msg_val:
                    msg_lines.append(msg_val)
            elif is_msg:
                msg_lines.append(line)
            else:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    html_lines.append('<strong>' + parts[0].strip() + ':</strong> ' + parts[1].strip() + '<br>')
                else:
                    html_lines.append(line + '<br>')

        if msg_lines:
            html_lines.append('<br><strong>Mensaje:</strong><br>')
            for m_item in msg_lines:
                html_lines.append(m_item + '<br>')

        html_lines.append('</p>')
        final_html_body = ''.join(html_lines)

        def post_contact_msg(body_to_post=final_html_body):
            note_subtype = env['mail.message.subtype'].search([('name', '=', 'Notes')], limit=1)
            subtype_id = note_subtype.id if note_subtype else 2
            env['mail.message'].create({
                'model': 'crm.lead',
                'res_id': record.id,
                'body': body_to_post,
                'message_type': 'comment',
                'subtype_id': subtype_id,
            })
        env.cr.postcommit.add(post_contact_msg)
        
        payload_raw = ''"""

final_code_582 = orig_code_582.replace(old_header_block, new_header_block)
compile(final_code_582, '<string>', 'exec')

res_582 = client.write('ir.actions.server', [582], {'code': final_code_582})
print("Action 582 write result:", res_582)
