#!/usr/bin/env python3
"""
Setup email signatures for all Wayki Trek team members.
"""

import base64
from pathlib import Path
import sys

# Permite importar odoo_cli al ejecutar el script desde su carpeta.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

USERS_DATA = [
    {
        "login": "leocusi@waykitrek.net",
        "name": "Leo Cusi",
        "function": "Administrador",
        "phone": "+51 984 463 021",
    },
    {
        "login": "sales@waykitrek.net",
        "name": "Américo Aguilar",
        "function": "Ventas",
        "phone": "+51 969 775 002",
    },
    {
        "login": "coordinator@waykitrek.net",
        "name": "Carlos Fernandez",
        "function": "Post-Ventas",
        "phone": "+51 987 378 388",
    },
    {
        "login": "network@waykitrek.net",
        "name": "Amaru Cusi",
        "function": "Marketing",
        "phone": "+51 913 551 308",
    },
]


def _load_logo_b64() -> str:
    logo_path = Path(__file__).with_name("logo.png")
    if not logo_path.exists():
        raise FileNotFoundError(f"No se encontró logo en: {logo_path}")
    return base64.b64encode(logo_path.read_bytes()).decode("utf-8")


def generate_signature_html(name: str, function: str, phone: str, email: str, logo_b64: str) -> str:
    return f"""<div style="font-family: Arial, sans-serif; color: #333333; line-height: 1.5; font-size: 13px;">
  <table cellpadding="0" cellspacing="0" border="0" style="border-collapse: collapse;">
    <tr>
      <td style="vertical-align: top; padding-right: 15px; border-right: 2px solid #20603D;">
        <img src="data:image/png;base64,{logo_b64}" alt="Wayki Trek" width="120" style="display: block; outline: none; border: none; text-decoration: none;" />
      </td>
      <td style="vertical-align: top; padding-left: 15px;">
        <div style="font-size: 15px; font-weight: bold; color: #20603D;">{name}</div>
        <div style="font-size: 13px; color: #666666; margin-bottom: 8px;">{function}</div>
        <div style="font-size: 12px; color: #333333;">
          <strong>Teléfono:</strong> <a href="tel:{phone.replace(' ', '')}" style="color: #20603D; text-decoration: none;">{phone}</a><br/>
          <strong>Correo:</strong> <a href="mailto:{email}" style="color: #20603D; text-decoration: none;">{email}</a>
        </div>
      </td>
    </tr>
  </table>
</div>"""


def main() -> None:
    print("Conectando a Odoo...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado a Odoo (uid={uid})")

    logo_b64 = _load_logo_b64()

    for udata in USERS_DATA:
        login = udata["login"]
        name = udata["name"]
        function = udata["function"]
        phone = udata["phone"]

        print(f"\nProcesando usuario: {login} ({name})...")

        # 1. Buscar el usuario
        users = client.search_read(
            "res.users",
            domain=[["login", "=", login]],
            fields=["id", "name", "partner_id"],
            limit=1,
        )
        if not users:
            print(f"⚠️ No se encontró ningún usuario con login '{login}'")
            continue

        user = users[0]
        user_id = user["id"]
        partner_id = user["partner_id"][0]
        print(f"   Encontrado Usuario ID {user_id} | Partner ID {partner_id}")

        # 2. Generar firma
        sig_html = generate_signature_html(name, function, phone, login, logo_b64)

        # 3. Actualizar partner
        client.write(
            "res.partner",
            [partner_id],
            {
                "name": name,
                "function": function,
                "phone": phone,
                "email": login,
            }
        )
        print("   ✅ Partner actualizado.")

        # 4. Actualizar usuario
        client.write(
            "res.users",
            [user_id],
            {
                "name": name,
                "signature": sig_html,
            }
        )
        print("   ✅ Usuario y firma actualizados.")

    print("\n🎉 Proceso completado para todos los usuarios encontrados.")


if __name__ == "__main__":
    main()
