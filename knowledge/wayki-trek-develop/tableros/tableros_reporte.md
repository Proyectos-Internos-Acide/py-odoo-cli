# 📊 Manual de Tableros (Dashboards) - Wayki Trek

Este manual ha sido diseñado para explicar de manera sencilla y clara qué información muestra cada tablero (dashboard) del sistema, de dónde proviene esa información y para qué sirve. Está pensado para que cualquier persona del equipo pueda entender la salud del negocio de un vistazo.

---

## 1. Tablero de Ventas (Sales)
Este tablero es el centro principal para evaluar el desempeño comercial de la empresa. Toda la información que se observa aquí está filtrada por un periodo de tiempo (por defecto muestra los **"Últimos 90 días"**, como se ve en la esquina superior derecha).

**¿De dónde se extrae la información general?**
Absolutamente todos los datos de esta pantalla provienen del módulo de **Ventas** de Odoo. El sistema lee las Cotizaciones (presupuestos) y las Órdenes de Venta (ventas confirmadas) que el equipo comercial registra en el día a día.

### Análisis detallado de lo que se ve en pantalla:

#### A. Tarjetas de Indicadores Principales (KPIs superiores)
Son los 4 bloques ubicados en la parte superior. Nos dan la "fotografía" rápida del negocio. En la imagen vemos que todos tienen un texto verde (↑∞% desde el último periodo), lo que indica que hay un crecimiento positivo en comparación con los 90 días anteriores.
1. **Cotizaciones (5):** 
   - *Qué significa:* Se han creado y enviado 5 presupuestos a clientes potenciales. 
   - *De dónde sale:* Cuenta cuántos documentos en el módulo de Ventas están en estado "Presupuesto" o "Cotización enviada".
2. **Confirmados (5):** 
   - *Qué significa:* De todas las cotizaciones, 5 ya han sido aceptadas por el cliente.
   - *De dónde sale:* Cuenta cuántos documentos pasaron al estado "Orden de Venta" (venta cerrada).
3. **Ingreso ($14.859):** 
   - *Qué significa:* Es el dinero total que la empresa ha generado o va a recibir por esas 5 ventas confirmadas.
   - *De dónde sale:* Es la suma del total de dinero de las Órdenes de Venta.
4. **Orden promedio ($2.972):** 
   - *Qué significa:* En promedio, cada vez que un cliente nos compra, gasta cerca de 3 mil dólares.
   - *De dónde sale:* Se calcula dividiendo el "Ingreso" ($14.859) entre el número de ventas "Confirmadas" (5). Es un indicador clave para saber si estamos vendiendo tours caros o baratos.

#### B. Gráfico Central: "Ventas mensuales"
- *Qué muestra:* Es un gráfico de líneas (aunque en la imagen solo haya un punto azul por ahora). En el eje inferior (horizontal) vemos el mes **"Julio 2026"**, y en el eje lateral (vertical) vemos el **"Revenue"** (Ingresos) que va desde 0 hasta 16.000.
- *De dónde sale:* Toma el total de ventas (Ingreso) y lo divide por meses. El punto azul está casi llegando a la línea de 15.000, lo que coincide exactamente con nuestro Ingreso total de $14.859. Con el paso de los meses, este punto formará una línea para ver si las ventas suben o bajan.

#### C. Tablas Inferiores (Rankings)
En la parte de abajo vemos dos listas detalladas que nos ayudan a entender exactamente quién está comprando y quién está vendiendo. Ambas tablas muestran el correo o nombre del Cliente, el Vendedor responsable y el Ingreso generado.

1. **Mejores cotizaciones (Izquierda):**
   - *Qué muestra:* Las 5 cotizaciones (presupuestos) con los montos de dinero más altos que están actualmente en proceso. Vemos correos como "waykitrek.transportes@gmail.com" con montos desde $289 hasta $3,582. 
   - *De dónde sale:* El sistema revisa los documentos en estado "Presupuesto", los ordena del más caro al más barato y muestra el Top 5. El vendedor estrella aquí es "Amaru Cusi", quien está manejando todas estas grandes cotizaciones.
2. **Órdenes de venta principales (Derecha):**
   - *Qué muestra:* Las 5 ventas **ya cerradas** más grandes de la empresa. Aquí vemos una venta gigantesca de $11,360 al cliente "contactorogerls@gmail.com", liderada por el vendedor Amaru Cusi. También vemos ventas de "Carlos Fernandez" y "Américo Aguilar" manejadas por Leo Cusi.
   - *De dónde sale:* El sistema revisa los documentos en estado "Orden de Venta", los ordena de mayor a menor y extrae a los mejores 5 clientes.

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
