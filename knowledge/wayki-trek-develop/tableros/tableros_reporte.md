# 📊 Manual de Tableros (Dashboards) - Wayki Trek

Este manual ha sido diseñado para explicar de manera sencilla y clara qué información muestra cada tablero (dashboard) del sistema, de dónde proviene esa información y para qué sirve. Está pensado para que cualquier persona del equipo pueda entender la salud del negocio de un vistazo.

---

## 1. Tablero de Ventas (Sales)
Este tablero es el centro principal para evaluar el desempeño comercial de la empresa. La información se actualiza dinámicamente y puede ser filtrada por distintos periodos de tiempo (por defecto "Últimos 90 días").

**¿De dónde se extrae la información general?**
Toda la data de esta pantalla proviene del módulo de **Ventas** de Odoo. Se alimenta automáticamente de los presupuestos (Cotizaciones) y de las ventas confirmadas (Órdenes de Venta) gestionadas por el equipo comercial.

### Análisis de las métricas y gráficos disponibles:

* **Tarjetas de Indicadores Principales (KPIs superiores):**
  * **Cotizaciones:** Total de presupuestos generados y enviados a los clientes que aún no se han cerrado.
  * **Confirmados:** Número total de ventas que ya han sido aceptadas y oficializadas.
  * **Ingreso:** Monto total de dinero generado por las ventas confirmadas en el periodo seleccionado.
  * **Orden promedio:** El valor monetario promedio de cada venta (Ingresos divididos entre las Órdenes confirmadas). Ayuda a entender el nivel de gasto habitual de los clientes.

* **Gráfico "Ventas mensuales" (Monthly Sales):**
  * Muestra la evolución de los ingresos a lo largo del tiempo. Es fundamental para identificar patrones estacionales (meses de alta o baja demanda en turismo).

### Tablas de Ranking y Desempeño:
Estas secciones organizan la información de mayor a menor para identificar rápidamente las mejores oportunidades comerciales.

* **Top Quotations (Mejores cotizaciones) y Top Sales Orders (Órdenes de venta principales):**
  * Muestran las negociaciones de mayor valor económico. Detallan el Cliente, el Vendedor a cargo y el monto potencial o cerrado (Revenue). 
  * *Fuente:* Cotizaciones pendientes y Órdenes de venta confirmadas, respectivamente.

* **Top Products (Productos más vendidos) y Categorías:**
  * Identifican qué tours específicos y qué familias de productos (ej. "Packages", "Inca Trail") están generando más ingresos y mayor volumen de pedidos.
  * *Fuente:* Las líneas de detalle (los tours específicos agregados) dentro de cada Orden de Venta.

* **Top Countries (Mejores países) y Top Customers (Mejores clientes):**
  * Permiten visualizar geográficamente de dónde provienen los compradores y revelar quiénes son los clientes individuales que más invierten.
  * *Fuente:* La información de perfil y dirección del contacto asociado a la Orden de Venta.

* **Top Sales Teams (Equipos) y Top Salespeople (Vendedores):**
  * Evalúa el rendimiento del personal interno, mostrando qué equipo y qué asesor de ventas está cerrando más tratos y atrayendo mayor cantidad de dinero.
  * *Fuente:* El campo "Vendedor" y "Equipo de Ventas" asignado a cada venta.

* **Top Sources (Orígenes) y Top Mediums (Medios de adquisición):**
  * Analizan por qué canal publicitario o vía de contacto llegó la venta (ej. referidos, sitio web, redes sociales). Es vital para evaluar la efectividad del área de marketing.
  * *Fuente:* Las etiquetas de rastreo (UTM) registradas en Odoo al momento en que el prospecto inició el contacto.

![Tablero de Ventas](./screenshots/tablero_5_sales.png)

---

## 2. Tablero de Productos (Product)
Este tablero está enfocado enteramente en analizar *qué* es lo que se está vendiendo (qué tours, servicios o paquetes generan más interés y rentabilidad), dejando en un segundo plano las métricas generales de dinero de la empresa.

