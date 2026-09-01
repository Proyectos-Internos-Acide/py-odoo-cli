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

        # Limpiar tags para parsear lineas
        clean_text = raw_desc.replace('<br/>', '\\n').replace('<br />', '\\n').replace('<br>', '\\n')
        for tag in ['<p>', '</p>', '<strong>', '</strong>', '<b>', '</b>', '<i>', '</i>', '<span>', '</span>', '<div>', '</div>']:
            clean_text = clean_text.replace(tag, '')
            clean_text = clean_text.replace(tag.upper(), '')

        lines = [l.strip() for l in clean_text.split('\\n') if l.strip()]

        html_parts = ['<b>DETALLES DEL FORMULARIO DE CONTACTO</b><br/>']
        if client_name:
            html_parts.append(f'<b>Cliente:</b> {client_name}<br/>')
        if record.email_from:
            html_parts.append(f'<b>Email:</b> {record.email_from}<br/>')
        if record.phone:
            html_parts.append(f'<b>Telefono:</b> {record.phone}<br/>')
        html_parts.append('<br/>')

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
                    html_parts.append(f'<b>{parts[0].strip()}:</b> {parts[1].strip()}<br/>')
                else:
                    html_parts.append(f'{line}<br/>')

        if msg_lines:
            html_parts.append('<br/><b>Mensaje:</b><br/>')
            for m_item in msg_lines:
                html_parts.append(f'{m_item}<br/>')

        final_html_note = ''.join(html_parts)

        def post_contact_msg(body_to_post=final_html_note):
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
