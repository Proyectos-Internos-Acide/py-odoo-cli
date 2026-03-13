#!/usr/bin/env python3
"""
Cargar datos de ejemplo realistas para Machu Picchu Exclusive Tours.

IMPORTANTE:
- Este script NO se debe ejecutar en producción sin tu confirmación explícita.
- Crea datos ficticios: clientes, oportunidades, proyectos/tareas y actividades.

Uso sugerido (solo después de validar configuración):
    .venv/bin/python knowledge/machu-picchu-exclusive-tours/load_sample_data.py
    docker-compose run --rm odoo-cli python knowledge/machu-picchu-exclusive-tours/load_sample_data.py
"""

import os
import random
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from odoo_cli import OdooClient  # type: ignore
from odoo_cli.exceptions import (  # type: ignore
    OdooConfigError,
    OdooConnectionError,
    OdooExecutionError,
    OdooFaultError,
)


UTC = timezone.utc


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _random_date_within_last_year() -> datetime:
    days_back = random.randint(0, 365)
    return _now() - timedelta(days=days_back)


def _random_future_date(max_days_ahead: int = 30) -> datetime:
    days_ahead = random.randint(1, max_days_ahead)
    return _now() + timedelta(days=days_ahead)


def _connect_client() -> OdooClient:
    try:
        client = OdooClient()
        client.connect()
        return client
    except (OdooConfigError, OdooConnectionError) as e:
        print(f"Error de conexión/configuración: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado al inicializar el cliente: {e}")
        sys.exit(1)


def create_partners(client: OdooClient) -> List[int]:
    print("Creando clientes (res.partner) de ejemplo...")
    first_names = [
        "John",
        "Emily",
        "Michael",
        "Sophia",
        "David",
        "Laura",
        "Carlos",
        "Ana",
        "Liam",
        "Olivia",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Martinez",
        "Brown",
        "Garcia",
        "Lopez",
        "Wilson",
        "Anderson",
        "Silva",
        "Torres",
    ]
    countries = ["US", "GB", "AU", "CA", "DE", "FR", "ES", "BR", "MX", "AR"]
    tags = ["VIP", "Honeymoon", "Family", "Solo Traveler", "Friends", "Repeat"]

    partner_ids: List[int] = []
    for idx in range(30):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        name = f"{fn} {ln}"
        email = f"{fn.lower()}.{ln.lower()}{idx}@example.com"
        phone = f"+1-555-{random.randint(1000000, 9999999)}"
        passport = f"P{random.randint(1000000, 9999999)}"
        country_code = random.choice(countries)

        vals: Dict[str, Any] = {
            "name": name,
            "email": email,
            "phone": phone,
            "country_id": False,  # se puede ajustar manualmente si se desea
            "comment": f"Pasaporte: {passport}",
        }

        partner_id = client.create("res.partner", vals)
        partner_ids.append(partner_id)

        if random.random() < 0.7:
            chosen_tags = random.sample(tags, k=random.randint(1, 2))
            print(f"- {name} ({email}) [{', '.join(chosen_tags)}]")
        else:
            print(f"- {name} ({email})")

    print(f"Total de clientes creados: {len(partner_ids)}")
    return partner_ids


def create_opportunities(client: OdooClient, partner_ids: List[int]) -> List[int]:
    print("Creando oportunidades (crm.lead) de ejemplo...")
    destinations = ["Cusco & Machu Picchu", "Sacred Valley", "Arequipa & Colca", "Lima Gourmet"]

    lead_ids: List[int] = []
    for _ in range(25):
        partner_id = random.choice(partner_ids)
        nights = random.randint(3, 14)
        destination = random.choice(destinations)
        expected_revenue = random.randint(1500, 8000)
        create_date = _random_date_within_last_year()

        vals: Dict[str, Any] = {
            "name": f"Viaje {destination} ({nights} noches)",
            "partner_id": partner_id,
            "expected_revenue": float(expected_revenue),
            "description": f"Programa personalizado de {nights} días para {destination}.",
        }

        lead_id = client.create("crm.lead", vals)
        lead_ids.append(lead_id)

    print(f"Total de oportunidades creadas: {len(lead_ids)}")
    return lead_ids


def get_or_create_reservations_project(client: OdooClient) -> int:
    projects = client.search_read(
        "project.project",
        domain=[["name", "=", "Reservas Machu Picchu Exclusive Tours"]],
        fields=["id"],
        limit=1,
    )
    if projects:
        return int(projects[0]["id"])
    return client.create("project.project", {"name": "Reservas Machu Picchu Exclusive Tours"})


