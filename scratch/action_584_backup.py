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
        # 2. Buscar si ya existe un Contacto con este correo limpio
        partner = env['res.partner'].search([('email', '=ilike', clean_email)], limit=1)
        if not partner:
            partner = env['res.partner'].search([('email', 'ilike', clean_email)], limit=1)

        if partner:
            # Si el contacto existe, lo enlazamos al Lead
            record.write({'partner_id': partner.id})
            
            # Si el contacto tenía de nombre el asunto o el correo, y ahora tenemos el nombre real del remitente, lo actualizamos
            if display_name and (partner.name == record.name or '@' in partner.name):
                partner.write({'name': display_name})
            if partner.email != clean_email and clean_email:
                partner.write({'email': clean_email})
        else:
            # 3. Determinar el nombre real del contacto (Prioridad: Display Name -> contact_name -> Nombre formateado del email)
            contact_name = display_name or (record.contact_name and record.contact_name.strip())
            
            if not contact_name:
                user_part = clean_email.split('@')[0]
                contact_name = user_part.replace('.', ' ').replace('_', ' ').replace('-', ' ').title()

            # Limpiar prefijos de etiquetas como [INTERNO] o "Cliente:"
            if contact_name.startswith('['):
                p_parts = contact_name.split(']', 1)
                if len(p_parts) > 1:
                    contact_name = p_parts[1].strip()

            if contact_name.lower().startswith('cliente:'):
                contact_name = contact_name[8:].strip()
            elif contact_name.lower().startswith('cliente :'):
                contact_name = contact_name[9:].strip()

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