**¿De dónde se extrae la información general?**
Se nutre de la combinación del catálogo de **Productos** y el módulo de **Ventas**. El sistema desglosa y analiza cada línea de detalle dentro de las facturas y órdenes de venta confirmadas para saber exactamente qué servicio específico se compró.

### Análisis de las métricas y gráficos disponibles:

* **Tarjetas de Indicadores Principales (KPIs superiores):**
  * **Más vendido:** Muestra el producto o tour exacto que ha tenido más éxito en volumen durante el periodo evaluado.
  * **Mejor categoría:** Identifica cuál familia de servicios (ej. "Packages", "Inca Trail") es la favorita absoluta de los clientes en general.

* **Gráficos de Barras de Desempeño:**
  * **Best Sellers by Revenue (Mejores productos por ingresos):** Muestra de forma visual qué productos específicos están dejando la mayor cantidad neta de dinero a la empresa. Sirve para entender qué servicios son los más rentables.
  * **Best Sellers by Units Sold (Mejores productos por volumen):** Muestra qué productos tienen la mayor rotación o salida (independientemente de si son baratos o caros). Es vital para saber qué tours atraen a la mayor masa de turistas.

### Tablas de Ranking y Detalle:
* **Best Selling Products (Productos más vendidos):**
  * Una tabla exhaustiva que clasifica todo el catálogo ofertado. Por cada tour o servicio, detalla exactamente cuántas unidades/pasajes se vendieron (Units) y cuánto dinero exacto generaron (Revenue).
  * *Fuente:* El recuento total de los artículos facturados en las ventas ganadas.
* **Category (Rendimiento por Categoría):**
  * En lugar de analizar producto por producto, esta tabla agrupa las ventas por familias enteras. Permite a la gerencia decidir qué macro-categorías de viaje vale la pena potenciar en futuras campañas.
  * *Fuente:* El campo "Categoría de Producto" configurado en el inventario de Odoo.

![Tablero de Productos](./screenshots/tablero_6_product.png)

---

## 3. Tablero de Leads (Prospectos)
Un "Lead" o prospecto es una persona o contacto que ha mostrado interés en nuestros servicios (por ejemplo, llenando un formulario en la página web o mandando un correo), pero que todavía no ha recibido una cotización formal. Este tablero evalúa cómo atraemos y gestionamos a esos posibles clientes.

**¿De dónde se extrae la información general?**
Toda la información fluye desde el módulo de **CRM** (Gestión de Relaciones con el Cliente). Se alimenta automáticamente cada vez que ingresa una nueva consulta al sistema y se registra como una oportunidad de venta inicial.

### Análisis de las métricas y gráficos disponibles:

* **Tarjetas de Indicadores Principales (KPIs superiores):**
  * **Índice de acuerdos (Win Rate):** Muestra qué porcentaje histórico de prospectos termina convirtiéndose en clientes reales. Es la medida clave del éxito de las ventas.
  * **Tamaño promedio de trato:** Cuánto dinero se espera ganar, en promedio, por cada prospecto nuevo que ingresa al sistema.
  * **Ingreso:** El dinero total real que ha ingresado a partir de los prospectos generados en este periodo.
  * **Días para ganar / Días hasta asignar:** Miden la agilidad del equipo. Cuánto tiempo pasa desde que un prospecto nos contacta hasta que un vendedor lo atiende, y cuántos días pasan hasta que finalmente paga.

* **Gráfico "Leads por mes" (Leads by Month):**
  * Visualiza el volumen de consultas que llegan mes a mes. Es fundamental para saber en qué épocas del año la empresa recibe más correos y solicitudes de información.

### Tablas de Ranking y Segmentación:
* **Top Countries (Mapa y Países principales):**
  * Un mapa mundial y una tabla que muestran visualmente de qué países provienen las personas que nos contactan. Es información vital para la gerencia al decidir en qué territorios invertir dinero para publicidad (ej. pautas en Google o Facebook).
  * *Fuente:* El país registrado por el cliente en el formulario web o en su perfil de contacto.

