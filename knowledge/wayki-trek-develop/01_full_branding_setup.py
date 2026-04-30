#!/usr/bin/env python3
"""
Setup integral para Wayki Trek en Odoo:
- Branding (logo + paleta de colores corporativa)
- Moneda única en USD
- Pipeline CRM según definición del proyecto
"""

import base64
from pathlib import Path
import sys

# Permite importar odoo_cli al ejecutar el script desde su carpeta.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


PALETTE = {
    "primary": "#20603D",          # Verde bosque profundo
    "secondary": "#E5B745",        # Dorado mostaza
    "secondary_shadow": "#B68E33", # Dorado viejo/siena
    "accent": "#FFFFFF",           # Blanco puro
}

CRM_STAGES = [
    ("Nuevo Lead (Captación Automática)", False),
    ("Negociación / Cotización", False),
    ("Validación Interna (Vistos Buenos)", False),
    ("Reserva en Ejecución", False),
    ("Confirmado / Pago de Saldo", False),
    ("Convertido en Cliente / Post-Venta", True),
]


def _load_logo_b64() -> str:
    logo_path = Path(__file__).with_name("logo.png")
    if not logo_path.exists():
        raise FileNotFoundError(f"No se encontró logo en: {logo_path}")
    return base64.b64encode(logo_path.read_bytes()).decode("utf-8")


def setup_currency(client: OdooClient) -> None:
    print("\n[1/3] Configurando moneda única USD...")
    usd = client.execute(
        "res.currency",
        "search_read",
        [["name", "=", "USD"]],
        fields=["id", "name", "active"],
        limit=1,
        context={"active_test": False},
    )
    if not usd:
        raise RuntimeError("No existe USD en res.currency")

    usd_id = usd[0]["id"]
    if not usd[0].get("active"):
        client.write("res.currency", [usd_id], {"active": True})

    companies = client.search_read("res.company", domain=[], fields=["id", "name"], limit=100)
    for comp in companies:
        client.write("res.company", [comp["id"]], {"currency_id": usd_id})

    all_currencies = client.execute(
        "res.currency",
        "search_read",
        [],
        fields=["id", "name", "active"],
        limit=500,
        context={"active_test": False},
    )
    non_usd_active_ids = [c["id"] for c in all_currencies if c.get("name") != "USD" and c.get("active")]
    if non_usd_active_ids:
        client.write("res.currency", non_usd_active_ids, {"active": False})

    print(f"✅ USD activa y {len(non_usd_active_ids)} moneda(s) no-USD desactivada(s).")


def setup_branding(client: OdooClient) -> None:
    print("\n[2/3] Aplicando branding Wayki Trek...")
    logo_b64 = _load_logo_b64()
    companies = client.search_read("res.company", domain=[], fields=["id", "name"], limit=100)
    if not companies:
        raise RuntimeError("No se encontraron compañías para aplicar branding.")

    for comp in companies:
        vals = {
            "logo": logo_b64,
            "logo_web": logo_b64,
            "primary_color": PALETTE["primary"],
            "secondary_color": PALETTE["secondary"],
            "email_primary_color": PALETTE["primary"],
            "email_secondary_color": PALETTE["secondary"],
        }
        client.write("res.company", [comp["id"]], vals)

    print(f"✅ Branding aplicado a {len(companies)} compañía(s).")
    print(
        "   Paleta: "
        f"primary={PALETTE['primary']} | secondary={PALETTE['secondary']} | "
        f"secondary_shadow={PALETTE['secondary_shadow']} | accent={PALETTE['accent']}"
    )


def setup_crm_stages(client: OdooClient) -> None:
    print("\n[3/3] Configurando pipeline CRM...")
    existing = client.search_read("crm.stage", domain=[], fields=["id", "name"], limit=300)
    existing_by_name = {s["name"]: s["id"] for s in existing}
    desired_names = {name for name, _ in CRM_STAGES}

    for idx, (name, is_won) in enumerate(CRM_STAGES, start=1):
        vals = {
            "name": name,
            "sequence": idx * 10,
            "is_won": is_won,
            "fold": bool(is_won),
        }
        if name in existing_by_name:
            client.write("crm.stage", [existing_by_name[name]], vals)
        else:
            client.create("crm.stage", vals)

    final_stages = client.search_read(
        "crm.stage",
        domain=[],
        fields=["name", "sequence", "is_won"],
        order="sequence asc",
        limit=100,
    )
    print("✅ Etapas activas:")
    for stage in final_stages:
        print(f"   - {stage['sequence']:>3} | won={stage.get('is_won')} | {stage['name']}")


def main() -> None:
    print("Iniciando setup integral Wayki Trek...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado a Odoo (uid={uid})")

    setup_currency(client)
    setup_branding(client)
    setup_crm_stages(client)

    print("\n🎉 Setup completado.")


if __name__ == "__main__":
    main()
