# 📊 Manual de Tableros (Dashboards) - Wayki Trek

Este manual ha sido diseñado para explicar de manera sencilla y clara qué información muestra cada tablero (dashboard) del sistema, de dónde proviene esa información y para qué sirve. Está pensado para que cualquier persona del equipo pueda entender la salud del negocio de un vistazo.

---

## 1. Tablero de Ventas (Sales)
Este tablero es el centro principal para ver cuánto dinero está ingresando a la empresa a través de las ventas de paquetes y tours.

**¿De dónde se extrae la información?**
Toda la información proviene del módulo de **Ventas** de Odoo. Se alimenta automáticamente cada vez que un vendedor crea una "Cotización" (un presupuesto para un cliente) y cuando esta cotización es aceptada y se convierte en una "Orden de Venta" oficial.

**¿Qué muestra este tablero?**
* **Cuadros superiores (Métricas rápidas):** Te muestra rápidamente cuántas cotizaciones se han hecho en total, cuántas ventas se han confirmado, el dinero total que ha ingresado y el valor promedio que gasta cada cliente en una compra.
* **Ventas mensuales (Gráfico de líneas):** Te permite ver cómo han subido o bajado las ventas a lo largo de los meses. Es ideal para identificar las temporadas altas o bajas del año.
* **Mejores cotizaciones y Órdenes de venta principales (Tablas inferiores):** Es un ranking en tiempo real. Te dice exactamente qué clientes están comprando más (o están a punto de comprar) y qué vendedor de tu equipo está cerrando esos tratos.

![Tablero de Ventas](./screenshots/tablero_5_sales.png)

---

## 2. Tablero de Productos (Product)
Este tablero está enfocado enteramente en *qué* es lo que se está vendiendo, en lugar de *cuánto* dinero general ingresa. 

**¿De dónde se extrae la información?**
Se extrae de la combinación del módulo de **Ventas** y el catálogo de **Productos**. Odoo analiza cada línea de las facturas y comprobantes para saber qué tour, paquete o servicio específico compró cada persona.

**¿Qué muestra este tablero?**
* **Más vendido y Mejor categoría (Cuadros superiores):** Te dice de un vistazo cuál es el tour estrella (por ejemplo, "Peru 15 Days") y qué tipo de servicio es el favorito de los clientes de forma general (ej. la categoría "Packages").
* **Mejores vendedores por ingresos (Gráfico de barras superior):** Muestra visualmente qué producto específico le está dejando la mayor cantidad de dinero a la empresa.
* **Mejores vendedores por unidades vendidas (Gráfico de barras inferior):** Muestra qué producto se vende más cantidad de veces (independientemente de si es un tour barato o caro). Esto es útil para saber qué tours atraen a mayor volumen de personas.

![Tablero de Productos](./screenshots/tablero_6_product.png)

---

## 3. Tablero de Leads (Prospectos)
Un "Lead" o prospecto es una persona que ha mostrado interés (por ejemplo, llenó un formulario en la página web o mandó un correo preguntando), pero que todavía no ha comprado nada. Este tablero mide cómo atraemos a esos posibles clientes.

**¿De dónde se extrae la información?**
Proviene del módulo de **CRM** (Gestión de Relaciones con el Cliente). Se alimenta automáticamente cuando entran nuevos contactos al sistema, mucho antes de que se les envíe un precio o cotización.

**¿Qué muestra este tablero?**
* **Métricas rápidas:** Muestra qué porcentaje de estos interesados se convierten en clientes reales ("Índice de acuerdos"), y cuántos días en promedio tarda el equipo en contactarlos y ganar la venta.
* **Leads por mes (Gráfico):** Te ayuda a ver en qué meses llegan más personas interesadas haciendo preguntas.
* **Top Countries (Mapa Mundial):** ¡Muy visual y estratégico! Pinta en el mapa del mundo de qué países provienen las personas que nos contactan. Es vital para saber en qué países invertir dinero para publicidad.

![Tablero de Leads](./screenshots/tablero_1_leads.png)

---

## 4. Tablero de Flujo (Pipeline)
El "Pipeline" o embudo de ventas es el proceso paso a paso por el que pasa un cliente potencial: desde que es un contacto nuevo, pasando por la negociación, hasta que finalmente reserva y paga el tour.

**¿De dónde se extrae la información?**
Al igual que los Leads, se extrae del **CRM**, pero aquí se enfoca exclusivamente en las "Oportunidades" (personas que ya están en un proceso de negociación serio con nuestros vendedores).

**¿Qué muestra este tablero?**
* **Métricas rápidas:** 
  * **Esperado:** Es una proyección a futuro del dinero que *podría* ingresar si los vendedores logran cerrar todas las negociaciones que tienen en curso.
  * **Cerrado:** El dinero que ya se ganó definitivamente.
  * **Oportunidades abiertas:** Cuántas negociaciones activas están manejando los vendedores en este preciso momento.
* **Top Opportunities (Gráfico superior):** Muestra cuáles son las negociaciones más grandes (las que traerían más dinero) y qué probabilidad de éxito tienen.
* **Pipeline / Embudo (Gráfico inferior):** Muestra visualmente dónde se están estancando los clientes. Sirve para detectar problemas (por ejemplo, si a mucha gente se le envía la cotización pero nadie responde para comprar).

![Tablero de Flujo](./screenshots/tablero_2_pipeline.png)

---

## 5. Tablero de Marketing por Correo (Email Marketing)
Mide el éxito de las campañas de publicidad o boletines informativos que se envían por correo electrónico masivo a los clientes.

**¿De dónde se extrae la información?**
Directamente del módulo de **Marketing por Correo**. El sistema rastrea de forma invisible qué correos llegan a su destino, cuáles rebotan y si el cliente hizo clic en algún enlace dentro del correo.

**¿Qué muestra este tablero?**
* **Métricas rápidas:** 
  * **Enviados / Abiertos:** Cuántos correos mandamos en total y cuántas personas realmente lo abrieron.
  * **Tasa de abiertos / Tasa de clics:** Te dice en porcentaje qué tan atractivo fue el título de tu correo (si el número es alto, mucha gente lo abrió) y qué tan buena fue la oferta interior (si hicieron clic en los enlaces para leer más).
  * **Canceló su suscripción:** Personas que se aburrieron y pidieron no recibir más correos de la empresa.
* **Correos enviados por mes (Gráfico de barras apiladas):** Permite comparar mes a mes el volumen de correos enviados, desglosando en colores cuántos fueron un éxito (entregados y abiertos) y cuántos fallaron (cancelados o rebotados).

![Tablero de Marketing por Correo](./screenshots/tablero_3_email_marketing.png)