* **Top Tags (Etiquetas principales) y Top Lost Reasons (Motivos de pérdida):**
  * Identifican qué tipo de intereses tienen los prospectos (usando etiquetas como "Aventura", "VIP") y, lo más crítico, **por qué se pierden las ventas** (ej. "Precio alto", "Falta de cupos"). 
  * *Fuente:* Las etiquetas agregadas por los vendedores y el "Motivo de pérdida" que seleccionan al descartar una oportunidad en el CRM.

* **Top Campaigns, Sources y Mediums (Campañas, Orígenes y Medios):**
  * Estas tres tablas analizan exactamente qué campaña publicitaria, buscador o red social está atrayendo a la mayor cantidad de prospectos, y cuáles traen a los prospectos más rentables.
  * *Fuente:* Los enlaces de rastreo de marketing (UTM) que Odoo captura de forma invisible cuando el cliente hace clic en un anuncio antes de llenar el formulario web.

* **Top Sales Teams y Top Salespeople (Equipos y Vendedores):**
  * Mide qué miembro del equipo y qué grupo de ventas están recibiendo y procesando la mayor cantidad de consultas nuevas, y cuántos ingresos logran materializar a partir de ellas.
  * *Fuente:* El vendedor asignado de forma automática o manual al Lead dentro del CRM.

![Tablero de Leads](./screenshots/tablero_1_leads.png)

---

## 4. Tablero de Flujo (Pipeline)
El "Pipeline" o embudo de ventas representa el proceso paso a paso por el que pasa un cliente potencial: desde el inicio de la negociación hasta que finalmente reserva y paga el tour. A diferencia del tablero de Leads, aquí nos enfocamos en el valor monetario que está "sobre la mesa" y a punto de ganarse.

**¿De dónde se extrae la información general?**
Al igual que los Leads, se extrae del módulo de **CRM**, pero aquí la información se filtra y se enfoca exclusivamente en las "Oportunidades" (personas que ya pasaron el primer filtro y están en un proceso de negociación serio con los vendedores).

### Análisis de las métricas y gráficos disponibles:

* **Tarjetas de Indicadores Principales (KPIs superiores):**
  * **Esperado:** Es una proyección financiera. Suma el dinero total que ingresaría a la empresa si los vendedores logran cerrar con éxito todas las negociaciones activas.
  * **Cerrado:** El dinero real que ya se ganó definitivamente y se cerró en el periodo evaluado.
  * **Oportunidades abiertas:** El número exacto de negociaciones en curso que los vendedores están atendiendo activamente hoy.

* **Gráficos de Progreso y Tiempo:**
  * **Pipeline (Embudo por Etapa):** Muestra visualmente dónde se encuentran agrupados los clientes. Sirve para detectar "cuellos de botella" (por ejemplo, si el sistema alerta que hay 50 personas estancadas en la etapa "Cotización enviada" que no han avanzado).
  * **Cierre esperado (Expected Closing):** Un gráfico que proyecta en qué fechas futuras ingresará el dinero a la empresa, basándose en la "Fecha límite" estimada que el vendedor le asigna a cada negociación en el CRM.

### Tablas de Ranking y Análisis Estratégico:
* **Top Opportunities (Mejores oportunidades):**
  * Es posiblemente la tabla más crítica para la gerencia. Enlista las negociaciones individuales de mayor valor económico. Detalla la Oportunidad, la Etapa actual, el Vendedor responsable, el País, el monto de dinero potencial (Revenue) y el Porcentaje de Éxito (Success %) estimado.
  * *Fuente:* El listado directo de Oportunidades activas en el tablero Kanban del CRM.

* **Desglose Geográfico (Country y Top Cities):**
  * Tablas que agrupan el valor de las negociaciones activas según el país o la ciudad específica del prospecto. Útil para lanzar ofertas dirigidas a ciudades específicas.
  * *Fuente:* La ciudad y país registrados en la ficha de contacto del CRM.

