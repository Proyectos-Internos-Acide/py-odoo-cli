# 📦 Guía: Configuración de Paquetes Turísticos (Kits)

En esta guía aprenderás a usar la función de **Kit** para vender un paquete ("Cusco Mágico") que descuenta o reserva servicios individuales (Hotel, Guía, etc.) sin ser un producto físico.

---

## 1. ¿Por qué usar un Kit?

En turismo, un paquete no es algo que guardas en un estante. Es una agrupación de servicios. El Kit te permite:
*   Vender un solo ítem al cliente.
*   Mantener el control de costos de cada componente por separado.
*   Automatizar las reservas a los proveedores de cada componente.

---

## 2. Paso a Paso: Creación del Kit

### A. Crear los componentes (Servicios)
Primero crea los servicios individuales (ej. Hotel, Tour).
1.  Vaya a **Ventas > Productos**.
2.  Asegúrese de que el **Tipo de Producto** sea **Servicio**.
3.  En la pestaña **Inventario**, marque la ruta **Comprar** y **Bajo pedido (MTO)**.

### B. Crear el Paquete (Producto Principal)
1.  Cree un producto llamado `Paquete Cusco Mágico`.
2.  **Tipo de Producto**: **Servicio**.
3.  Haga clic en el botón inteligente **Lista de Materiales** (arriba a la derecha).

### C. Configurar la Lista de Materiales (LdM)
![Odoo Kit BoM](https://www.odoo.com/web/image/75217822-e421be00/mrp_kit_bom.png)

1.  Haga clic en **Nuevo**.
2.  **Tipo de LdM**: Seleccione obligatoriamente **Kit**.
3.  **Componentes**: Añada los servicios base (2 noches de hotel, 1 tour, etc.).

---

## 3. Resultado en la Venta

Cuando agregas el `Paquete Cusco Mágico` a una cotización:
1.  El cliente solo ve el nombre del paquete y el precio total.
2.  **Internamente**: Odoo "rompe" el kit y sabe que debe gestionar el hotel y el tour vinculados.

---

> [!IMPORTANT]
> **Esencia Odoo LatAm:** Para que los Kits funcionen, debe tener instalado el módulo de **Fabricación (MRP)**, ya que ahí es donde reside la lógica de las Listas de Materiales.

---
*Referencia: [Kits en Odoo](https://www.odoo.com/documentation/17.0/es/applications/inventory_and_mrp/manufacturing/management/kit_shipping.html)*
