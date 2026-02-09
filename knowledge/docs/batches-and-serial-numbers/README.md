---
title: Diferencia entre lotes y números de serie en Odoo 15
source: https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/differences.html
---

# Diferencia entre lotes y números de serie

Los **lotes** y **números de serie** son dos formas diferentes de identificar y rastrear los productos en Odoo. Aunque hay similitudes entre estos dos métodos de rastreo, también hay diferencias importantes que afectan:

- **Recepciones**
- **Entregas**
- **Reportes de inventario**

Un **lote** indica un grupo específico de artículos que se recibió, almacenó o envió desde un almacén, o un grupo de productos fabricados dentro de la empresa.

Un **número de serie** es un identificador único que se asigna a productos o artículos de forma incremental (o secuencial) para distinguirlos de otros productos y artículos.

> Referencias relacionadas:
> - [Usar lotes para gestionar grupos y productos](https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/lots.html)
> - [Usar números de serie para rastrear productos](https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/serial_numbers.html)

---

## Activar lotes y números de serie

Para poder rastrear productos mediante lotes y números de serie, primero hay que activar la funcionalidad en Odoo.

1. Ir a `Inventario ‣ Configuración ‣ Ajustes`.
2. Desplazarse hasta la sección **Trazabilidad**.
3. Marcar la casilla **Número de serie y lote**.
4. Hacer clic en **Guardar** para aplicar los cambios.

> Esta configuración permite que los productos puedan gestionarse con números de lote, números de serie o ambos, según las necesidades de trazabilidad de la empresa.

![Activar lotes y números de serie en los ajustes de Inventario](https://www.odoo.com/documentation/15.0/_images/differences-enabled-setting.png)

---

## Cuándo usar lotes

Los **lotes** son especialmente útiles para productos que se fabrican o reciben en **grandes cantidades**, como:

- Ropa
- Alimentos
- Cualquier producto con **fecha de caducidad** o características de producción comunes

Usar lotes ayuda a:

- Saber de qué **grupo** proviene un producto.
- Gestionar **retiros de productos** del mercado.
- Controlar y seguir **fechas de caducidad**.

![Lote creado con la cantidad de productos en él](https://www.odoo.com/documentation/15.0/_images/differences-lot.png)

Los fabricantes asignan un **número de lote** a grupos de productos que comparten propiedades en común. Por ello:

- Varios bienes pueden compartir el **mismo número de lote**.
- Es posible identificar rápidamente un conjunto de productos dentro de un grupo.
- Se puede seguir el ciclo de vida del grupo completo desde su ingreso hasta su salida del almacén.

---

## Cuándo usar números de serie

Los **números de serie** se asignan a **productos individuales**.

Su objetivo principal es permitir la **identificación del historial de cada artículo** conforme se mueve a lo largo de la cadena de suministro.

Esto es especialmente útil para:

- Fabricantes que ofrecen **servicio posventa**.
- Productos que requieren:
  - Historial de reparaciones.
  - Control de garantía.
  - Seguimiento individualizado después de la venta.

Los números de serie pueden estar compuestos por:

- Números.
- Letras.
- Símbolos tipográficos.
- O una combinación de los anteriores.

Cada número de serie debe ser **único** para cada unidad individual.

![Lista de números de serie para productos](https://www.odoo.com/documentation/15.0/_images/differences-serial-numbers.png)

---

## Trazabilidad

La **trazabilidad** permite a fabricantes y empresas visualizar el **ciclo de vida completo** de un producto o grupo de productos.

Los reportes de trazabilidad incluyen información como:

- **Origen** del producto (de dónde procede y cuándo llegó).
- **Ubicación de almacenamiento**.
- **Destino** (a quién se envió).

### Cómo ver la trazabilidad en Odoo

1. Ir a `Inventario ‣ Productos ‣ Números de serie/lote`.
2. En este tablero se listan automáticamente todos los productos a los que se les haya asignado un lote o número de serie.
3. Se puede expandir cada línea para ver:
   - Los lotes asociados.
   - Los números de serie asignados.

### Agrupar por lote o número de serie

Para agrupar la información:

1. Quitar todos los **filtros automáticos** de la barra de búsqueda (esquina superior derecha).
2. Hacer clic en **Agrupar por**.
3. Seleccionar **Agregar grupo personalizado**.
4. Elegir **Lote/Número de serie**.
5. Hacer clic en **Aplicar**.

Al hacerlo, se muestran todos los lotes y números de serie existentes, y se puede:

- Expandir cada grupo.
- Ver las cantidades de productos que comparten ese lote o número de serie.

Para los números de serie **únicos** que **no se reutilizan**, debería haber **solo un producto por número de serie**.

![Página de informes con listas desplegables de lotes y números de serie](https://www.odoo.com/documentation/15.0/_images/differences-tracking.png)

### Detalle y seguimiento de un lote o número de serie

Para más información sobre un lote o número de serie específico:

1. Hacer clic en la **línea de artículo** del lote o número de serie.
2. Se abrirá el formulario correspondiente a ese número de lote/serie.
3. Desde allí, se puede usar:
   - El botón inteligente **Ubicación** para ver todas las existencias a la mano asociadas a ese número.
   - El botón inteligente **Trazabilidad** para ver **todas las operaciones** realizadas con ese número de lote o serie.

---

## Referencia de imágenes

Todas las imágenes apuntan al sitio oficial de Odoo.  
Si quieres descargarlas para usarlas en local (por ejemplo en `knowledge/docs/batches-and-serial-numbers/imgs/`), puedes hacerlo con estos enlaces y guardarlas con los nombres sugeridos:

| Descripción                                                   | URL (Odoo)                                                                 | Nombre sugerido local                         |
|---------------------------------------------------------------|----------------------------------------------------------------------------|-----------------------------------------------|
| Ajuste: activar lotes y números de serie                      | `https://www.odoo.com/documentation/15.0/_images/differences-enabled-setting.png`      | `differences-enabled-setting.png`            |
| Ejemplo de lote con cantidad de productos                     | `https://www.odoo.com/documentation/15.0/_images/differences-lot.png`                  | `differences-lot.png`                         |
| Lista de números de serie para productos                      | `https://www.odoo.com/documentation/15.0/_images/differences-serial-numbers.png`       | `differences-serial-numbers.png`             |
| Reporte de trazabilidad con lotes y números de serie          | `https://www.odoo.com/documentation/15.0/_images/differences-tracking.png`             | `differences-tracking.png`                    |

Ejemplo de descarga (desde la carpeta del proyecto):

```bash
cd knowledge/docs/batches-and-serial-numbers
mkdir -p imgs
curl -o imgs/differences-enabled-setting.png "https://www.odoo.com/documentation/15.0/_images/differences-enabled-setting.png"
curl -o imgs/differences-lot.png "https://www.odoo.com/documentation/15.0/_images/differences-lot.png"
curl -o imgs/differences-serial-numbers.png "https://www.odoo.com/documentation/15.0/_images/differences-serial-numbers.png"
curl -o imgs/differences-tracking.png "https://www.odoo.com/documentation/15.0/_images/differences-tracking.png"
```

Si guardas las imágenes en `imgs/`, puedes reemplazar las URLs absolutas por rutas relativas, por ejemplo: `![Lotes](imgs/differences-lot.png)`.

Consulta siempre la página oficial por posibles actualizaciones:

- [Documentación Odoo 15 – Diferencia entre lotes y números de serie](https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/differences.html)

