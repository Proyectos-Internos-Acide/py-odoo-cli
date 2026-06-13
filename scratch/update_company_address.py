#!/usr/bin/env python3
"""
Fetch, update, and push the web.company_address_list view (ID 206)
to add 'Calle QUERA 239' above 'Cusco - Perú'.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    print("Conectado.\n")

    VIEW_ID = 206

    # Fetch current arch
    view = client.search_read("ir.ui.view", [["id", "=", VIEW_ID]], ["name", "key", "arch_db"])
    if not view:
        print("ERROR: View ID 206 not found!")
        return

    print(f"Vista: {view[0]['name']} | key: {view[0]['key']}")
    print("\nArch actual:")
    print(view[0]["arch_db"])

    # Patch: add Calle QUERA 239 before Cusco - Perú
    old_arch = view[0]["arch_db"]
    new_arch = old_arch.replace(
        "<li>Cusco - Perú</li>",
        "<li>Calle QUERA 239</li>\n        <li>Cusco - Perú</li>"
    )

    if new_arch == old_arch:
        print("\n⚠️  'Cusco - Perú' no encontrado literalmente. Mostrando arch completo:")
        print(old_arch)
        return

    print("\nArch nuevo:")
    print(new_arch)

    # Push update
    client.write("ir.ui.view", [VIEW_ID], {"arch_db": new_arch})
    print("\n✅ Vista actualizada exitosamente.")

if __name__ == "__main__":
    main()
