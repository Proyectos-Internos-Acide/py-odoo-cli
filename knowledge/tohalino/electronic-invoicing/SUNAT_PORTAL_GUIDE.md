# Guía de Consulta: Facturas en Portal SUNAT

Esta guía explica cómo verificar que las facturas enviadas desde Odoo han sido recibidas y aceptadas correctamente por la SUNAT.

## Consideraciones Iniciales
Odoo utiliza el sistema **SEE - Del Contribuyente**. Por lo tanto, los comprobantes **no** aparecerán en la sección de "Factura Electrónica SOL", sino en la sección específica de sistemas propios.

---

## Pasos para la Consulta

1.  **Ingreso al Portal**:
    *   Entra a [SUNAT Operaciones en Línea](https://www.sunat.gob.pe/).
    *   Selecciona **Mis Trámites y Consultas**.
    *   Inicia sesión con tu RUC, Usuario SOL y Clave.

2.  **Ubicación del Menú**:
    *   Haz clic en la pestaña superior **EMPRESAS**.
    *   Sigue esta ruta en el menú lateral:
        `Comprobantes de Pago` 
        ➔ `SEE - Del Contribuyente y Envío de Documentos`
        ➔ `Consultar Envíos de CPE`
        ➔ **Consultar Envío de Comprobante de Pago Electrónicos**

3.  **Filtros de Búsqueda**:
    *   **Fecha de Inicio / Fin**: Selecciona el rango de fechas de emisión.
    *   **Tipo de Comprobante**: Selecciona `01 - FACTURA`.
    *   Haz clic en el botón **Buscar**.

4.  **Verificación de Estado**:
    *   Aparecerá una lista con los documentos enviados.
    *   Busca la serie (ej. `FFFI`) y el número de tu factura.
    *   Lo más importante es validar la columna **Estado del Comprobante**, que debe decir **ACEPTADO**.

---

## Preguntas Frecuentes

### ¿Por qué mi factura no aparece en "Consultar Factura SOL"?
Porque esa sección solo muestra facturas creadas directamente en la web de SUNAT. Las facturas de Odoo se consideran "externas" y solo se ven en la ruta de "Sistemas del Contribuyente".

### ¿Qué es el CDR?
Es la "Constancia de Recepción". En Odoo, lo encuentras dentro del archivo **.ZIP** en la pestaña **Documentos EDI**. Es tu comprobante legal de que SUNAT procesó el archivo.