def create_projects_and_tasks(
    client: OdooClient,
    project_id: int,
    partner_ids: List[int],
    lead_ids: List[int],
) -> List[int]:
    print("Creando tareas de proyecto (viajes/itinerarios)...")

    task_ids: List[int] = []

    stages = client.search_read(
        "project.task.type",
        domain=[["name", "in", [s for s in [
            "Borrador de Cotización",
            "Confirmación (Adelanto)",
            "Compra de Tickets/Hoteles",
            "Venta Final (Ejecución)",
        ]]]],
        fields=["id", "name"],
    )
    stage_by_name = {s["name"]: int(s["id"]) for s in stages if s.get("name") and s.get("id")}

    stage_names_cycle = [
        "Borrador de Cotización",
        "Confirmación (Adelanto)",
        "Compra de Tickets/Hoteles",
        "Venta Final (Ejecución)",
    ]

    for _ in range(20):
        partner_id = random.choice(partner_ids)
        lead_id = random.choice(lead_ids) if lead_ids else False
        stage_name = random.choice(stage_names_cycle)
        stage_id = stage_by_name.get(stage_name)
        start_date = _random_date_within_last_year()

        vals: Dict[str, Any] = {
            "name": f"Reserva para cliente {partner_id}",
            "project_id": project_id,
            "partner_id": partner_id,
            "date_deadline": _random_future_date(60).date().isoformat(),
        }
        if stage_id:
            vals["stage_id"] = stage_id
        if lead_id:
            vals["description"] = f"Oportunidad relacionada ID {lead_id}"

        task_id = client.create("project.task", vals)
        task_ids.append(task_id)

    print(f"Total de tareas de reserva creadas: {len(task_ids)}")
    return task_ids


def get_or_create_products(client: OdooClient) -> List[int]:
    """Obtener o crear productos/servicios turísticos para ventas y compras."""
    print("Obteniendo/creando productos turísticos...")
    products_info = [
        ("Paquete Cusco & Machu Picchu 4D/3N", 890.0),
        ("Paquete Sacred Valley 2D/1N", 420.0),
        ("Ticket Tren Machu Picchu (ida y vuelta)", 180.0),
        ("Guía privado Machu Picchu", 95.0),
        ("Hotel 3* Cusco - Noche", 85.0),
        ("Transfer Aeropuerto - Hotel", 45.0),
        ("Tour Colca 2D/1N", 320.0),
        ("Boleto Turístico Cusco", 70.0),
        ("Almuerzo Buffet Valle Sagrado", 35.0),
        ("Fee administrativo", 25.0),
    ]
    product_ids: List[int] = []
    for name, list_price in products_info:
        existing = client.search_read(
            "product.template",
            domain=[["name", "=", name]],
            fields=["id"],
            limit=1,
        )
        if existing:
            product_ids.append(int(existing[0]["id"]))
            continue
        pid = client.create(
            "product.template",
            {
                "name": name,
                "type": "service",
                "list_price": list_price,
                "sale_ok": True,
                "purchase_ok": True,
                "invoice_policy": "order",
            },
        )
        product_ids.append(pid)
    print(f"  Productos disponibles: {len(product_ids)}")
    return product_ids


def _get_product_for_line(client: OdooClient, product_tmpl_id: int) -> int:
    """Obtener product.product ID desde product.template."""
    variants = client.search_read(
        "product.product",
        domain=[["product_tmpl_id", "=", product_tmpl_id]],
        fields=["id"],
        limit=1,
    )
    return int(variants[0]["id"]) if variants else product_tmpl_id


def create_sale_orders(
    client: OdooClient,
    partner_ids: List[int],
    lead_ids: List[int],
    product_ids: List[int],
) -> List[int]:
    print("Creando presupuestos y pedidos de venta (sale.order)...")
    order_ids: List[int] = []
    for _ in range(35):
        partner_id = random.choice(partner_ids)
        lead_id = random.choice(lead_ids) if lead_ids else None
        num_lines = random.randint(1, 4)
        lines: List[Tuple[str, Dict[str, Any]]] = []
        total = 0.0
        for _ in range(num_lines):
            prod_tmpl_id = random.choice(product_ids)
            product_id = _get_product_for_line(client, prod_tmpl_id)
            qty = random.choice([1.0, 2.0, 3.0, 4.0, 1.0])
            prod = client.search_read(
                "product.template",
                domain=[["id", "=", prod_tmpl_id]],
                fields=["list_price"],
                limit=1,
            )
            price = float(prod[0].get("list_price", 100)) if prod else 100.0
            discount = random.choice([0, 0, 0, 5, 10])
            subtotal = qty * price * (1 - discount / 100)
            total += subtotal
            lines.append(
                (
                    0,
                    0,
                    {
                        "product_id": product_id,
                        "product_uom_qty": qty,
                        "price_unit": price,
                        "discount": discount,
                    },
                )
            )
        vals: Dict[str, Any] = {
            "partner_id": partner_id,
            "order_line": lines,
        }
        if lead_id:
            vals["opportunity_id"] = lead_id
        so_id = client.create("sale.order", vals)
        order_ids.append(so_id)
        # Confirmar en la interfaz Odoo; action_confirm vía API falla en Odoo SaaS
    print(f"Total de órdenes de venta creadas: {len(order_ids)}")
    return order_ids


