#!/usr/bin/env python3
"""
Configura unidades de medida estándar para CM Line.

- Usa la unidad estándar de Odoo (`Units`) como referencia para cantidades.
- Añade UoM para paquetes, cientos, millares, caja, bolsa, saco, docena y bobina.
- Añade UoM de volumen: Galón y Metro cúbico (basadas en litros).

Uso con Docker:
    docker-compose run --rm odoo-cli python knowledge/cmline-production/setup_uom.py
"""

import os
import sys
from typing import Any, Dict, List, Tuple

# Ajustar el path para importar odoo_cli desde la raíz del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from odoo_cli import OdooClient  # type: ignore[import]
from odoo_cli.exceptions import (  # type: ignore[import]
    OdooClientError,
    OdooConfigError,
    OdooConnectionError,
    OdooFaultError,
)


def _get_uom_by_name(client: OdooClient, uom_name: str) -> Dict[str, Any]:
    """Obtener datos de una UoM existente por nombre."""
    records: List[Dict[str, Any]] = client.search_read(
        "uom.uom",
        [["name", "=", uom_name]],
        fields=["id", "name", "factor", "relative_factor", "relative_uom_id", "rounding"],
        limit=1,
    )
    if not records:
        raise RuntimeError(
            f"No se encontró la unidad de medida base '{uom_name}'. "
            "Revisa que exista en Odoo."
        )
    rec = records[0]
    print(
        f"✅ UoM base detectada '{uom_name}': "
        f"id={rec['id']}, factor={rec['factor']}, "
        f"relative_factor={rec['relative_factor']}, "
        f"relative_uom_id={rec['relative_uom_id']}"
    )
    return rec


def _ensure_uom(
    client: OdooClient,
    name: str,
    base_uom_id: int,
    factor: float,
    rounding: float = 1.0,
) -> int:
    """Crear la UoM si no existe ya con ese nombre ligada a la UoM base."""
    existing: List[Dict[str, Any]] = client.search_read(
        "uom.uom",
        [
            ["name", "=", name],
            ["relative_uom_id", "=", base_uom_id],
        ],
        fields=["id", "name", "relative_uom_id"],
        limit=1,
    )
    if existing:
        uom_id = int(existing[0]["id"])
        print(f"ℹ️  UoM '{name}' ya existe (id={uom_id}), no se modifica.")
        return uom_id

    vals: Dict[str, Any] = {
        "name": name,
        "relative_uom_id": base_uom_id,
        "factor": factor,
        "relative_factor": factor,
        "rounding": rounding,
        "active": True,
    }
    uom_id = client.create("uom.uom", vals)
    print(f"✅ UoM '{name}' creada (id={uom_id}) [factor={factor}, rounding={rounding}]")
    return int(uom_id)


def main() -> None:
    try:
        client = OdooClient()
        uid = client.connect()
        print(f"✅ Conectado a Odoo. UID={uid}")

        # 1) Detectar UoM base
        # Cantidad/piezas: usamos la UoM estándar "Units"
        units_uom = _get_uom_by_name(client, "Units")
        units_uom_id = int(units_uom["id"])

        # Volumen: tomamos "ml" como base y "L" como ejemplo ya configurado
        ml_uom = _get_uom_by_name(client, "ml")
        ml_uom_id = int(ml_uom["id"])

        print()
        print(
            "=== Configurando unidades basadas en piezas "
            f"(base: Units, id={units_uom_id}) ==="
        )

        # 2) UoM basadas en piezas (factores respecto a "Units")
        piece_uoms = [
            # nombre,             factor,  rounding
            ("Paquete 25",        25.0,    1.0),
            ("Paquete 50",        50.0,    1.0),
            ("Docena",            12.0,    1.0),
            ("Ciento",            100.0,   1.0),
            ("Millar",            1000.0,  1.0),
            ("Caja 1000",         1000.0,  1.0),
            ("Bolsa 50",          50.0,    1.0),
            ("Saco 25",           25.0,    1.0),
            ("Bobina",            1.0,     1.0),
        ]

        for name, factor, rounding in piece_uoms:
            _ensure_uom(
                client=client,
                name=name,
                base_uom_id=units_uom_id,
                factor=factor,
                rounding=rounding,
            )

        print()
        print(
            "=== Configurando unidades de volumen "
            f"(base: ml, id={ml_uom_id}) ==="
        )

        # 3) UoM de volumen (factores respecto a litros)
        volume_uoms = [
            # nombre,       factor (L por unidad), rounding
            # factor = cantidad de ml por unidad
            ("Galón",        3785.0,    0.001),
            ("Metro cúbico", 1_000_000.0, 0.001),
        ]

        for name, factor, rounding in volume_uoms:
            _ensure_uom(
                client=client,
                name=name,
                base_uom_id=ml_uom_id,
                factor=factor,
                rounding=rounding,
            )

        print()
        print("✅ Configuración de unidades de medida completada.")

    except OdooConfigError as e:
        print(f"❌ Error de configuración: {e}")
        print("   Verifica tu archivo .env (ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD).")
        sys.exit(1)
    except OdooConnectionError as e:
        print(f"❌ Error de conexión: {e}")
        print("   Verifica tus credenciales y que la instancia de Odoo sea accesible.")
        sys.exit(1)
    except OdooFaultError as e:
        print(f"❌ Error de Odoo: {e.fault_string}")
        if e.fault_code is not None:
            print(f"   Código de fallo: {e.fault_code}")
        sys.exit(1)
    except OdooClientError as e:
        print(f"❌ Error del cliente Odoo: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

