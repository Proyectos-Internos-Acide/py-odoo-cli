# Guía de Filtros Dinámicos para Email Marketing en Odoo
**Wayki Trek**

Este manual explica detalladamente cómo filtrar destinatarios en la aplicación de **Email Marketing** (Marketing por correo) en Odoo de forma 100% dinámica para diferentes escenarios comerciales comunes.

---

## 📌 Concepto Clave: Filtrado Directo vs. Listas Estáticas

En Odoo, **no es necesario crear listas de correo manuales** para cada campaña. Es mucho más eficiente utilizar **Filtros Dinámicos** en los destinatarios. Al hacerlo:
1. El sistema busca las bases de datos en tiempo real justo antes de realizar el envío.
2. Evitas que contactos nuevos que cumplen con los requisitos se queden fuera del envío.
3. Se previene enviar correos a personas que ya no cumplen las condiciones (ej. oportunidades ganadas).

---

## 🛠️ Paso Inicial: Dónde configurar el filtro

1. Ve a la aplicación **Marketing por correo** (Email Marketing).
2. Haz clic en **Nuevo** (Crear) para iniciar una campaña.
3. Ubica el campo **Destinatarios** (Recipients). Aquí es donde definiremos el origen y las reglas de filtrado.

---

## 📂 Casos Prácticos de Filtrado

### Caso 1: Destinatarios creados en fechas específicas
*Útil para enviar correos de bienvenida a registros recientes o promociones a leads de un mes específico.*

1. En **Destinatarios**, selecciona **Iniciativa/Oportunidad** (Lead/Opportunity) o **Contacto** (Partner).
2. Agrega las siguientes reglas:
   - **Regla 1**: `Fecha de creación` ➔ `es mayor o igual que` ➔ *[Selecciona el inicio de fecha]*
   - **Regla 2** (Haciendo clic en "+"): `Fecha de creación` ➔ `es menor o igual que` ➔ *[Selecciona el fin de fecha]*

> [!TIP]
> Si deseas filtrar de forma relativa (por ejemplo, "siempre los del mes actual"), selecciona el operador `está establecido` u Odoo te presentará un selector dinámico que dice **"Este mes"** o **"Este año"** según tu versión.

---

### Caso 2: Destinatarios en una etapa específica del CRM
*Ideal para enviar material de seguimiento a leads en etapa "Calificado" o correos de postventa a oportunidades "Ganadas".*

1. En **Destinatarios**, selecciona **Iniciativa/Oportunidad** (Lead/Opportunity).
2. Configura las siguientes reglas:
   - **Regla 1**: `Tipo` ➔ `=` ➔ `Oportunidad`
   - **Regla 2**: `Etapa` (Stage) ➔ `=` ➔ *[Selecciona la etapa, por ejemplo: **Seguimiento**]*

*Ejemplo visual del filtro:*
`[ Tipo = Oportunidad ] AND [ Etapa = Seguimiento ]`

---

### Caso 3: Destinatarios que compraron un Tour específico
*Ideal para enviar itinerarios, recomendaciones de viaje o encuestas de satisfacción específicas a quienes compraron un tour determinado.*

Para este caso, debemos buscar a través de las ventas facturadas/confirmadas.

1. En **Destinatarios**, selecciona **Orden de venta** (Sales Order).
2. Configura las siguientes reglas para filtrar compras reales:
   - **Regla 1 (Estado de la venta)**: `Estado` ➔ `=` ➔ `Pedido de venta` (Sales Order). *Esto excluye presupuestos borradores.*
   - **Regla 2 (Filtro de producto)**: `Líneas del pedido / Producto` ➔ `=` ➔ *[Busca y selecciona el tour, por ejemplo: **Camino Inca 2 Días**]*

#### 💡 Variante avanzada: Filtrar desde la ficha de Contactos
Si prefieres que los destinatarios sigan siendo del modelo **Contacto** (para no enviar un correo por cada orden si un cliente compró varias veces):
1. En **Destinatarios**, selecciona **Contacto** (Partner).
2. Agrega la regla:
   - `Pedidos de venta / Líneas de pedido / Producto` ➔ `=` ➔ *[Selecciona el producto del Tour]*
   - `Pedidos de venta / Estado` ➔ `=` ➔ `Pedido de venta`

---

## ⚙️ Reglas de Oro para combinar filtros

Cuando agregas múltiples líneas de filtros, Odoo te da la opción de elegir cómo se relacionan entre sí:

* **"Todas las condiciones" (AND / Y)**:
  * El destinatario debe cumplir **absolutamente todas** las reglas.
  * *Ejemplo*: Oportunidades creadas este mes **Y** que estén en etapa "Calificado".
* **"Cualquiera de las condiciones" (OR / O)**:
  * El destinatario se incluirá si cumple **al menos una** de las reglas.
  * *Ejemplo*: Clientes que compraron "Camino Inca 2 días" **O** "Camino Inca 4 días".

---

## 🔍 Cómo verificar antes de enviar

Nunca envíes a ciegas. Odoo te proporciona herramientas de seguridad antes del envío:

1. **El contador verde**: Al definir el filtro, verás un contador como: `15 registros seleccionados`.
2. **Ver lista**: Haz clic en el enlace verde del contador. Se abrirá una ventana emergente con el listado exacto de nombres y correos seleccionados. Revísala para validar que el filtro funciona como esperas.
3. **Enviar prueba**: Antes de enviar a toda la lista, usa el botón **Enviar prueba** en la parte superior izquierda de la campaña y digita tu correo personal para verificar el diseño final.
