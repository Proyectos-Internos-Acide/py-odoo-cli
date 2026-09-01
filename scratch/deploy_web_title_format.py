from odoo_cli.client import OdooClient

client = OdooClient()

# -------------------------------------------------------------------------
# 1. ACTION 582: Format Opportunity Name as [WEB] - Cliente - Tour - Pax
# -------------------------------------------------------------------------
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

        # Extraer nombre del lead inicial
        rec_name = str(record.name or '').strip()
        client_name = rec_name
        if client_name.startswith('[WEB]'):
            parts_web = client_name.split(' - ')
            if len(parts_web) > 1:
                client_name = parts_web[1].strip()
        if client_name.lower().startswith('cliente:'):
            client_name = client_name[8:].strip()
        elif client_name.lower().startswith('cliente :'):
            client_name = client_name[9:].strip()

        # Limpiar tags para parsear lineas del formulario
        clean_text = raw_desc.replace('<br/>', '\\n').replace('<br />', '\\n').replace('<br>', '\\n')
        for tag in ['<p>', '</p>', '<strong>', '</strong>', '<b>', '</b>', '<i>', '</i>', '<span>', '</span>', '<div>', '</div>']:
            clean_text = clean_text.replace(tag, '')
            clean_text = clean_text.replace(tag.upper(), '')

        lines = [l.strip() for l in clean_text.split('\\n') if l.strip()]

        tour_name = ''
        pax_qty = ''
        msg_lines = []
        is_msg = False

        html_lines = ['<p><strong>DETALLES DEL FORMULARIO DE CONTACTO</strong><br><br>']
        if client_name:
            html_lines.append('<strong>Cliente:</strong> ' + str(client_name) + '<br>')
        if record.email_from:
            html_lines.append('<strong>Email:</strong> ' + str(record.email_from) + '<br>')
        if record.phone:
            html_lines.append('<strong>Telefono:</strong> ' + str(record.phone) + '<br>')
        html_lines.append('<br>')

        for line in lines:
            if 'DETALLES DEL TOUR' in line:
                continue
            if line.startswith('Aventura:'):
                tour_name = line[9:].strip()
                html_lines.append('<strong>Aventura:</strong> ' + tour_name + '<br>')
            elif line.startswith('No. Personas:'):
                pax_qty = line[13:].strip()
                html_lines.append('<strong>No. Personas:</strong> ' + pax_qty + '<br>')
            elif line.startswith('Mensaje:'):
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

        # ── Formatear Nuevo Nombre de la Oportunidad: [WEB] - Cliente - Tour - Pax ──
        title_parts = ['[WEB]', client_name or 'Cliente']
        if tour_name:
            title_parts.append(tour_name)
        if pax_qty:
            pax_label = f'{pax_qty} Pax' if 'pax' not in pax_qty.lower() else pax_qty
            title_parts.append(pax_label)

        new_opportunity_name = ' - '.join(title_parts)

        # Actualizar la oportunidad con nombre formateado y limpiar descripción
        record.write({
            'name': new_opportunity_name,
            'description': ''
        })

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


# -------------------------------------------------------------------------
# 2. ACTION 584: Support [WEB] - Name in Contact Linking
# -------------------------------------------------------------------------
code_584 = '''if record.email_from:
    raw_from = str(record.email_from or '').strip()
    display_name = ''
    clean_email = raw_from.lower()

    if '<' in raw_from and '>' in raw_from:
        parts = raw_from.split('<')
        name_part = parts[0].replace('\"', '').replace(\"'\", \"\").strip()
        email_part = parts[1].split('>')[0].replace('\"', '').replace(\"'\", \"\").strip().lower()
        if name_part and '@' not in name_part:
            display_name = name_part
        if email_part:
            clean_email = email_part
    else:
        clean_email = raw_from.replace('\"', '').replace(\"'\", \"\").strip().lower()

    if '@' in clean_email and len(clean_email) > 4:
        # Extraer nombre del título si empieza con [WEB], Cliente: o [INTERNO]
        lead_name_candidate = ''
        if record.name:
            rec_name = str(record.name).strip()
            if rec_name.startswith('[WEB]'):
                p_web = rec_name.split(' - ')
                if len(p_web) > 1:
                    lead_name_candidate = p_web[1].strip()
            elif rec_name.lower().startswith('cliente:'):
                lead_name_candidate = rec_name[8:].strip()
            elif rec_name.lower().startswith('cliente :'):
                lead_name_candidate = rec_name[9:].strip()
            elif rec_name.startswith('['):
                p_parts = rec_name.split(']', 1)
                if len(p_parts) > 1:
                    cand = p_parts[1].strip()
                    if '-' in cand:
                        cand = cand.split('-')[0].strip()
                    lead_name_candidate = cand

        # Determinar el nombre real del contacto (Prioridad: lead_name_candidate -> display_name -> contact_name -> formateado de email)
        contact_name = (
            lead_name_candidate
            or display_name
            or (record.contact_name and record.contact_name.strip() not in ['Email', 'email'] and record.contact_name.strip())
        )

        if not contact_name or contact_name.lower() == 'email':
            user_part = clean_email.split('@')[0]
            contact_name = user_part.replace('.', ' ').replace('_', ' ').replace('-', ' ').title()

        # Limpiar prefijos residuales
        if contact_name.startswith('['):
            p_parts = contact_name.split(']', 1)
            if len(p_parts) > 1:
                contact_name = p_parts[1].strip()
        if contact_name.lower().startswith('cliente:'):
            contact_name = contact_name[8:].strip()
        elif contact_name.lower().startswith('cliente :'):
            contact_name = contact_name[9:].strip()

        # 2. Buscar si ya existe un Contacto con este correo limpio
        partner = env['res.partner'].search([('email', '=ilike', clean_email)], limit=1)
        if not partner:
            partner = env['res.partner'].search([('email', 'ilike', clean_email)], limit=1)

        if partner:
            # Si el contacto existe, lo enlazamos al Lead
            record.write({
                'partner_id': partner.id,
                'contact_name': contact_name
            })
            
            # Siempre actualizar el nombre del contacto con el nombre real del formulario
            if contact_name and contact_name.lower() != 'email':
                partner.write({'name': contact_name})
            if partner.email != clean_email and clean_email:
                partner.write({'email': clean_email})
            if record.phone and not partner.phone:
                partner.write({'phone': record.phone})
        else:
            partner_vals = {
                'name': contact_name,
                'email': clean_email,
            }
            if record.phone:
                partner_vals['phone'] = record.phone

            new_partner = env['res.partner'].create(partner_vals)
            record.write({
                'partner_id': new_partner.id,
                'contact_name': contact_name
            })
'''

compile(code_584, '<string>', 'exec')
res_584 = client.write('ir.actions.server', [584], {'code': code_584})
print("Action 584 write result:", res_584)
