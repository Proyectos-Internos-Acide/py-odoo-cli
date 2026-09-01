from odoo_cli.client import OdooClient

client = OdooClient()

# -------------------------------------------------------------------------
# ACTION 582: Formatting Chatter Note with proper HTML <br> tags (no emojis)
# -------------------------------------------------------------------------
a582 = client.search_read('ir.actions.server', [('id', '=', 582)], ['id', 'name', 'code'])[0]
curr_code_582 = a582['code']

replacement_code_582 = """try:
    # --- AGREGADO ESPECIAL PARA EL FORMULARIO DE CONTACTO WEB ---
    # Interceptamos si el PHP de WordPress mando el texto directo en la descripcion
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

        # Limpiar tags HTML redundantes sin usar regex
        clean_text = raw_desc.replace('<br/>', '\\n').replace('<br />', '\\n').replace('<br>', '\\n')
        for tag in ['<p>', '</p>', '<strong>', '</strong>', '<b>', '</b>', '<i>', '</i>', '<span>', '</span>', '<div>', '</div>']:
            clean_text = clean_text.replace(tag, '')
            clean_text = clean_text.replace(tag.upper(), '')

        lines = [l.strip() for l in clean_text.split('\\n') if l.strip()]

        result_html = ['<strong>DETALLES DEL FORMULARIO DE CONTACTO</strong>', '<br>']
        if client_name:
            result_html.append('<strong>Cliente:</strong> ' + str(client_name))
        if record.email_from:
            result_html.append('<strong>Email:</strong> ' + str(record.email_from))
        if record.phone:
            result_html.append('<strong>Telefono:</strong> ' + str(record.phone))
        result_html.append('<br>')

        msg_block = []
        is_msg = False

        for line in lines:
            if 'DETALLES DEL TOUR' in line:
                continue
            if line.startswith('Mensaje:'):
                is_msg = True
                msg_val = line[8:].strip()
                if msg_val:
                    msg_block.append(msg_val)
            elif is_msg:
                msg_block.append(line)
            else:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    result_html.append('<strong>' + parts[0].strip() + ':</strong> ' + parts[1].strip())
                else:
                    result_html.append(line)

        if msg_block:
            result_html.append('<br>')
            result_html.append('<strong>Mensaje:</strong>')
            result_html.extend(msg_block)

        final_note = '<br>'.join(result_html)

        def post_contact_msg():
            env['crm.lead'].browse(record.id).message_post(
                body=final_note, 
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


# -------------------------------------------------------------------------
# ACTION 584: Ensure Partner Name is Always Updated if Real Name Provided
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
        # Extraer nombre del título si empieza con 'Cliente:' o similares
        lead_name_candidate = ''
        if record.name:
            rec_name = str(record.name).strip()
            if rec_name.lower().startswith('cliente:'):
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
print("Action 584 update result:", res_584)