def create_suppliers(client: OdooClient) -> List[int]:
    print("Creando proveedores para compras...")
    suppliers = [
        ("Inca Rail", "contacto@incarail.com"),
        ("PeruRail", "ventas@perurail.com"),
        ("Belmond Sanctuary Lodge", "reservas@belmond.com"),
        ("Hoteles Libertador", "reservas@libertador.com"),
        ("Tren a Machu Picchu SAC", "info@trenmachupicchu.com"),
    ]
    ids: List[int] = []
    for name, email in suppliers:
        existing = client.search_read(
            "res.partner",
            domain=[["name", "=", name]],
            fields=["id"],
            limit=1,
        )
        if existing:
            ids.append(int(existing[0]["id"]))
            continue
        pid = client.create(
            "res.partner",
            {"name": name, "email": email, "supplier_rank": 1, "is_company": True},
        )
        ids.append(pid)
    print(f"  Proveedores: {len(ids)}")
    return ids


def create_purchase_orders(
    client: OdooClient,
    supplier_ids: List[int],
    product_ids: List[int],
) -> List[int]:
    print("Creando órdenes de compra (purchase.order)...")
    try:
        models = client.search_read(
            "ir.model",
            domain=[["model", "=", "purchase.order"]],
            fields=["id"],
            limit=1,
        )
        if not models:
            print("  Módulo de compras no instalado, se omite.")
            return []
    except (OdooFaultError, OdooExecutionError):
        print("  Módulo de compras no instalado, se omite.")
        return []
    order_ids: List[int] = []
    for _ in range(25):
        partner_id = random.choice(supplier_ids)
        prod_tmpl_id = random.choice(product_ids)
        product_id = _get_product_for_line(client, prod_tmpl_id)
        qty = random.choice([1.0, 2.0, 5.0, 10.0, 20.0])
        prod = client.search_read(
            "product.template",
            domain=[["id", "=", prod_tmpl_id]],
            fields=["list_price"],
            limit=1,
        )
        price = float(prod[0].get("list_price", 50)) * 0.7 if prod else 50.0
        po_id = client.create(
            "purchase.order",
            {"partner_id": partner_id},
        )
        client.create(
            "purchase.order.line",
            {
                "order_id": po_id,
                "product_id": product_id,
                "product_qty": qty,
                "price_unit": round(price, 2),
                "date_planned": _random_future_date(14).strftime("%Y-%m-%d 12:00:00"),
            },
        )
        order_ids.append(po_id)
        if random.random() < 0.6:
            try:
                client.execute("purchase.order", "button_confirm", [[po_id]])
            except (OdooFaultError, OdooExecutionError):
                pass
    print(f"Total de órdenes de compra creadas: {len(order_ids)}")
    return order_ids


def create_activities(client: OdooClient, partner_ids: List[int]) -> int:
    print("Creando actividades de seguimiento (mail.activity)...")

    activity_types = client.search_read(
        "mail.activity.type",
        domain=[],
        fields=["id", "name"],
        limit=10,
    )
    if not activity_types:
        print("No se encontraron tipos de actividad, se omite la creación de actividades.")
        return 0

    models = client.search_read(
        "ir.model",
        domain=[["model", "=", "res.partner"]],
        fields=["id"],
        limit=1,
    )
    if not models:
        print("No se encontró ir.model para res.partner, se omite la creación de actividades.")
        return 0

    activity_type_id = int(activity_types[0]["id"])
    res_model_id = int(models[0]["id"])

    created = 0
    for partner_id in random.sample(partner_ids, k=min(len(partner_ids), 15)):
        vals: Dict[str, Any] = {
            "res_model": "res.partner",
            "res_id": int(partner_id),
            "res_model_id": res_model_id,
            "activity_type_id": activity_type_id,
            "summary": "Seguimiento de viaje",
            "date_deadline": _random_future_date(30).date().isoformat(),
        }
        try:
            client.create("mail.activity", vals)
            created += 1
        except (OdooFaultError, OdooExecutionError):
            pass  # Algunas instancias restringen la creación de actividades vía API
    print(f"Total de actividades creadas: {created}")
    return created


def main() -> None:
    print("--- Carga de datos de ejemplo para Machu Picchu Exclusive Tours ---")
    client = _connect_client()

    try:
        partners = create_partners(client)
        products = get_or_create_products(client)
        suppliers = create_suppliers(client)
        leads = create_opportunities(client, partners)
        project_id = get_or_create_reservations_project(client)
        tasks = create_projects_and_tasks(client, project_id, partners, leads)
        sale_orders = create_sale_orders(client, partners, leads, products)
        purchase_orders = create_purchase_orders(client, suppliers, products)
        activities_count = create_activities(client, partners)

        print("Resumen de carga de datos:")
        print(f"- Clientes creados: {len(partners)}")
        print(f"- Oportunidades creadas: {len(leads)}")
        print(f"- Tareas de reserva creadas: {len(tasks)}")
        print(f"- Presupuestos/pedidos de venta: {len(sale_orders)}")
        print(f"- Órdenes de compra: {len(purchase_orders)}")
        print(f"- Actividades creadas: {activities_count}")
    except (OdooConnectionError, OdooFaultError, OdooExecutionError) as e:
        print(f"Error durante la carga de datos: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado durante la carga de datos: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

