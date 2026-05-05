#!/usr/bin/env python3
"""
Crea/actualiza tours diarios en la categoría "Tours diarios" con precios por tipo de grupo.

Tours:
- Cusco - Cusco City Tour
- Cusco - Valle Sagrado
- Cusco - Moray & Maras

Regla:
- Precio base del producto = 0
- El precio final se define por variante (price_extra) en atributo "Tipo de grupo".
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


CATEGORY_NAME = "Tours diarios"
GROUP_ATTR_NAME = "Tipo de grupo"
PASSENGER_ATTR_NAME = "Tipo de pasajero"

TOURS = [
    {
        "name": "Cusco - Cusco City Tour",
        "description": (
            "Tarifas por tipo de grupo:\n"
            "- Grupo mediano (10 a 16 personas): USD $55 por persona. "
            "Equilibrio perfecto entre precio, interacción y calidad de servicio.\n"
            "- Grupo grande (15 a 30 personas): USD $45 por persona. "
            "Opción más económica y social, manteniendo el estándar Wayki Trek."
        ),
        "prices": {
            "Grupo mediano (10 a 16 personas)": 55.0,
            "Grupo grande (15 a 30 personas)": 45.0,
        },
    },
    {
        "name": "Cusco - Valle Sagrado",
        "description": (
            "Tarifas por tipo de grupo:\n"
            "- Grupo mediano (10 a 16 personas): USD $55 por persona. "
            "Equilibrio perfecto entre precio, interacción y calidad de servicio.\n"
            "- Grupo grande (15 a 30 personas): USD $45 por persona. "
            "Opción más económica y social, manteniendo el estándar Wayki Trek."
        ),
        "prices": {
            "Grupo mediano (10 a 16 personas)": 55.0,
            "Grupo grande (15 a 30 personas)": 45.0,
        },
    },
    {
        "name": "Cusco - Moray & Maras",
        "description": (
            "Tarifas por tipo de grupo:\n"
            "- Grupo pequeño (4 a 10 personas): USD $60 por persona. "
            "Ideal para quienes buscan una experiencia más personalizada con mayor interacción con el guía.\n"
            "- Grupo mediano (10 a 16 personas): USD $50 por persona. "
            "Perfecto equilibrio entre servicio de calidad y precio accesible.\n"
            "- Grupo grande (15 a 30 personas): USD $40 por persona. "
            "Opción compartida más económica para viajeros sociales y grupos familiares."
        ),
        "prices": {
            "Grupo pequeño (4 a 10 personas)": 60.0,
            "Grupo mediano (10 a 16 personas)": 50.0,
            "Grupo grande (15 a 30 personas)": 40.0,
        },
    },
]


def ensure_category(client: OdooClient) -> int:
    category = client.search_read("product.category", domain=[["name", "=", CATEGORY_NAME]], fields=["id"], limit=1)
    if not category:
        raise RuntimeError(f"No existe la categoría '{CATEGORY_NAME}'.")
    return category[0]["id"]


def ensure_attribute(client: OdooClient, attribute_name: str) -> int:
    attribute = client.search_read("product.attribute", domain=[["name", "=", attribute_name]], fields=["id"], limit=1)
    if attribute:
        return attribute[0]["id"]
    return client.create(
        "product.attribute",
        {"name": attribute_name, "display_type": "radio", "create_variant": "always"},
    )


def ensure_value_ids(client: OdooClient, attribute_id: int, labels: list[str]) -> dict[str, int]:
    value_ids: dict[str, int] = {}
    for label in labels:
        value = client.search_read(
            "product.attribute.value",
            domain=[["name", "=", label], ["attribute_id", "=", attribute_id]],
            fields=["id"],
            limit=1,
        )
        value_ids[label] = value[0]["id"] if value else client.create(
            "product.attribute.value",
            {"name": label, "attribute_id": attribute_id},
        )
    return value_ids


def create_or_update_product(client: OdooClient, category_id: int, name: str, description: str) -> int:
    existing = client.search_read("product.template", domain=[["name", "=", name]], fields=["id"], limit=1)
    values = {
        "name": name,
        "categ_id": category_id,
        "type": "service",
        "sale_ok": True,
        "purchase_ok": False,
        "taxes_id": [(6, 0, [])],
        "supplier_taxes_id": [(6, 0, [])],
        "list_price": 0.0,
        "description_sale": description,
    }
    if existing:
        template_id = existing[0]["id"]
        client.write("product.template", [template_id], values)
        return template_id
    return client.create("product.template", values)


def set_group_line_only(client: OdooClient, template_id: int, group_attribute_id: int, group_value_ids: list[int]) -> None:
    # Mantener solo el atributo de grupo para que el configurador sea simple.
    lines = client.search_read(
        "product.template.attribute.line",
        domain=[["product_tmpl_id", "=", template_id]],
        fields=["id", "attribute_id"],
        limit=50,
    )
    for line in lines:
        attr = line.get("attribute_id")
        if isinstance(attr, list) and attr and attr[0] != group_attribute_id:
            client.unlink("product.template.attribute.line", [line["id"]])

    group_line = client.search_read(
        "product.template.attribute.line",
        domain=[["product_tmpl_id", "=", template_id], ["attribute_id", "=", group_attribute_id]],
        fields=["id"],
        limit=1,
    )
    if group_line:
        client.write("product.template.attribute.line", [group_line[0]["id"]], {"value_ids": [(6, 0, group_value_ids)]})
    else:
        client.create(
            "product.template.attribute.line",
            {
                "product_tmpl_id": template_id,
                "attribute_id": group_attribute_id,
                "value_ids": [(6, 0, group_value_ids)],
            },
        )


def set_price_extras(client: OdooClient, template_id: int, prices_by_label: dict[str, float], group_label_to_id: dict[str, int]) -> None:
    prices_by_value_id = {group_label_to_id[label]: amount for label, amount in prices_by_label.items()}
    ptavs = client.search_read(
        "product.template.attribute.value",
        domain=[["product_tmpl_id", "=", template_id]],
        fields=["id", "product_attribute_value_id"],
        limit=200,
    )
    for ptav in ptavs:
        pav = ptav.get("product_attribute_value_id")
        if isinstance(pav, list) and pav:
            value_id = pav[0]
            if value_id in prices_by_value_id:
                client.write("product.template.attribute.value", [ptav["id"]], {"price_extra": prices_by_value_id[value_id]})


def show_result(client: OdooClient, template_id: int, product_name: str) -> None:
    variants = client.search_read(
        "product.product",
        domain=[["product_tmpl_id", "=", template_id], ["active", "=", True]],
        fields=["display_name", "lst_price"],
        order="id asc",
        limit=30,
    )
    print(f"\n✅ {product_name}")
    for variant in variants:
        print(f"- {variant['display_name']} | USD {variant['lst_price']}")


def main() -> None:
    print("Creando tours diarios...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    category_id = ensure_category(client)
    group_attribute_id = ensure_attribute(client, GROUP_ATTR_NAME)
    # Asegurar también que exista atributo de pasajero por compatibilidad con automatización global.
    ensure_attribute(client, PASSENGER_ATTR_NAME)

    all_group_labels = sorted({label for tour in TOURS for label in tour["prices"].keys()})
    group_label_to_id = ensure_value_ids(client, group_attribute_id, all_group_labels)

    for tour in TOURS:
        template_id = create_or_update_product(client, category_id, tour["name"], tour["description"])
        labels = list(tour["prices"].keys())
        set_group_line_only(client, template_id, group_attribute_id, [group_label_to_id[label] for label in labels])
        set_price_extras(client, template_id, tour["prices"], group_label_to_id)
        show_result(client, template_id, tour["name"])

    print("\n🎉 Tours diarios creados/actualizados.")


if __name__ == "__main__":
    main()
