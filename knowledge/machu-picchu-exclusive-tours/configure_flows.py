#!/usr/bin/env python3
"""
Configurar flujos estándar (CRM y Proyectos) para Machu Picchu Exclusive Tours.

Uso:
    .venv/bin/python knowledge/machu-picchu-exclusive-tours/configure_flows.py
    docker-compose run --rm odoo-cli python knowledge/machu-picchu-exclusive-tours/configure_flows.py
"""

import os
import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from odoo_cli import OdooClient  # type: ignore
from odoo_cli.exceptions import (  # type: ignore
    OdooConfigError,
    OdooConnectionError,
    OdooExecutionError,
    OdooFaultError,
)


CRM_STAGES: List[Dict[str, Any]] = [
    {"name": "Nuevo Lead", "sequence": 10},
    {"name": "En evaluación", "sequence": 20},
    {"name": "Propuesta enviada", "sequence": 30},
    {"name": "Cerrado ganado", "sequence": 40, "fold": True},
    {"name": "Cerrado perdido", "sequence": 50, "fold": True},
]

PROJECT_NAME = "Reservas Machu Picchu Exclusive Tours"

PROJECT_TASK_STAGES: List[Dict[str, Any]] = [
    {"name": "Borrador de Cotización", "sequence": 10},
    {"name": "Confirmación (Adelanto)", "sequence": 20},
    {"name": "Compra de Tickets/Hoteles", "sequence": 30},
    {"name": "Venta Final (Ejecución)", "sequence": 40},
]


def _connect_client() -> Optional[OdooClient]:
    try:
        client = OdooClient()
        client.connect()
        return client
    except OdooConfigError as e:
        print(f"Error de configuración: {e}")
        return None
    except OdooConnectionError as e:
        print(f"Error de conexión: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al inicializar el cliente: {e}")
        return None


def ensure_crm_stages(client: OdooClient) -> None:
    print("Configurando etapas de CRM (crm.stage)...")
    existing = client.search_read(
        "crm.stage",
        domain=[],
        fields=["id", "name", "sequence", "fold"],
    )
    by_name: Dict[str, Dict[str, Any]] = {str(r.get("name")): r for r in existing if r.get("name")}

    for stage in CRM_STAGES:
        name = stage["name"]
        current = by_name.get(name)
        if current:
            updates: Dict[str, Any] = {}
            if "sequence" in stage and current.get("sequence") != stage["sequence"]:
                updates["sequence"] = stage["sequence"]
            if "fold" in stage and current.get("fold") != stage["fold"]:
                updates["fold"] = stage["fold"]
            if updates:
                print(f"- Actualizando etapa CRM existente: {name}")
                client.write("crm.stage", [int(current["id"])], updates)
            else:
                print(f"- Etapa CRM ya configurada: {name}")
            continue

        print(f"- Creando etapa CRM: {name}")
        client.create("crm.stage", stage)


def ensure_project_and_stages(client: OdooClient) -> None:
    print("Configurando proyecto de reservas y etapas de tareas...")

    projects = client.search_read(
        "project.project",
        domain=[["name", "=", PROJECT_NAME]],
        fields=["id", "name"],
        limit=1,
    )
    if projects:
        project_id = int(projects[0]["id"])
        print(f"- Proyecto existente encontrado: {PROJECT_NAME} (ID {project_id})")
    else:
        print(f"- Creando proyecto: {PROJECT_NAME}")
        project_id = client.create(
            "project.project",
            {
                "name": PROJECT_NAME,
            },
        )

    existing_types = client.search_read(
        "project.task.type",
        domain=[],
        fields=["id", "name", "sequence"],
    )
    by_name: Dict[str, Dict[str, Any]] = {str(r.get("name")): r for r in existing_types if r.get("name")}

    for stage in PROJECT_TASK_STAGES:
        name = stage["name"]
        current = by_name.get(name)
        base_vals: Dict[str, Any] = {
            "name": name,
            "sequence": stage.get("sequence", 10),
        }

        if current:
            updates: Dict[str, Any] = {}
            if current.get("sequence") != base_vals["sequence"]:
                updates["sequence"] = base_vals["sequence"]
            if updates:
                print(f"- Actualizando etapa de proyecto existente: {name}")
                client.write("project.task.type", [int(current["id"])], updates)
            else:
                print(f"- Etapa de proyecto ya configurada: {name}")
            continue

        print(f"- Creando etapa de proyecto: {name}")
        client.create("project.task.type", base_vals)

    print(
        "Nota: las etapas de proyecto creadas son globales y aparecerán como columnas en los tableros Kanban de tareas."
    )


def main() -> None:
    print("--- Configuración de flujos CRM y Proyectos para Machu Picchu Exclusive Tours ---")
    client = _connect_client()
    if not client:
        sys.exit(1)

    try:
        ensure_crm_stages(client)
        ensure_project_and_stages(client)
        print("Configuración completada.")
    except (OdooConnectionError, OdooFaultError, OdooExecutionError) as e:
        print(f"Error al configurar flujos: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado al configurar flujos: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

