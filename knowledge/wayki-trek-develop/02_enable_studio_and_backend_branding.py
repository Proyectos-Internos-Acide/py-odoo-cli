#!/usr/bin/env python3
"""
Habilita Studio y aplica branding backend/login para Wayki Trek.
"""

import base64
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


PALETTE = {
    "primary_color": "#20603D",
    "secondary_color": "#E5B745",
    "email_primary_color": "#20603D",
    "email_secondary_color": "#E5B745",
}


def ensure_studio_installed(client: OdooClient) -> None:
    studio = client.search_read(
        "ir.module.module",
        domain=[["name", "=", "web_studio"]],
        fields=["id", "name", "state"],
        limit=1,
    )
    if not studio:
        raise RuntimeError("No se encontró módulo web_studio en la instancia.")

    mod = studio[0]
    if mod["state"] != "installed":
        client.execute("ir.module.module", "button_immediate_install", [mod["id"]])
        print("✅ web_studio instalado.")
    else:
        print("✅ web_studio ya estaba instalado.")


def load_logo() -> str:
    logo_path = Path(__file__).with_name("logo.png")
    if not logo_path.exists():
        raise FileNotFoundError(f"No existe logo en {logo_path}")
    return base64.b64encode(logo_path.read_bytes()).decode("utf-8")


def apply_company_branding(client: OdooClient) -> None:
    logo_b64 = load_logo()
    companies = client.search_read("res.company", domain=[], fields=["id", "name"], limit=20)
    if not companies:
        raise RuntimeError("No se encontraron compañías.")

    vals = {
        **PALETTE,
        "logo": logo_b64,
        "logo_web": logo_b64,
        "uses_default_logo": False,
    }
    for comp in companies:
        client.write("res.company", [comp["id"]], vals)

    print(f"✅ Branding backend/login aplicado a {len(companies)} compañía(s).")


def print_summary(client: OdooClient) -> None:
    studio = client.search_read(
        "ir.module.module",
        domain=[["name", "=", "web_studio"]],
        fields=["name", "state"],
        limit=1,
    )[0]
    company = client.search_read(
        "res.company",
        domain=[],
        fields=["name", "primary_color", "secondary_color", "email_primary_color", "email_secondary_color"],
        limit=1,
    )[0]

    print("\nRESUMEN:")
    print(f"- Studio: {studio['state']}")
    print(f"- Company: {company['name']}")
    print(f"- primary_color: {company.get('primary_color')}")
    print(f"- secondary_color: {company.get('secondary_color')}")
    print(f"- email_primary_color: {company.get('email_primary_color')}")
    print(f"- email_secondary_color: {company.get('email_secondary_color')}")


def main() -> None:
    print("Iniciando setup Studio + branding backend/login...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    ensure_studio_installed(client)
    apply_company_branding(client)
    print_summary(client)
    print("\n🎉 Listo.")


if __name__ == "__main__":
    main()
