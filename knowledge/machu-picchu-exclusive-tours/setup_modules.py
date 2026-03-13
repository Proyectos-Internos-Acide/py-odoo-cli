#!/usr/bin/env python3
"""
Verificar e instalar módulos estándar necesarios para Machu Picchu Exclusive Tours.

Uso:
    .venv/bin/python knowledge/machu-picchu-exclusive-tours/setup_modules.py
    docker-compose run --rm odoo-cli python knowledge/machu-picchu-exclusive-tours/setup_modules.py
"""

import os
import sys
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from odoo_cli import OdooClient  # type: ignore
from odoo_cli.exceptions import (  # type: ignore
    OdooConfigError,
    OdooConnectionError,
    OdooExecutionError,
    OdooFaultError,
)


REQUIRED_MODULES: List[str] = [
    "crm",
    "project",
]

OPTIONAL_MODULES: List[str] = [
    "sale_crm",
]


def _index_modules(records: List[Dict]) -> Dict[str, Dict]:
    by_name: Dict[str, Dict] = {}
    for rec in records:
        name = rec.get("name")
        if name:
            by_name[str(name)] = rec
    return by_name


def setup_modules() -> int:
    print("--- Setup de módulos estándar para Machu Picchu Exclusive Tours ---")
    try:
        client = OdooClient()
        client.connect()
    except OdooConfigError as e:
        print(f"Error de configuración: {e}")
        print("Revisa tu archivo .env (ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD).")
        return 1
    except OdooConnectionError as e:
        print(f"Error de conexión: {e}")
        return 1
    except Exception as e:
        print(f"Error inesperado al inicializar el cliente: {e}")
        return 1

    target_modules: List[str] = REQUIRED_MODULES + OPTIONAL_MODULES
    print(f"Verificando módulos: {', '.join(target_modules)}")

    try:
        records = client.search_read(
            "ir.module.module",
            domain=[["name", "in", target_modules]],
            fields=["name", "state"],
        )
    except (OdooConnectionError, OdooFaultError, OdooExecutionError) as e:
        print(f"Error al leer módulos: {e}")
        return 1

    indexed = _index_modules(records)

    to_install_ids: List[int] = []

    for name in target_modules:
        rec = indexed.get(name)
        if not rec:
            print(f"- {name}: no encontrado en esta instancia (posible limitación de SaaS).")
            continue

        rec_id = rec.get("id")
        state = rec.get("state")

        if state == "installed":
            print(f"- {name}: ya instalado.")
            continue

        if not rec_id:
            print(f"- {name}: no tiene ID de módulo, se omite.")
            continue

        print(f"- {name}: estado actual '{state}', marcando para instalación...")
        to_install_ids.append(int(rec_id))

    if not to_install_ids:
        print("No hay módulos pendientes de instalar.")
        return 0

    try:
        # Llamada equivalente a hacer clic en 'Instalar' (uno por uno por compatibilidad con Odoo SaaS).
        for mid in to_install_ids:
            client.execute("ir.module.module", "button_install", [[mid]])
        print(f"Se han marcado {len(to_install_ids)} módulo(s) para instalación.")
        print("La instalación puede tardar unos minutos en aplicarse en el servidor.")
    except (OdooConnectionError, OdooFaultError, OdooExecutionError) as e:
        print(f"La instalación por API no está disponible en esta instancia (SaaS): {e}")
        print("Instala manualmente desde Odoo: Aplicaciones -> buscar 'CRM' y 'Proyectos' -> Instalar.")
        return 0  # No fallar; el usuario puede instalar desde la UI
    except Exception as e:
        print(f"Error inesperado durante la instalación de módulos: {e}")
        print("Instala manualmente desde Odoo: Aplicaciones -> CRM, Proyectos -> Instalar.")
        return 0

    return 0


def main() -> None:
    code = setup_modules()
    sys.exit(code)


if __name__ == "__main__":
    main()

