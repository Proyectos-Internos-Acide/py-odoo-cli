#!/usr/bin/env python3
"""
Crea productos en categoría "Tours diarios" para Machu Picchu:
- 1 día (Expedition/Voyager, Vistadome, Hiram Bingham)
- 2 días (Expedition/Voyager, Vistadome)
- 3 días (Expedition/Voyager, Vistadome)

Trazabilidad:
- Atributo "Tipo de pasajero" preseleccionado con Adulto/Estudiante/Niño.
- "Tipo de pasajero" siempre en price_extra = 0.

Precios:
- Precio base del producto = 0
- Atributo "Tipo de tren" define price_extra para cada variante.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


CATEGORY_NAME = "Tours diarios"
PASSENGER_ATTR_NAME = "Tipo de pasajero"
TRAIN_ATTR_NAME = "Tipo de tren"

PASSENGERS = ["Adulto", "Estudiante", "Niño"]


PRODUCTS = [
    {
        "name": "Machu Picchu - Machu Picchu 1 día",
        "description": (
            "Viaja desde Cusco hacia la ciudadela sagrada de los incas en un día completo "
            "organizado al detalle. Disfruta de un recorrido guiado en grupo compartido, con "
            "transporte, tren, entradas y logística incluida. Ideal para quienes disponen "
            "de poco tiempo, pero no quieren irse del Perú sin descubrir Machu Picchu. "
            "¡Una experiencia intensa, eficiente y profundamente memorable!\n\n"
            "Con Wayki Trek puedes visitar Machu Picchu en un solo día con la tranquilidad de "
            "un servicio organizado, seguro y con opciones que se ajustan a tu estilo de viaje. "
            "Ya sea en tren turístico, panorámico o de lujo, la experiencia será inolvidable."
        ),
        "train_prices": {
            "Tren Expedition / Voyager": 320.0,
            "Tren Vistadome": 370.0,
            "Tren Hiram Bingham": 950.0,
        },
    },
    {
        "name": "Machu Picchu - Machu Picchu 2 días",
        "description": (
            "Este viaje de 2 días combina cultura viva, paisajes sagrados y la majestuosidad "
            "de Machu Picchu en un recorrido privado y profundamente personalizado. Desde "
            "Moray y las Salineras hasta el corazón de la ciudadela inca, caminarás al ritmo "
            "de tu historia, con guía exclusivo, atención a cada detalle y tiempo real para "
            "absorber la energía de los Apus. Ideal para viajeros que buscan profundidad, calidad "
            "y conexión."
        ),
        "train_prices": {
            "Tren Expedition / Voyager": 520.0,
            "Tren Vistadome": 590.0,
        },
    },
    {
        "name": "Machu Picchu - Machu Picchu 3 días",
        "description": (
            "Este itinerario de 3 días te lleva a través del corazón del legado inca: desde los "
            "templos ancestrales de Cusco, pasando por los laboratorios agrícolas de Moray y las "
            "salineras vivas de Maras, hasta llegar sin prisas a Machu Picchu. Diseñado en servicio "
            "privado, combina un ritmo flexible, guía especialista y humano, traslados confortables, "
            "alimentación seleccionada, alojamiento con estándares Wayki y acompañamiento constante. "
            "Ideal para quienes buscan profundidad cultural, conexión natural y una logística sin fallos. "
            "Porque el camino también importa, tanto como el destino."
        ),
        "train_prices": {
            "Tren Expedition / Voyager": 640.0,
            "Tren Vistadome": 710.0,
        },
    },
]


def ensure_category(client: OdooClient) -> int:
    rec = client.search_read(
        "product.category", domain=[["name", "=", CATEGORY_NAME]], fields=["id"], limit=1
    )
    if not rec:
        raise RuntimeError(f"No existe la categoría {CATEGORY_NAME}")
    return rec[0]["id"]


def ensure_attribute(client: OdooClient, name: str) -> int:
    rec = client.search_read("product.attribute", domain=[["name", "=", name]], fields=["id"], limit=1)
    if rec:
        return rec[0]["id"]
    return client.create(
        "product.attribute",
        {"name": name, "display_type": "radio", "create_variant": "always"},
    )


def ensure_attribute_values(client: OdooClient, attr_id: int, labels: list[str]) -> dict[str, int]:
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


def get_or_create_template(client: OdooClient, name: str, categ_id: int, description: str) -> int:
    tmpl = client.search_read(
        "product.template", domain=[["name", "=", name]], fields=["id"], limit=1
    )
    vals = {
        "name": name,
        "categ_id": categ_id,
        "type": "service",
        "sale_ok": True,
        "purchase_ok": False,
        "taxes_id": [(6, 0, [])],
        "supplier_taxes_id": [(6, 0, [])],
        # Base must be 0; pricing comes from price_extra of attribute values.
        "list_price": 0.0,
        "description_sale": description,
    }
    if tmpl:
        client.write("product.template", [tmpl[0]["id"]], vals)
        return tmpl[0]["id"]
    return client.create("product.template", vals)


def ensure_template_attribute_line(client: OdooClient, tmpl_id: int, attr_id: int, value_ids: list[int]) -> None:
    line = client.search_read(
        "product.template.attribute.line",
        domain=[["product_tmpl_id", "=", tmpl_id], ["attribute_id", "=", attr_id]],
        fields=["id"],
        limit=1,
    )
    if line:
        client.write(
            "product.template.attribute.line",
            [line[0]["id"]],
            {"value_ids": [(6, 0, value_ids)]},
        )
    else:
        client.create(
            "product.template.attribute.line",
            {
                "product_tmpl_id": tmpl_id,
                "attribute_id": attr_id,
                "value_ids": [(6, 0, value_ids)],
            },
        )


def set_price_extras_for_template_values(
    client: OdooClient,
    tmpl_id: int,
    passenger_value_ids: list[int],
    train_value_price: dict[int, float],
) -> None:
    # Ajusta price_extra para las combinaciones del producto.
    ptavs = client.search_read(
        "product.template.attribute.value",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["id", "product_attribute_value_id", "price_extra"],
        limit=500,
    )

    for row in ptavs:
        pav = row.get("product_attribute_value_id")
        if not isinstance(pav, list) or not pav:
            continue
        pav_id = pav[0]

        if pav_id in passenger_value_ids:
            # Pasajero siempre 0 para trazabilidad.
            if row.get("price_extra") != 0.0:
                client.write("product.template.attribute.value", [row["id"]], {"price_extra": 0.0})
            continue

        if pav_id in train_value_price:
            amount = train_value_price[pav_id]
            if row.get("price_extra") != amount:
                client.write("product.template.attribute.value", [row["id"]], {"price_extra": amount})


def show_variants(client: OdooClient, tmpl_id: int, product_name: str) -> None:
    variants = client.search_read(
        "product.product",
        domain=[["product_tmpl_id", "=", tmpl_id], ["active", "=", True]],
        fields=["display_name", "lst_price"],
        limit=200,
        order="id asc",
    )
    print(f"\n✅ {product_name}")
    for v in variants:
        print(f"- {v['display_name']} | USD {v['lst_price']}")


def main() -> None:
    print("Creando/actualizando tours diarios Machu Picchu...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    categ_id = ensure_category(client)
    passenger_attr_id = ensure_attribute(client, PASSENGER_ATTR_NAME)
    train_attr_id = ensure_attribute(client, TRAIN_ATTR_NAME)

    passenger_value_map = ensure_attribute_values(client, passenger_attr_id, PASSENGERS)
    passenger_value_ids = [passenger_value_map[x] for x in PASSENGERS]

    for product in PRODUCTS:
        tmpl_id = get_or_create_template(client, product["name"], categ_id, product["description"])

        # Asegurar lineas de atributos
        ensure_template_attribute_line(client, tmpl_id, passenger_attr_id, passenger_value_ids)

        train_labels = list(product["train_prices"].keys())
        train_value_map = ensure_attribute_values(client, train_attr_id, train_labels)
        train_value_ids = [train_value_map[x] for x in train_labels]
        ensure_template_attribute_line(client, tmpl_id, train_attr_id, train_value_ids)

        # price_extra:
        train_value_price = {train_value_map[label]: price for label, price in product["train_prices"].items()}
        set_price_extras_for_template_values(
            client,
            tmpl_id,
            passenger_value_ids=passenger_value_ids,
            train_value_price=train_value_price,
        )
        show_variants(client, tmpl_id, product["name"])

    print("\n🎉 Listo.")


if __name__ == "__main__":
    main()

