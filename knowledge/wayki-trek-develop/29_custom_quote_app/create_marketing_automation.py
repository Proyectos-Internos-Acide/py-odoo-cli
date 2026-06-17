#!/usr/bin/env python3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

def create_marketing_campaign():
    print("-> Iniciando creación de Campaña de Marketing de Prueba...")
    client = OdooClient()
    client.connect()
    
    # 1. Obtener el modelo crm.lead
    lead_models = client.search_read("ir.model", [["model", "=", "crm.lead"]], ["id"])
    if not lead_models:
        print("❌ Error: No se encontró el modelo crm.lead en Odoo.")
        return
    model_id = lead_models[0]["id"]
    
    # 2. Configurar los contenidos de los correos (mailing.mailing)
    body_email_1 = """
<div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f7f9fc; padding: 30px 15px; margin: 0;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 6px solid #20603D;">
        
        <!-- Cabecera -->
        <div style="background-color: #20603D; padding: 30px 20px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: bold; letter-spacing: 0.5px;">Wayki Trek</h1>
            <p style="color: #E5B745; margin: 5px 0 0 0; font-size: 14px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Tu próxima gran aventura</p>
        </div>
        
        <!-- Contenido -->
        <div style="padding: 30px 25px; line-height: 1.6; color: #333333; font-size: 15px;">
            <p style="margin-top: 0;">¡Hola <strong><t t-out="object.contact_name or 'Viajero'"/></strong>!</p>
            
            <p>Dinos, ¿qué paso? Vimos que estabas muy interesado en realizar tu viaje de aventura con nosotros. 🏔️</p>
            
            <p>Queríamos saber si tuviste algún inconveniente o si te gustaría conversar directamente para resolver cualquier duda sobre el itinerario, preparación o fechas de viaje. Estamos aquí para ayudarte a planificar todo a tu medida.</p>
            
            <!-- Botón de acción -->
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://wa.me/51963038997" style="background-color: #20603D; color: #ffffff; text-decoration: none; padding: 12px 28px; border-radius: 5px; font-weight: bold; display: inline-block; font-size: 16px; border: 1px solid #20603D;">
                    Escríbenos por WhatsApp 💬
                </a>
            </div>
            
            <p style="margin-bottom: 0;">Si lo prefieres, puedes responder directamente a este correo. ¡Buen día!</p>
        </div>
        
        <!-- Pie de página -->
        <div style="background-color: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0;">
            <p style="margin: 0 0 5px 0;">Wayki Trek · Expertos en Rutas de Aventura</p>
            <p style="margin: 0;">Cusco, Perú</p>
        </div>
    </div>
</div>
""".strip()

    body_email_2 = """
<div style="font-family: Arial, sans-serif; line-height: 1.5; color: #333333; font-size: 14px; padding: 20px;">
    <p>Hola <t t-out="object.contact_name or 'Viajero'"/>,</p>
    
    <p>Queríamos saber si tuviste oportunidad de revisar la información que te enviamos anteriormente o si necesitas alguna aclaración.</p>
    
    <p style="margin-top: 15px;">Avísanos si deseas programar una llamada corta para resolver tus dudas.</p>
    
    <p style="margin-top: 25px;">Saludos cordiales,<br/>El equipo de Wayki Trek</p>
</div>
""".strip()

    # Upsert Correo 1
    mailing_1_subject = "PRUEBA: ¿Listo para tu próxima aventura? 🏔️"
    existing_m1 = client.search_read("mailing.mailing", [["subject", "=", mailing_1_subject]], ["id"])
    m1_vals = {
        "subject": mailing_1_subject,
        "body_html": body_email_1,
        "mailing_model_id": model_id,
        "mailing_type": "mail",
        "use_in_marketing_automation": True,
        "state": "draft",
    }
    if existing_m1:
        m1_id = existing_m1[0]["id"]
        client.write("mailing.mailing", [m1_id], m1_vals)
        print(f"✅ Correo 1 '{mailing_1_subject}' actualizado (ID={m1_id}).")
    else:
        m1_id = client.create("mailing.mailing", m1_vals)
        print(f"✅ Correo 1 '{mailing_1_subject}' creado (ID={m1_id}).")

    # Upsert Correo 2
    mailing_2_subject = "PRUEBA: Queríamos saber si tienes alguna pregunta"
    existing_m2 = client.search_read("mailing.mailing", [["subject", "=", mailing_2_subject]], ["id"])
    m2_vals = {
        "subject": mailing_2_subject,
        "body_html": body_email_2,
        "mailing_model_id": model_id,
        "mailing_type": "mail",
        "use_in_marketing_automation": True,
        "state": "draft",
    }
    if existing_m2:
        m2_id = existing_m2[0]["id"]
        client.write("mailing.mailing", [m2_id], m2_vals)
        print(f"✅ Correo 2 '{mailing_2_subject}' actualizado (ID={m2_id}).")
    else:
        m2_id = client.create("mailing.mailing", m2_vals)
        print(f"✅ Correo 2 '{mailing_2_subject}' creado (ID={m2_id}).")

    # 3. Crear/Actualizar Campaña de Marketing (Borrar si ya existe para restaurar a Borrador)
    campaign_name = "PRUEBA: Prueba de marketing"
    existing_camp = client.search_read("marketing.campaign", [["name", "=", campaign_name]], ["id"])
    
    if existing_camp:
        camp_id = existing_camp[0]["id"]
        print(f"-> Campaña existente '{campaign_name}' encontrada (ID={camp_id}). Eliminando para recrear en Borrador...")
        client.execute("marketing.campaign", "unlink", [camp_id])
    
    # Filtro: leads en etapa "Seguimiento" (Stage ID = 12)
    campaign_domain = "[('stage_id', '=', 12)]"
    
    camp_vals = {
        "name": campaign_name,
        "model_id": model_id,
        "domain": campaign_domain,
        "active": True,
        "state": "draft",
    }
    
    camp_id = client.create("marketing.campaign", camp_vals)
    print(f"✅ Campaña '{campaign_name}' recreada en Borrador (ID={camp_id}).")

    # 4. Crear Actividades de la Campaña
    # Eliminar actividades viejas para recrear y enlazar correctamente
    existing_activities = client.search_read("marketing.activity", [["campaign_id", "=", camp_id]], ["id"])
    if existing_activities:
        client.execute("marketing.activity", "unlink", [act["id"] for act in existing_activities])

    # Actividad 1: Correo Inmediato al entrar a "Seguimiento"
    act_1_vals = {
        "name": "PRUEBA: Re-captar interés (Inmediato)",
        "campaign_id": camp_id,
        "activity_type": "email",
        "mass_mailing_id": m1_id,
        "trigger_type": "begin",
        "interval_number": 0,
        "interval_type": "hours",
    }
    act_1_id = client.create("marketing.activity", act_1_vals)
    print(f"✅ Actividad 1 creada (ID={act_1_id}).")

    # Actividad 2: Correo a los 2 días si sigue en "Seguimiento"
    act_2_vals = {
        "name": "PRUEBA: Segundo mensaje (A los 2 días)",
        "campaign_id": camp_id,
        "activity_type": "email",
        "mass_mailing_id": m2_id,
        "parent_id": act_1_id,
        "trigger_type": "activity",  # Se dispara x tiempo después de la actividad padre
        "interval_number": 2,
        "interval_type": "days",
    }
    act_2_id = client.create("marketing.activity", act_2_vals)
    print(f"✅ Actividad 2 creada (ID={act_2_id}).")
    
    print("🎉 Configuración de la automatización de marketing de prueba terminada.")

if __name__ == "__main__":
    create_marketing_campaign()
