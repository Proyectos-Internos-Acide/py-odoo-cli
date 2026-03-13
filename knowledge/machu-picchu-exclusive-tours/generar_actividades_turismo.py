#!/usr/bin/env python3
"""
Generar actividades relacionadas al rubro turismo para Machu Picchu Exclusive Tours.

Creará actividades en:
- Oportunidades de CRM (crm.lead) con nombre que empiece por "Viaje"
- Tareas de proyecto de reservas (project.task) con nombre que empiece por "Reserva para cliente"

Uso:
    .venv/bin/python knowledge/machu-picchu-exclusive-tours/generar_actividades_turismo.py
"""

import os
import random
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from odoo_cli import OdooClient  # type: ignore
from odoo_cli.exceptions import (  # type: ignore
    OdooConfigError,
    OdooConnectionError,
    OdooExecutionError,
    OdooFaultError,
)


UTC = timezone.utc


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _random_future_date(max_days_ahead: int = 45) -> str:
    days_ahead = random.randint(1, max_days_ahead)
    return (_now() + timedelta(days=days_ahead)).date().isoformat()


def _connect_client() -> OdooClient:
    try:
        client = OdooClient()
        client.connect()
        return client
    except (OdooConfigError, OdooConnectionError) as e:
        print(f"Error de conexión/configuración: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado al inicializar el cliente: {e}")
        sys.exit(1)


def _get_activity_type(client: OdooClient) -> int:
    """Elegir un tipo de actividad estándar (llamada / por hacer)."""
    types = client.search_read(
        "mail.activity.type",
        domain=[],
        fields=["id", "name"],
        limit=20,
    )
    if not types:
        raise OdooExecutionError("No se encontraron tipos de actividad en el sistema.")

    # Preferir tipos 'Llamada' o 'To Do' si existen
    preferred_names = {"call", "llamada", "to do", "todo", "por hacer"}
    for t in types:
        name = (t.get("name") or "").strip().lower()
        if name in preferred_names:
            return int(t["id"])
    return int(types[0]["id"])


def _get_model_id(client: OdooClient, model_name: str) -> int:
    res = client.search_read(
        "ir.model",
        domain=[["model", "=", model_name]],
        fields=["id"],
        limit=1,
    )
    if not res:
        raise OdooExecutionError(f"No se encontró ir.model para {model_name}")
    return int(res[0]["id"])


def actividades_en_oportunidades(client: OdooClient, activity_type_id: int) -> int:
    print("Creando actividades en oportunidades de CRM...")
    model_name = "crm.lead"
    try:
        model_id = _get_model_id(client, model_name)
    except OdooExecutionError as e:
        print(f"  {e}, se omiten actividades en oportunidades.")
        return 0

    leads = client.search_read(
        model_name,
        domain=[["name", "ilike", "Viaje"]],
        fields=["id", "name", "expected_revenue"],
        limit=40,
    )
    if not leads:
        print("  No se encontraron oportunidades con prefijo 'Viaje'.")
        return 0

    summaries = [
        "Llamada de seguimiento de propuesta",
        "Confirmar detalles de itinerario",
        "Recordatorio de pago de adelanto",
        "Enviar versión final de itinerario",
        "Validar datos de pasaportes",
    ]

    created = 0
    for lead in leads:
        lead_id = int(lead["id"])
        name = lead.get("name") or ""
        revenue = lead.get("expected_revenue") or 0

        # Crear 1 o 2 actividades por oportunidad
        for _ in range(random.choice([1, 2])):
            summary = random.choice(summaries)
            note = (
                f"Oportunidad: {name}\n"
                f"Importe estimado: {revenue}.\n"
                "Alinear expectativas de servicio de lujo y validar fechas tentativas."
            )
            vals: Dict[str, Any] = {
                "res_model": model_name,
                "res_model_id": model_id,
                "res_id": lead_id,
                "activity_type_id": activity_type_id,
                "summary": summary,
                "note": note,
                "date_deadline": _random_future_date(60),
            }
            try:
                client.create("mail.activity", vals)
                created += 1
            except (OdooFaultError, OdooExecutionError):
                continue

    print(f"  Actividades creadas en oportunidades: {created}")
    return created


def actividades_en_reservas(client: OdooClient, activity_type_id: int) -> int:
    print("Creando actividades en tareas de reservas (project.task)...")
    model_name = "project.task"
    try:
        model_id = _get_model_id(client, model_name)
    except OdooExecutionError as e:
        print(f"  {e}, se omiten actividades en reservas.")
        return 0

    tasks = client.search_read(
        model_name,
        domain=[["name", "ilike", "Reserva para cliente"]],
        fields=["id", "name"],
        limit=40,
    )
    if not tasks:
        print("  No se encontraron tareas de reservas con el patrón esperado.")
        return 0

    summaries = [
        "Verificar compra de tickets de tren",
        "Confirmar reservas de hotel",
        "Revisar logística de traslados",
        "Coordinar guía local en Machu Picchu",
        "Confirmar preferencias alimenticias del pasajero",
    ]

    created = 0
    for task in tasks:
        task_id = int(task["id"])
        name = task.get("name") or ""

        # 1 actividad clave por reserva
        summary = random.choice(summaries)
        note = (
            f"Reserva: {name}\n"
            "Asegurar que todos los servicios críticos (trenes, hoteles, traslados) estén confirmados "
            "al menos 7 días antes del inicio del viaje."
        )
        vals: Dict[str, Any] = {
            "res_model": model_name,
            "res_model_id": model_id,
            "res_id": task_id,
            "activity_type_id": activity_type_id,
            "summary": summary,
            "note": note,
            "date_deadline": _random_future_date(45),
        }
        try:
            client.create("mail.activity", vals)
            created += 1
        except (OdooFaultError, OdooExecutionError):
            continue

    print(f"  Actividades creadas en reservas: {created}")
    return created


def main() -> None:
    print("--- Generación de actividades turísticas (CRM + Reservas) ---")
    client = _connect_client()

    try:
        activity_type_id = _get_activity_type(client)
        total_leads = actividades_en_oportunidades(client, activity_type_id)
        total_tasks = actividades_en_reservas(client, activity_type_id)

        print("Resumen general de actividades:")
        print(f"- En oportunidades de CRM: {total_leads}")
        print(f"- En tareas de reserva: {total_tasks}")
        print(f"- Total actividades creadas: {total_leads + total_tasks}")
    except (OdooConnectionError, OdooFaultError, OdooExecutionError) as e:
        print(f"Error al generar actividades: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado al generar actividades: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

