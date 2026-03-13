#!/usr/bin/env python3
"""
Listar aplicaciones (módulos) instaladas en Odoo - Machu Picchu Exclusive Tours

Uso:
    .venv/bin/python knowledge/machu-picchu-exclusive-tours/listar_modulos.py
    docker-compose run --rm odoo-cli python knowledge/machu-picchu-exclusive-tours/listar_modulos.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from odoo_cli import OdooClient
from odoo_cli.exceptions import OdooConfigError, OdooConnectionError, OdooFaultError, OdooExecutionError


def main():
    print("--- Aplicaciones instaladas: Machu Picchu Exclusive Tours ---")
    try:
        client = OdooClient()
        client.connect()

        modules = client.search_read(
            "ir.module.module",
            domain=[["state", "=", "installed"]],
            fields=["name", "shortdesc", "author", "installed_version"],
            order="name",
        )

        print("-" * 90)
        print(f"{'Nombre':<35} | {'Versión':<12} | {'Descripción'}")
        print("-" * 90)
        for m in modules:
            name = m.get("name") or ""
            version = m.get("installed_version") or ""
            desc = (m.get("shortdesc") or "")[:45]
            print(f"{name:<35} | {version:<12} | {desc}")
        print("-" * 90)
        print(f"Total: {len(modules)} módulos instalados")

    except OdooConfigError as e:
        print(f"Error de configuración: {e}")
        sys.exit(1)
    except (OdooConnectionError, OdooFaultError, OdooExecutionError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
