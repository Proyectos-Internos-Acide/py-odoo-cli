try:
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
        
        payload_raw = ''
    else:
        # Leemos el payload del campo dedicado o de description
        payload_raw = record.x_wayki_sync_payload
    is_dedicated = bool(payload_raw)

    if not payload_raw:
        payload_raw = record.description

    # DEBUG: Comprobar si el trigger funciona
    # record.message_post(body=f"DEBUG: Payload recibido: {str(payload_raw)[:200]} (Dedicated: {is_dedicated})")

    json_str = str(payload_raw or '').strip()
    
    # Si viene del description, intentamos extraer el bloque JSON (por si hay HTML o texto extra)
    if not is_dedicated:
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = json_str[start_idx:end_idx+1]

    # Si hay texto, y (es el campo dedicado O parece un JSON válido)
    if json_str and (is_dedicated or (json_str.startswith('{') and json_str.endswith('}'))):
        try:
            data = json.loads(json_str)
            
            # Limpiamos el payload para no volver a disparar esto por accidente
            if is_dedicated:
                record.write({'x_wayki_sync_payload': False})

            # Validar que sea un Objeto/Diccionario (evita que números o strings pasen como json válido)
            if not isinstance(data, dict):
                raise Exception("Se esperaba un Objeto JSON (diccionario), pero se recibió otro tipo de dato.")

        except Exception as e:
            error_msg = "Formato de datos NO ACEPTADO. El payload DEBE ser un objeto JSON estrictamente válido."
            record.message_post(
                body=f"⚠️ ERROR DE FORMATO: {error_msg}<br/>Detalle técnico: {str(e)}<br/>Recibido: <code>{str(payload_raw)[:500]}</code>",
                message_type='comment'
            )
            record.write({'x_wayki_sync_payload': False})
            raise UserError(f"{error_msg} (Detalle: {str(e)})")

        # ── ENRUTADOR POR ACCIÓN ──
        action = data.get('action')

        # Si no se envía el action, enviar a logs de odoo como error (lanzando excepción)
        if not action:
            error_msg = "JSON recibido sin campo 'action' obligatorio."
            record.message_post(
                body=f"⚠️ ERROR: {error_msg}<br/><code>{json_str[:500]}</code>",
                message_type='comment'
            )
            raise UserError(error_msg)

        # ── Datos generales y fallbacks ──
        booking_data = data.get('data', {}).get('booking', {})
        if not booking_data:
            booking_data = data.get('data', {}).get('payment', {})
        if not booking_data:
            booking_data = data.get('data', {}).get('transaction', {})

        # --- EXTRACCIÓN ULTRA-ROBUSTA DE BOOKING ID ---
        # Buscamos en raíz, en booking_data, o cualquier campo que se llame id/bookingId
        booking_id = data.get('bookingId') or data.get('booking_id') or data.get('id')
        if not booking_id:
            booking_id = booking_data.get('bookingId') or booking_data.get('booking_id') or booking_data.get('id')
        
        # Fallback agresivo: buscar en el primer nivel cualquier campo que contenga 'booking' e 'id'
        if not booking_id:
            for k, v in data.items():
                if 'booking' in k.lower() and 'id' in k.lower() and isinstance(v, (str, int)):
                    booking_id = v
                    break

        # ── VALIDACIÓN DE CAMPOS OBLIGATORIOS SEGÚN ACCIÓN ──
        if action == 'wayki_reserve_tour':
            required_fields = [
                'bookingId', 'tourName', 'tourId', 'startDate', 'endDate',
                'adultPassengers', 'childrenPassengers', 'studentPassengers',
                'adultPrice', 'studentPrice', 'childrenPrice', 'amount',
                'amountStr', 'debt', 'babyPassengers'
            ]
            missing = []
            for f in required_fields:
                if data.get(f) is None and booking_data.get(f) is None:
                    missing.append(f)

            if missing:
                error_msg = f"Faltan campos obligatorios para procesar la reserva: {', '.join(missing)}"
                record.message_post(body=f"⚠️ ERROR: {error_msg}", message_type='comment')
                raise UserError(error_msg)

        elif action == 'wayki_payment_tour':
            pax_check = data.get('passengers') or booking_data.get('passengers') or []
            p_first = pax_check[0] if pax_check else {}
            chk_email = p_first.get('email') or data.get('email') or booking_data.get('email') or ''
            
            if not booking_id and not chk_email:
                error_msg = "Falta 'bookingId' o 'email' obligatorio para procesar el pago."
                record.message_post(body=f"⚠️ ERROR: {error_msg}", message_type='comment')
                raise UserError(error_msg)

        trip_name = data.get('tourName') or data.get('tripName') or booking_data.get('tripName') or booking_data.get('title')
        
        # amount = Total del Tour
        amount = data.get('amount')
        if amount is None:
            amount = booking_data.get('amount_paid', booking_data.get('amount', 0))

        # amount_paid = El pago específico que entra en action wayki_payment_tour
        amount_paid = data.get('amountPaid') or data.get('amount_pay') or amount

        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        # ── Función auxiliar para generar HTML del Tour ──
        def get_tour_html(data_dict, b_id, t_name, total_amount, now_date):
            p_list = data_dict.get('passengers') or booking_data.get('passengers') or []
            pax_html = ""
            for p in p_list:
                pax_html += (
                    f"• 👤 {p.get('firstName', '')} {p.get('lastName', '')} "
                    f"| Doc: {p.get('documentNumber', 'N/A')} "
                    f"| 📧 {p.get('email', 'N/A')} "
                    f"| 📞 {p.get('phone', 'N/A')} "
                    f"| 🌍 {p.get('nationality', 'N/A')}<br/>"
                )

            serv_list = data_dict.get('additionalServices') or booking_data.get('additionalServices') or []
            serv_html = ""
            for s in serv_list:
                serv_html += f"• 🛠️ {s.get('name', '')} (x{s.get('quantity', 0)}) - ${s.get('amountTotal', 0)}<br/>"

            hotel_list = data_dict.get('hotels') or booking_data.get('hotels') or []
            hotel_html = ""
            for h in hotel_list:
                hotel_html += f"• 🏨 {h.get('name', 'Hotel')} (x{h.get('quantity', 0)}) - ${h.get('amountTotal', 0)}<br/>"

            adults = data_dict.get('adultPassengers', booking_data.get('adultPassengers', 0))
            children = data_dict.get('childrenPassengers', booking_data.get('childrenPassengers', 0))
            students = data_dict.get('studentPassengers', booking_data.get('studentPassengers', 0))
            babies = data_dict.get('babyPassengers', booking_data.get('babyPassengers', 0))

            adult_price = data_dict.get('adultPrice', booking_data.get('adultPrice', 0))
            student_price = data_dict.get('studentPrice', booking_data.get('studentPrice', 0))
            children_price = data_dict.get('childrenPrice', booking_data.get('childrenPrice', 0))

            t_debt = data_dict.get('debt', booking_data.get('debt', 0))
            s_date = data_dict.get('startDate', booking_data.get('startDate', 'N/A'))
            e_date = data_dict.get('endDate', booking_data.get('endDate', 'N/A'))

            return (
                f"<b>==== 🎟️ RESERVA WAYKITREK ====</b><br/>"
                f"🆔 <b>Booking ID:</b> {b_id or 'N/A'}<br/>"
                f"🎟️ <b>Tour:</b> {t_name or 'N/A'}<br/>"
                f"📅 <b>Fechas:</b> {s_date} → {e_date}<br/>"
                f"<br/>"
                f"<b>💰 Resumen Económico:</b><br/>"
                f"• Monto Total: <b>${total_amount or 0}</b><br/>"
                f"• Deuda Pendiente: ${t_debt}<br/>"
                f"• Precio Adulto: ${adult_price} | Estudiante: ${student_price} | Menor de edad: ${children_price}<br/>"
                f"<br/>"
                f"<b>👥 Pasajeros ({adults} adultos, {students} estudiantes, {children} menores de edad):</b><br/>"
                f"{pax_html or '<i>No registrados</i>'}<br/>"
                f"<b>🛠️ Servicios Adicionales:</b><br/>"
                f"{serv_html or '<i>Ninguno</i>'}<br/>"
                f"<b>🏨 Hoteles:</b><br/>"
                f"{hotel_html or '<i>Ninguno</i>'}<br/>"
                f"<br/>"
                f"<i>📡 Sincronizado: {now_date}</i>"
            )

        pax_list = data.get('passengers') or booking_data.get('passengers') or []
        primary_pax = pax_list[0] if pax_list else {}
        
        first_name = primary_pax.get('firstName')
        last_name = primary_pax.get('lastName')
        fallback_buyer = booking_data.get('buyerName') or booking_data.get('name') or data.get('buyerName') or data.get('name') or 'Cliente'
        
        if first_name or last_name:
            buyer_name = f"{first_name or ''} {last_name or ''}".strip()
        else:
            buyer_name = fallback_buyer

        final_email = primary_pax.get('email') or data.get('email') or booking_data.get('email') or ''
        final_phone = primary_pax.get('phone') or data.get('phone') or booking_data.get('phone') or ''

        # =============================================================
        # ACCIÓN: RESERVA DE TOUR → Crear/actualizar oportunidad
        # =============================================================
        if action == 'wayki_reserve_tour':
            full_html = get_tour_html(data, booking_id, trip_name, amount, now_str)

            # ── Búsqueda Dinámica de Etapa "Nuevo Lead" ──
            stage_new = env['crm.stage'].search([('name', '=', 'Nuevo Lead (Captación Automática)')], limit=1)
            if not stage_new:
                stage_new = env['crm.stage'].search([('name', 'ilike', 'Nuevo')], limit=1)
            if not stage_new:
                stage_new = env['crm.stage'].search([('is_won', '=', False)], order='sequence asc', limit=1)
            
            vals = {
                'description': '', # Limpiamos el JSON crudo de la caja de notas
                'name': f"[INTERNO] {buyer_name} - {trip_name or 'Tour'}",
                'email_from': final_email,
                'phone': final_phone,
                'expected_revenue': float(amount or 0),
                'stage_id': stage_new.id if stage_new else 5, 
                'probability': 10,
                'type': 'opportunity',
            }
            if booking_id:
                vals['x_wayki_booking_id'] = booking_id

            record.write(vals)

            # --- AGREGADO: Enviar resumen al chatter de manera diferida (postcommit) ---
            def post_msg():
                env['crm.lead'].browse(record.id).message_post(
                    body=full_html, 
                    message_type='comment', 
                    subtype_xmlid='mail.mt_note'
                )
            env.cr.postcommit.add(post_msg)
            


        # =============================================================
        # ACCIÓN: PAGO DE TOUR → Mover a Ganado / Pago de Saldo
        # =============================================================
        elif action == 'wayki_payment_tour':
            tx_ref = data.get('transactionCode') or data.get('transactionId') or data.get('code') or 'N/A'
            method = data.get('methodType') or 'N/A'
            payment_description = data.get('description') or 'Pago reserva'
            pago_date = data.get('date') or now_str

            chatter_msg = (
                f"<b>💰 PAGO REGISTRADO VIA WE TRAVEL / POSTMAN</b><br/>"
                f"• 💵 <b>Monto Pagado:</b> ${amount_paid or 0}<br/>"
                f"• 💳 <b>Método:</b> {method}<br/>"
                f"• 🔑 <b>Transacción:</b> {tx_ref}<br/>"
                f"• 🆔 <b>Booking ID:</b> {booking_id or 'N/A'}<br/>"
                f"• 📝 <b>Detalles:</b> {payment_description}<br/>"
                f"• 📅 <b>Fecha Pago:</b> {pago_date}"
            )

            # ── Búsqueda Dinámica de Etapa de Pago ──
            stage_paid = env['crm.stage'].search([('name', '=', 'Confirmado / Pago de Saldo')], limit=1)
            if not stage_paid:
                stage_paid = env['crm.stage'].search([('name', 'ilike', 'Confirmado')], limit=1)
            if not stage_paid:
                stage_paid = env['crm.stage'].search([('name', 'ilike', 'Pago')], limit=1)
            if not stage_paid:
                stage_paid = env['crm.stage'].search([('is_won', '=', True)], limit=1)

            existing_lead = None
            if booking_id:
                leads = env['crm.lead'].search([
                    ('x_wayki_booking_id', '=', booking_id),
                    ('id', '!=', record.id)
                ], limit=1)
                existing_lead = leads[0] if leads else None

            # Fallback por email si booking_id no devolvió resultados
            if not existing_lead and final_email:
                leads = env['crm.lead'].search([
                    ('email_from', '=', final_email),
                    ('id', '!=', record.id)
                ], order='create_date desc', limit=1)
                existing_lead = leads[0] if leads else None

            full_html = get_tour_html(data, booking_id, trip_name, amount, now_str)

            if existing_lead:
                # ── Lead previo encontrado: moverlo a Pago/Ganado y notificar ──
                lead_vals = {
                    'probability': 100
                }
                
                if booking_id and not existing_lead.x_wayki_booking_id:
                    lead_vals['x_wayki_booking_id'] = booking_id

                if data.get('tourName') or booking_data.get('tourName'):
                    lead_vals['description'] = full_html

                if final_email and not existing_lead.email_from:
                    lead_vals['email_from'] = final_email
                if final_phone and not existing_lead.phone:
                    lead_vals['phone'] = final_phone

                if stage_paid:
                    lead_vals['stage_id'] = stage_paid.id
                
                existing_lead.write(lead_vals)
                existing_lead.message_post(body=chatter_msg, message_type='comment')
                
                # Archivar limpiamente el registro temporal creado por el webhook/Postman
                record.message_post(
                    body=f"📌 <b>PAGO PROCESADO:</b> Pago transferido al Lead Principal <b>#{existing_lead.id} - {existing_lead.name}</b>. Este registro fue consolidado y archivado.",
                    message_type='comment'
                )
                record.write({
                    'description': f"📌 <i>Pago procesado. Lead principal actualizado: #{existing_lead.id} - {existing_lead.name}</i>",
                    'active': False
                })
            else:
                # ── No hay lead previo diferente: actualizar este registro (record) ──
                vals = {
                    'description': f"📌 <i>Pago directo registrado: {now_str}</i><br/><br/>{full_html}",
                    'name': f"[PAGO] {buyer_name} - {trip_name or 'Tour'}",
                    'expected_revenue': float(amount or 0),
                    'probability': 100,
                    'type': 'opportunity',
                    'email_from': final_email,
                    'phone': final_phone,
                }
                if stage_paid:
                    vals['stage_id'] = stage_paid.id
                if booking_id:
                    vals['x_wayki_booking_id'] = booking_id

                record.write(vals)
                record.message_post(body=chatter_msg, message_type='comment')

        # =============================================================
        # ACCIÓN GOOGLE SYNC (Bypass)
        # =============================================================
        elif action == 'google_sync':
            pass # No hacemos nada, permitimos que el script termine limpiamente

        # =============================================================
        # ACCIÓN NO RECONOCIDA
        # =============================================================
        else:
            error_msg = f"La acción '{action}' enviada en el JSON no es reconocida o no está soportada por el sistema Wayki."
            record.message_post(body=f"⚠️ ERROR: {error_msg}", message_type='comment')
            raise UserError(error_msg)

except Exception as e:
    if 'loads' not in str(e):
        record.message_post(body=f"❌ Error en Procesador Wayki: {str(e)}", message_type='notification')
        raise  # Lanza la excepcion para los logs de odoo
