Aquí tienes el **Set de Datos de Prueba** formateado en Markdown, listo para copiar y pegar en tu documentación o notas.

---

# 📂 Data de Prueba (Dummy Data) - Odoo Agencia de Viajes

**Objetivo:** Poblar la base de datos para que la demo se vea real, viva y profesional.

---

## 1. Contactos: Proveedores (Partners - Suppliers)

*Ruta: Módulo Contactos (o Compras > Proveedores)*

| Nombre | Tipo | RUC (Ficticio) | Notas Internas / Etiquetas |
| --- | --- | --- | --- |
| **Hotel Casa Andina Standard** | Compañía | 20123456781 | `Hotel` `Cusco` `Crédito 30 días` |
| **Transportes El Chasqui** | Compañía | 20876543219 | `Transporte` `Puntual` `Minivan H-1` |
| **Inca Rail** | Compañía | 20555555551 | `Tren` `Tickets` |
| **Carlos Mamani (Guía)** | Individual | 10456789012 | `Guía Oficial` `Inglés` `Francés` |
| **Restaurante Tunupa** | Compañía | 20987654321 | `Restaurante` `Buffet` `Valle Sagrado` |

---

## 2. Contactos: Clientes (Partners - Customers)

*Ruta: Módulo CRM o Ventas > Clientes*
*Tip: ¡Sube fotos reales de personas sonriendo!*

| Nombre | País | Email | Notas del CRM |
| --- | --- | --- | --- |
| **Juan Pérez & Familia** | 🇪🇸 España | `juan.perez@demo.com` | Viajan con 2 niños. Piden comida vegetariana. |
| **Sarah Smith** | 🇺🇸 USA | `sarah.smith@demo.com` | Cliente VIP. Busca hoteles 5 estrellas. |
| **Grupo Estudiantes BsAs** | 🇦🇷 Argentina | `grupo@demo.com` | Presupuesto ajustado (Mochileros). 15 Pax. |
| **Familia Tanaka** | 🇯🇵 Japón | `tanaka@demo.com` | Requieren guía en japonés obligatoriamente. |

---

## 3. Productos: Servicios Base (Componentes)

*Ruta: Ventas > Productos > Productos*

### A. Hoteles (Servicio - Compra/Venta)

* **Nombre:** `Noche Hab. Doble - Hotel 3* (Cusco)`
* **Tipo:** Servicio
* **Política Facturación:** Cantidades pedidas
* **Costo:** $60.00
* **Precio Venta:** $80.00
* **Proveedor:** Hotel Casa Andina Standard
* **Rutas:** ☑️ Comprar, ☑️ Obtener bajo pedido (MTO)

### B. Transportes (Servicio - Compra/Venta)

* **Nombre:** `Traslado Aep - Hotel (Privado)`
* **Tipo:** Servicio
* **Costo:** $10.00
* **Precio Venta:** $20.00
* **Proveedor:** Transportes El Chasqui
* **Rutas:** ☑️ Comprar, ☑️ Obtener bajo pedido (MTO)

### C. Tickets/Entradas (Servicio)

* **Nombre:** `Ticket Tren Expedition (Ollanta - Mapi)`
* **Tipo:** Servicio
* **Costo:** $65.00
* **Precio Venta:** $75.00
* **Proveedor:** Inca Rail
* **Rutas:** ☑️ Comprar, ☑️ Obtener bajo pedido (MTO)

### D. Fee de Agencia (Servicio - Solo Venta)

* **Nombre:** `Gastos Administrativos / Fee`
* **Tipo:** Servicio
* **Costo:** $0.00
* **Precio Venta:** $30.00

---

## 4. Producto "Paquete" (Kit de Venta)

*Ruta: Ventas > Productos. Este es el que usarás en la cotización.*

**Nombre:** `Paquete: Cusco Mágico & Machupicchu 4D/3N`
**Tipo:** **Servicio** (Configurado como Kit)
**Precio de Venta:** $590.00
**Descripción Venta:** *Programa detallado de 4 días que incluye alojamiento premium, boletos de tren y guiado especializado.*

#### 📋 Datos para la Plantilla de Presupuesto (Itinerario)

| Elemento | Texto / Título | Descripción para la Demo |
| :--- | :--- | :--- |
| **Sección** | `Día 1: Cusco y alrededores` | "Bienvenida en el aeropuerto y traslado al hotel..." |
| **Sección** | `Día 2: Machu Picchu Full Day` | "Viaje en tren y visita a la ciudadela inca..." |
| **Nota** | `Importante: Clima` | "Traer ropa abrigadora y bloqueador solar." |
| **Sección** | `Día 3: Despedida y Traslado` | "Mañana libre y traslado al aeropuerto." |

**🛠️ Lista de Materiales (BoM) - Tipo Kit:**

* 3 x `Noche Hab. Doble - Hotel 3* (Cusco)`
* 2 x `Traslado Aep - Hotel (Privado)`
* 1 x `Ticket Tren Expedition (Ollanta - Mapi)`
* 1 x `Carlos Mamani (Guía)`
* 1 x `Gastos Administrativos / Fee`

---

## 5. CRM Pipeline (Tablero de Oportunidades)

*Ruta: CRM > Flujo de Ventas (Mi Pipeline)*

#### 🟢 Etapa: Nuevo (New)

* **Oportunidad:** "Consulta Paquete Luna de Miel - Diciembre"
* **Cliente:** (Nuevo, sin nombre aún)
* **Ingreso Esperado:** $1,200
* **Etiquetas:** `Web` `Urgente`
* **Probabilidad:** 10%

#### 🔵 Etapa: Calificado (Qualified)

* **Oportunidad:** "Grupo Estudiantes BsAs - Cusco Económico"
* **Cliente:** Grupo Estudiantes BsAs
* **Ingreso Esperado:** $4,500
* **Cierre previsto:** 28/02/2026
* **Notas:** *Están comparando precios con otra agencia. Llamar el viernes.*
* **Actividad:** 📞 *Llamar* (Vence en 2 días).

#### 🟡 Etapa: Propuesta (Proposition)

* **Oportunidad:** "Sarah Smith - Luxury Experience"
* **Cliente:** Sarah Smith
* **Ingreso Esperado:** $2,800
* **Estado:** Presupuesto S00045 enviado por correo.
* **Actividad:** ⚠️ *Hacer seguimiento por WhatsApp* (Vencido ayer - **Úsalo para mostrar alertas**).

#### 🏆 Etapa: Ganado (Won)

* **Oportunidad:** "Juan Pérez - Cusco Clásico"
* **Cliente:** Juan Pérez
* **Ingreso Real:** $1,180
* **Estado:** Facturado y Pagado.
* **Probabilidad:** 100%

---

## 💡 Tips de Configuración Visual

1. **Moneda:** Asegúrate de que la moneda principal sea **USD** o **PEN** (Soles) según lo que maneje la agencia, o activa la **Multimoneda** para mostrar que puedes cobrar en Dólares y pagar en Soles.
2. **Fotos:**
* Sube una foto de **Machu Picchu** al producto "Paquete".
* Sube una foto de una **Van turística** al producto "Traslado".


3. **PDF Detallado (Programa):**
*   Usa el archivo de ejemplo `Programa Camino inca...pdf` como referencia visual.
*   Explica que Odoo genera un PDF similar automáticamente usando las **Secciones** y **Notas** que configuramos.
*   *As bajo la manga:* Menciona que pueden subir este PDF oficial directamente a la oportunidad del CRM como adjunto.