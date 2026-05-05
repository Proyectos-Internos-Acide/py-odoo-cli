#!/usr/bin/env python3
"""
Crea/actualiza tours de Caminatas Cortas (Montaña 7 Colores y Laguna Humantay)
en la categoría "Tours diarios", con precios por tipo de grupo.

No se usa "Tipo de pasajero" en estos productos, solo "Tipo de grupo".
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


CATEGORY_NAME = "Tours diarios"
GROUP_ATTR_NAME = "Tipo de grupo"


PRODUCTS = [
    {
        "name": "Caminatas Cortas - Montaña de 7 Colores",
        "description": (
            "Ubicada a más de 5,000 m s.n.m., la Montaña de 7 Colores (Vinicunca) es una de las "
            "maravillas naturales más impactantes del Perú. Este tour de aventura te llevará a través "
            "de paisajes altiplánicos, comunidades andinas y vistas de glaciares. Ideal para viajeros "
            "activos que buscan una experiencia desafiante y gratificante en un solo día.\n\n"
            "Conquista la Montaña de 7 Colores con un servicio completo, seguro y accesible. Te "
            "ofrecemos diferentes tarifas según el tamaño del grupo, descuentos especiales y la "
            "posibilidad de personalizar tu experiencia sin afectar la calidad."
        ),
        "prices": {
            "Grupo pequeño (4 a 10 personas)": 75.0,
            "Grupo mediano (10 a 16 personas)": 65.0,
            "Grupo grande (15 a 30 personas)": 55.0,
        },
    },
    {
        "name": "Caminatas Cortas - Laguna Humantay",
        "description": (
            "Ubicada a los pies del imponente nevado Salkantay, la Laguna Humantay es una joya "
            "natural de aguas color turquesa rodeada de montañas sagradas. Esta caminata de un día "
            "combina naturaleza, espiritualidad y desafío físico en un entorno inolvidable. Ideal para "
            "viajeros que ya se han aclimatado y buscan vivir una experiencia intensa y gratificante en "
            "los Andes. ¡Una ruta que conecta el cuerpo con la montaña y el alma con la naturaleza!\n\n"
            "Te ofrecemos diferentes tarifas según el tamaño del grupo, descuentos especiales y la "
            "posibilidad de personalizar tu experiencia sin afectar la calidad."
        ),
        "prices": {
            "Grupo pequeño (4 a 10 personas)": 75.0,
            "Grupo mediano (10 a 16 personas)": 65.0,
            "Grupo grande (15 a 30 personas)": 55.0,
        },
    },
]


def ensure_category(client: OdooClient) -> int:
    rec = client.search_read(
        "product.category", domain=[["name", "=", CATEGORY_NAME]], fields=["id"], limit=1
    )
    if not rec:
        raise RuntimeError(f"No existe la categoría '{CATEGORY_NAME}'.")
    return rec[0]["id"]


def ensure_group_attribute(client: OdooClient) -> int:
    rec = client.search_read(
        "product.attribute", domain=[["name", "=", GROUP_ATTR_NAME]], fields=["id"], limit=1
    )
    if rec:
        return rec[0]["id"]
    return client.create(
        "product.attribute",
        {"name": GROUP_ATTR_NAME, "display_type": "radio", "create_variant": "always"},
    )


def ensure_group_values(client: OdooClient, attr_id: int, labels: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for label in labels:
        rec = client.search_read(
            "product.attribute.value",
            domain=[["name", "=", label], ["attribute_id", "=", attr_id]],
            fields=["id"],
            limit=1,
        )
        if rec:
            out[label] = rec[0]["id"]
        else:
            out[label] = client.create(
                "product.attribute.value",
                {"name": label, "attribute_id": attr_id},
            )
    return out


def create_or_update_product(
    client: OdooClient, category_id: int, name: str, description: str
) -> int:
    existing = client.search_read(
        "product.template", domain=[["name", "=", name]], fields=["id"], limit=1
    )
    vals = {
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
        tmpl_id = existing[0]["id"]
        client.write("product.template", [tmpl_id], vals)
        return tmpl_id
    return client.create("product.template", vals)


def keep_only_group_attribute_line(
    client: OdooClient, tmpl_id: int, group_attr_id: int, group_value_ids: list[int]
) -> None:
    lines = client.search_read(
        "product.template.attribute.line",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["id", "attribute_id"],
        limit=50,
    )
    for line in lines:
        attr = line.get("attribute_id")
        if isinstance(attr, list) and attr and attr[0] != group_attr_id:
            client.unlink("product.template.attribute.line", [line["id"]])

    group_line = client.search_read(
        "product.template.attribute.line",
        domain=[["product_tmpl_id", "=", tmpl_id], ["attribute_id", "=", group_attr_id]],
        fields=["id"],
        limit=1,
    )
    if group_line:
        client.write(
            "product.template.attribute.line",
            [group_line[0]["id"]],
            {"value_ids": [(6, 0, group_value_ids)]},
        )
    else:
        client.create(
            "product.template.attribute.line",
            {
                "product_tmpl_id": tmpl_id,
                "attribute_id": group_attr_id,
                "value_ids": [(6, 0, group_value_ids)],
            },
        )


def set_group_price_extras(
    client: OdooClient,
    tmpl_id: int,
    prices_by_label: dict[str, float],
    group_label_to_id: dict[str, int],
) -> None:
    prices_by_value_id = {group_label_to_id[label]: price for label, price in prices_by_label.items()}
    ptavs = client.search_read(
        "product.template.attribute.value",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["id", "product_attribute_value_id"],
        limit=200,
    )
    for row in ptavs:
        pav = row.get("product_attribute_value_id")
        if isinstance(pav, list) and pav:
            vid = pav[0]
            if vid in prices_by_value_id:
                client.write(
                    "product.template.attribute.value",
                    [row["id"]],
                    {"price_extra": prices_by_value_id[vid]},
                )


def show_result(client: OdooClient, tmpl_id: int, name: str) -> None:
    variants = client.search_read(
        "product.product",
        domain=[["product_tmpl_id", "=", tmpl_id], ["active", "=", True]],
        fields=["display_name", "lst_price"],
        limit=50,
        order="id asc",
    )
    print(f"\n✅ {name}")
    for v in variants:
        print(f"- {v['display_name']} | USD {v['lst_price']}")


def main() -> None:
    print("Creando/actualizando tours de Caminatas Cortas...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    categ_id = ensure_category(client)
    group_attr_id = ensure_group_attribute(client)

    all_group_labels = sorted({label for p in PRODUCTS for label in p["prices"].keys()})
    group_label_to_id = ensure_group_values(client, group_attr_id, all_group_labels)

    for p in PRODUCTS:
        tmpl_id = create_or_update_product(client, categ_id, p["name"], p["description"])
        labels = list(p["prices"].keys())
        group_value_ids = [group_label_to_id[l] for l in labels]
        keep_only_group_attribute_line(client, tmpl_id, group_attr_id, group_value_ids)
        set_group_price_extras(client, tmpl_id, p["prices"], group_label_to_id)
        show_result(client, tmpl_id, p["name"])

    print("\n🎉 Listo.")


if __name__ == "__main__":
    main()

