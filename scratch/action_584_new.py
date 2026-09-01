if record.email_from:
    raw_from = str(record.email_from or '').strip()
    display_name = ''
    clean_email = raw_from.lower()

    if '<' in raw_from and '>' in raw_from:
        parts = raw_from.split('<')
        name_part = parts[0].replace('"', '').replace("'", "").strip()
        email_part = parts[1].split('>')[0].replace('"', '').replace("'", "").strip().lower()
        if name_part and '@' not in name_part:
            display_name = name_part
        if email_part:
            clean_email = email_part
    else:
        clean_email = raw_from.replace('"', '').replace("'", "").strip().lower()

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
            or (record.contact_name and record.contact_name.strip() != 'Email' and record.contact_name.strip())
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
            
            # Si el contacto tenía de nombre 'Email', el asunto o el correo, lo actualizamos al nombre real
            if contact_name and (partner.name in [record.name, 'Email', 'email'] or '@' in partner.name):
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