* **Orígenes y Medios (Top Sources y Top Mediums):**
  * Indican por qué vía (ej. buscador de Google) y medio (ej. campaña de Facebook Ads) llegaron los clientes con los que se está negociando el dinero actualmente.
  * *Fuente:* Las etiquetas de rastreo (UTM) que acompañan al prospecto desde su primer clic en internet.

* **Desempeño Interno (Top Salespeople y Top Sales Teams):**
  * A diferencia del tablero de Ventas (que mide victorias finales), estas tablas evalúan el potencial en curso. Muestran qué vendedor y qué equipo tienen la mayor carga de negociaciones abiertas y la mayor suma de dinero proyectado. Ayuda a redistribuir el trabajo si alguien está sobrecargado.
  * *Fuente:* El responsable asignado en la ficha de la Oportunidad dentro del CRM.

![Tablero de Flujo](./screenshots/tablero_2_pipeline.png)

---

## 5. Tablero de Marketing por Correo (Email Marketing)
Este tablero mide exclusivamente el impacto y éxito de las campañas masivas, boletines informativos (newsletters) o automatizaciones enviadas por correo electrónico a la base de datos de la empresa.

**¿De dónde se extrae la información general?**
Directamente del módulo de **Marketing por Correo (Email Marketing)**. Odoo inserta de forma automática rastreadores invisibles (píxeles) y enlaces trackeables en cada correo saliente, lo que le permite saber exactamente qué hace el cliente después de recibir el mensaje.

### Análisis de las métricas y gráficos disponibles:

* **Tarjetas de Indicadores Principales (KPIs superiores):**
  * **Enviados / Abiertos:** Volumen total de correos que salieron del servidor y cuántos de ellos fueron realmente abiertos por el destinatario.
  * **Tasa de entrega / Tasa de devolución (Bounced):** Indica la salud de la base de datos. Una alta tasa de devolución significa que muchos correos de tus contactos están mal escritos o ya no existen.
  * **Tasa de abiertos / Tasa de clics (CTR):** Miden el nivel de interés. Una alta tasa de abiertos indica que el "Asunto" del correo fue muy atractivo. Una alta tasa de clics indica que el contenido interno (ofertas, botones) fue convincente.
  * **Canceló su suscripción:** El porcentaje de personas que se aburrieron y decidieron darse de baja de la lista.

* **Gráficos de Tendencia (Mails sent per month / Over previous period):**
  * Gráficos de barras apiladas que comparan el volumen de correos enviados mes a mes (o frente al mes pasado). Clasifican visualmente qué porción de esos envíos fue Entregada, Respondida, Abierta o Cancelada.

### Tablas de Ranking y Monitoreo de Campañas:
* **Top 10 recent mailing campaigns (Top 10 campañas recientes):**
  * Una radiografía exacta de los últimos correos masivos enviados. Muestra el Asunto, la fecha exacta y un desglose estadístico profundo (en porcentajes y números totales) de cuántos lo recibieron, lo abrieron, lo respondieron o hicieron clic adentro. 
  * *Fuente:* El registro estadístico de la aplicación de Email Marketing.

* **Mailing campaigns in preparation (Campañas en preparación):**
  * Funciona como una sala de espera operativa. Muestra los correos que están redactados en estado "Borrador" (ej. "Promociones para Mayo", "Recordatorio de cumpleaños"), quién es el vendedor responsable de enviarlos y a qué modelo de contactos (ej. lista de correo, lead o cliente) van dirigidos. 

* **Top 10 best link trackers (Top 10 enlaces más clickeados):**
  * Evalúa qué botones o enlaces específicos dentro de tus correos llamaron más la atención. Detalla el título del enlace, hacia qué URL objetivo o WhatsApp dirigía (ej. "https://wa.me/...") y el número total de clics que recibió.
  * *Fuente:* El motor de rastreo de enlaces (Link Tracker) que Odoo incrusta al construir las plantillas de correo.

![Tablero de Marketing por Correo](./screenshots/tablero_3_email_marketing.png)
