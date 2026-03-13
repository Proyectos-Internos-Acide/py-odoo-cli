Aquí tienes la guía completa estructurada en **Markdown**, lista para que la copies, pegues en tus notas (Notion, Obsidian, etc.) o la imprimas para tu configuración.

---

# 🏔️ Guía de Demo Odoo: Agencia de Viajes "Andes Explorer"

**Objetivo:** Demostrar a *Peru Flores* y *Machupicchu* cómo Odoo centraliza CRM, Ventas, Operaciones y Facturación en un solo flujo.

---

## 1. El Escenario (Storytelling)

Para la demo, no hables de "módulos", habla de **la historia de un cliente**.

> **La Agencia:** "Andes Explorer" (Cusco).
> **El Problema:** Pierden tiempo cotizando en Excel, olvidan reservar a proveedores y no saben cuánto ganan por grupo.
> **El Cliente Ficticio:** Juan Pérez (España).
> **El Pedido:** Paquete "Cusco Mágico 3D/2N" para 2 personas (Hotel + Tours + Traslados).

---

## 2. Configuración Técnica (Hacer ANTES de la reunión)

### A. Módulos a Instalar

Asegúrate de tener instaladas estas aplicaciones en tu base de datos Odoo:

* [x] **CRM** (Gestión de Leads)
* [x] **Ventas** (Sales)
* [x] **Compras** (Purchase) - *Clave para reservar a terceros.*
* [x] **Inventario** (Inventory) - *Para manejar rutas de servicio.*
* [x] **Facturación/Contabilidad** (Invoicing/Accounting)
* [x] **Fabricación** (Manufacturing) - *¡OJO! Necesario para habilitar la función de "Kits" (Paquetes).*
* [ ] **Constructor de Presupuestos** (Sale Management Add-on) - *Para PDFs con imágenes y descripciones largas.*

### B. Configuración de Productos

Debes crear 3 tipos de productos para que la magia funcione:

#### 1. Producto Proveedor (Lo que compras)

* **Nombre:** `Noche Hotel *** (Cusco)`
* **Tipo:** **Servicio**.
> [!IMPORTANT]
> **Nota técnica para el Consultor:** Manejar los componentes y paquetes siempre como **Servicios** y NO como Bienes/Almacenables. Esto evita generar movimientos de stock innecesarios y albaranes de entrega que no aplican a turismo, manteniendo el flujo de operaciones limpio.
* **Pestaña Compra:**
* Marcar: ☑️ Se puede comprar.
* Proveedor: Crear "Hotel Los Portales".
* Precio: $50 (Costo).


* **Pestaña Inventario (Rutas):**
* Marcar: ☑️ **Comprar** (Buy) y ☑️ **Obtener bajo pedido** (MTO / Replenish on Order).
* *Nota:* Esto hace que al venderlo, Odoo cree la Orden de Compra automáticamente.



#### 2. Producto Propio (Tu ganancia)

* **Nombre:** `Fee de Agencia / Gestión`
* **Tipo:** Servicio.
* **Precio de Venta:** $50.

#### 3. El Paquete (El Kit de Venta)

* **Nombre:** `Paquete Cusco Mágico 3D/2N`
* **Tipo:** Servicio (o Consumible).
* **Precio de Venta:** $500.
* **Lista de Materiales (BoM):**
* Ve al botón inteligente **"Lista de Materiales"** arriba del producto.
* Crea una nueva.
* **Tipo de BoM:** **Kit** (Fantasma).
* **Componentes:**
* 2 x `Noche Hotel *** (Cusco)`
* 1 x `Fee de Agencia / Gestión`
* 1 x `Traslado Aeropuerto (Servicio Tercero)`

#### 4. Plantillas de Presupuesto (Itinerarios)

*   Ve a **Ventas > Configuración > Plantillas de presupuesto**.
*   Crea una llamada `Programa: Cusco Mágico`.
*   Añade el producto `Paquete Cusco Mágico 3D/2N`.
*   **Secciones y Notas:** Usa la pestaña "Líneas del pedido" para añadir secciones como `Día 1: Arribo y City Tour`, `Día 2: Valle Sagrado`, etc. Esto es lo que genera el PDF detallado (Programa).





---

## 3. Guion de la Demostración (Paso a Paso)

### Paso 1: CRM (La Captación)

1. Entra al módulo **CRM**.
2. Crea una oportunidad rápida: *"Juan Pérez - Interés Cusco 3D/2N"*.
3. Muestra el flujo visual (Kanban).
4. **Acción:** Agenda una actividad (relojito) tipo "Llamada de seguimiento" para mañana.
> *"Odoo no deja que se les enfríe ningún cliente, el sistema les recuerda llamar."*



### Paso 2: Ventas (La Cotización Flash)

1. Dentro de la oportunidad, clic en **"Nuevo Presupuesto"**.
2. **Usa la Plantilla:** Selecciona la plantilla `Programa: Cusco Mágico`.
3. Muestra cómo Odoo carga no solo el precio, sino todo el **itinerario detallado** (Notas y Secciones).
4. **El momento "Wow":** Clic en **Enviar por correo**.
5. Clic en **Vista Previa** (o abre el PDF).
6. Muestra que el PDF no es una simple factura, sino un **Programa de Viaje Detallado** (Como el PDF de ejemplo de Camino Inca).
    *   *Tip:* Explica que pueden añadir fotos y descripciones ricas usando el "Constructor de Presupuestos".

### Paso 3: Operaciones (Automatización)

1. Clic en **Confirmar** la venta.
2. Señala el botón inteligente **"Compra"** que aparece arriba a la derecha.
3. Entra y muéstrales que Odoo **ya creó la Orden de Compra** para el "Hotel Los Portales" por las 2 noches.
> *"¿Vieron? No tuvieron que llamar al hotel. Odoo ya redactó el correo de reserva por ustedes."*



### Paso 4: Rentabilidad (El Dinero)

1. Vuelve al pedido de venta.
2. Muestra el **Margen** (si tienes el módulo de márgenes activo) o explica la **Cuenta Analítica**.
* Venta: $500
* Costo (Hotel + Traslados): $350
* **Utilidad:** $150


3. Clic en **Crear Factura** para generar el borrador de la Factura Electrónica.

---

## 4. Tips Avanzados (As bajo la manga)

* **Variantes de Producto:**
* Crea un producto `Tour Valle Sagrado` con atributos: **Servicio** (Privado / Compartido).
* Muestra cómo el precio cambia solo al seleccionar "Privado".


* **Plantillas de Correo:**
* Ten lista una plantilla de email bonita que diga: *"Hola Juan, aquí tienes tu itinerario soñado..."* para que vean la personalización.



---

### ✅ Checklist Pre-Demo

* [ ] Logo de "Andes Explorer" subido a Odoo.
* [ ] Moneda configurada (Soles o Dólares, según usen ellos).
* [ ] Datos de demo limpios (borra pruebas fallidas anteriores).
* [ ] Laptop cargada y acceso a internet verificado (o base de datos local).