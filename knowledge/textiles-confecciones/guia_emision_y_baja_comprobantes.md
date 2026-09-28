# Guía Operativa: Emisión y Anulación de Facturas y Boletas en Odoo (SUNAT)
> **Versión**: Odoo SaaS 19.4 Enterprise — Localización Perú (`l10n_pe`)
> **Referencia oficial**: [Odoo 19.0 Docs — Peru Localization](https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations/peru.html)

Esta guía explica el ciclo de vida comercial, contable y tributario para **emitir** y **anular / dar de baja** comprobantes electrónicos (Facturas y Boletas) en **Textiles y Confecciones Atlas**, detallando todo lo que desencadena Odoo en cada fase.

---

## 1. Emisión de Facturas y Boletas Electrónicas

### A. Paso a Paso en la Interfaz de Odoo
1. Ingresa a **Facturación** (o **Contabilidad**) > **Clientes** > **Facturas**.
2. Haz clic en el botón **Nuevo**.
3. Completa los datos obligatorios del formulario EDI:
   * **Cliente**:
     * Para Factura: Selecciona o crea el cliente con su **RUC (11 dígitos)** y condición *Activo/Habido*. El **Tipo de Identificación** debe ser `RUC`.
     * Para Boleta: Selecciona o crea el cliente con su **DNI (8 dígitos)** (Tipo de Identificación `DNI`), o consumidor final.
   * **Tipo de Documento** *(campo requerido por l10n_pe)*:
     * El valor predeterminado es **`Factura Electrónica`** — cámbialo manualmente a **`Boleta de Venta`** si corresponde.
   * **Tipo de Operación** *(campo EDI requerido)*:
     * El valor predeterminado es **`Venta Interna`**. Selecciona otro si necesitas, ej. `Exportación de Bienes`.
   * **Fecha de Factura**: Fecha de emisión de la operación.
   * **Líneas de Factura (Productos/Servicios)**:
     * Agrega el producto (ej. `Polo 100% Algodón`).
     * Define la cantidad y el precio unitario.
     * Cada línea tiene el campo **"Razón de Afectación EDI"** que determina el alcance del impuesto según la lista SUNAT (se preselecciona automáticamente). Verifica que el impuesto sea **`IGV 18%`** (afectación `10 - Gravado - Operación Onerosa`).
4. **Número / Correlativo**:
   * Odoo asignará automáticamente el correlativo al confirmar (ej. `F101-00000006` o `B101-00000006`).
5. **Confirmar**:
   * Haz clic en **Confirmar**. Esto registra el movimiento contable y activa el flujo EDI.
6. **Envío a SUNAT (EDI asincrónico)**:
   * Tras confirmar, en la cabecera de la factura aparecerá el estado EDI **"Por Enviar"** (*To be Sent*).
   * El documento se envía **automáticamente mediante un cron que corre cada hora**, o puedes forzarlo inmediatamente con el botón **"Enviar ahora"** (*Send now*).

> [!NOTE]
> En Odoo SaaS 19.4 el envío es **asincrónico**: no hay un botón obligatorio "Enviar e Imprimir" como flujo principal. El cron despacha la cola EDI. El botón **"Enviar ahora"** permite enviarlo de forma inmediata cuando necesitas validación urgente.

---

### B. ¿Qué desencadena Odoo al Emitir un Comprobante?

Al confirmar y enviar el comprobante, Odoo ejecuta simultáneamente tres procesos:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CONFIRMAR Y ENVIAR                              │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│ 1. SUNAT (EDI)   │      │ 2. Contabilidad  │      │ 3. Inventario    │
├──────────────────┤      ├──────────────────┤      ├──────────────────┤
│• Genera XML UBL  │      │• Asiento Diario  │      │• Salida física   │
│  2.1 (Peru)      │      │  (Cta 12 vs      │      │  de almacén      │
│• Firma con CDT   │      │   Cta 70 y 40)   │      │• Descuento de    │
│• Envía OSE/SUNAT │      │• Saldo pendiente │      │  stock en kardex │
│• Recibe CDR      │      │  en cta corriente│      │  (si almacenable)│
│• ZIP + QR en PDF │      │                  │      │                  │
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

1. **A nivel Fiscal y SUNAT (EDI)**:
   * Odoo compila el archivo **XML** bajo el estándar **UBL 2.1**.
   * Firma el archivo con el **Certificado Digital Tributario** de Textiles Atlas.
   * Envía el paquete comprimido al Web Service de **SUNAT**.
   * SUNAT valida el RUC emisor, RUC/DNI receptor, afectaciones de IGV y correlativo.
   * SUNAT/OSE devuelve la **Constancia de Recepción (CDR)** con código `0` (Aceptado).
   * El estado EDI cambia a **"Enviado"** (*Sent*) y se muestra un mensaje verde en el chatter.
   * Odoo descarga el ZIP oficial (`20558074427-01-F101-XXXX.zip`) y lo adjunta en el chatter.
   * Se genera el PDF con el **Código QR** para entrega al cliente.

   > [!IMPORTANT]
   > Cada envío para validación **consume 1 crédito IAP**. Si hay error y se reenvía, se consumen 2 créditos en total. Odoo ofrece 1000 créditos gratuitos para producción.

2. **A nivel Contable y Financiero**:
   * El estado del comprobante pasa de `Borrador` a **`Registrado / Publicado (Posted)`**.
   * Se genera automáticamente el **Asiento Contable de Venta**:
     * **Debe (Cuenta 12 - Clientes)**: Monto total a cobrar.
     * **Haber (Cuenta 40 - Tributos por Pagar IGV 18%)**: Débito fiscal para la declaración mensual.
     * **Haber (Cuenta 70 - Ventas / Ingresos)**: Valor neto de la mercadería.
   * Se actualiza la cuenta corriente del cliente como cuenta por cobrar pendiente de pago.

3. **A nivel de Inventario**:
   * Si el producto está configurado como bien almacenable (`is_storable = True`), el sistema registra la **salida de mercadería** descontando del stock físico y valorizado.

---

## 2. Anulación / Baja de Comprobantes (Notas de Crédito)

### ¿Qué mecanismos de anulación existen en Odoo Perú?

La doc oficial de Odoo 19 para Perú contempla **dos mecanismos** distintos:

| Mecanismo | Cuándo usarlo | Documento generado ante SUNAT |
|---|---|---|
| **Nota de Crédito** (`Tipo 07`) | Corrección o reversión de una factura/boleta que sí representó una operación real | XML Nota de Crédito con referencia al original |
| **Solicitud de Cancelación** (*Request Cancellation*) | Factura emitida **por error** (no representa ninguna operación) | Ticket de baja / Resumen de Anulación ante SUNAT |

> [!IMPORTANT]
> En Odoo SaaS 19.4 Perú existe el botón **"Solicitar Cancelación"** (*Request Cancellation*) que genera un flujo de anulación distinto a la Nota de Crédito. Úsalo cuando el comprobante fue emitido por error y no representa ninguna transacción real.

---

### A. Anulación mediante Nota de Crédito

1. Abre la Factura o Boleta en **Facturación > Clientes > Facturas**.
2. Haz clic en el botón **"Nota de Crédito"** (*Add Credit Note*).
3. Se abrirá una ventana emergente:
   * **Motivo del Crédito**: Selecciona el código SUNAT correspondiente (ej. **`01 - Anulación de la operación`**).
   * **Método de crédito**: Para la **primera nota de crédito**, selecciona **"Reembolso parcial"** (*Partial Refund*) — esto permite definir la secuencia de la Nota de Crédito.
   * **Diario**: Diario de Ventas.
4. Haz clic en **Revertir** (*Reverse*).
5. Odoo crea un borrador de Nota de Crédito vinculada al comprobante original:
   * Para Factura: Serie **`FC01-XXXXXXXX`** (Tipo doc: Nota de Crédito Electrónica).
   * Para Boleta: Serie **`BC01-XXXXXXXX`**.
6. Confirma la nota de crédito. El flujo EDI es **idéntico al de facturas**: estado "Por Enviar" → cron o "Enviar ahora".

> [!NOTE]
> *"El flujo EDI para Notas de Crédito funciona de la misma manera que para facturas"* — documentación oficial Odoo 19.

---

### B. Anulación directa mediante Solicitud de Cancelación

Para facturas confirmadas y enviadas a SUNAT que fueron emitidas **por error**:

1. Abre la Factura o Boleta confirmada y enviada a SUNAT.
2. Haz clic en el botón **"Solicitar Cancelación"** (*Request Cancellation*).
3. Proporciona el **motivo de cancelación** en el campo solicitado.
4. El estado EDI cambia a **"Por Cancelar"** (*To Cancel*).
5. El cron lo despacha automáticamente (o usa **"Enviar ahora"**). SUNAT genera el ticket de anulación y devuelve el CDR.
6. Estado final: **"Cancelado"** (*Cancelled*), con ZIP y CDR registrados en el chatter.

> [!NOTE]
> Cada solicitud de cancelación también **consume 1 crédito IAP**.

---

### C. ¿Qué desencadena Odoo al Emitir la Nota de Crédito?

```
┌────────────────────────────────────────────────────────────────────────┐
│                   NOTA DE CRÉDITO (MOTIVO 01)                          │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│ 1. SUNAT (EDI)   │      │ 2. Contabilidad  │      │ 3. Conciliación  │
├──────────────────┤      ├──────────────────┤      ├──────────────────┤
│• Declara la      │      │• Extorna el IGV  │      │• Saldo pendiente │
│  anulación con   │      │  (resta débito   │      │  baja a S/ 0.00  │
│  referencia a la │      │   fiscal del mes)│      │• Factura queda   │
│  factura original│      │• Extorna el      │      │  en estado       │
│• CDR Aceptado    │      │  ingreso Cta 70  │      │  "Pagado/Revert" │
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

1. **A nivel Fiscal y SUNAT**:
   * Odoo genera el XML de Nota de Crédito con el nodo de referencia al comprobante afectado:
     * *Tipo de documento modificado*: `01` (Factura) o `03` (Boleta).
     * *Serie y número modificado*: ej. `F101-00000005`.
     * *Código de motivo*: `01` (Anulación de la operación).
   * SUNAT procesa la nota de crédito y emite el **CDR de aceptación**, dando por anulada la operación ante el fisco.

2. **A nivel Contable y Financiero**:
   * Odoo genera un **asiento contable inverso**:
     * **Haber (Cuenta 12)**: Disminuye la cuenta por cobrar.
     * **Debe (Cuenta 40)**: Extorna el IGV, asegurando que **no pagues impuestos de una venta cancelada**.
     * **Debe (Cuenta 70)**: Extorna el ingreso por ventas.
   * **Conciliación automática**: Odoo cruza la factura original contra la nota de crédito, cerrando ambas transacciones con saldo **`S/ 0.00`** y marcándolas como `Pagado / Revertido`.

3. **A nivel de Inventario**:
   * Odoo permite generar el movimiento de reingreso de mercadería al almacén para que el kardex físico vuelva a contar con el producto disponible para la venta.

---

## 3. Matriz de Estados en Odoo

| Estado en Odoo | ¿Tiene validez fiscal? | ¿Se puede modificar? | ¿Qué hacer si hay un error? |
| :--- | :--- | :--- | :--- |
| **Borrador (Draft)** | No | Sí, se puede editar o eliminar | Corrige o borra sin rastro |
| **Publicado / EDI "Por Enviar"** | Contablemente sí, fiscalmente pendiente | No alterable | Usa **Solicitar Cancelación** si fue error; si es válida, espera el envío al cron |
| **Publicado / EDI "Enviado"** | **Sí, oficial ante SUNAT** | No se puede alterar | Emite **Nota de Crédito** para revertir; usa **Solicitar Cancelación** si fue error de emisión |
| **Revertido / Pagado por Nota de Crédito** | Anulado fiscalmente | Cerrado | La operación queda con saldo contable S/ 0.00 |
| **Cancelado** (*Cancelled*) | Anulado fiscalmente | Cerrado | Ticket de baja enviado a SUNAT vía Solicitud de Cancelación |

---

## 4. Campos EDI exclusivos de Perú (`l10n_pe`)

Estos campos son propios de la localización peruana y **obligatorios** para el EDI:

| Campo | Ubicación | Descripción |
|---|---|---|
| **Tipo de Documento** | Cabecera de factura | Factura Electrónica, Boleta, Nota de Crédito, Nota de Débito |
| **Tipo de Operación** | Cabecera de factura | Venta Interna, Exportación de Bienes, op. 1001 (Detracción), etc. |
| **Razón de Afectación EDI** | Cada línea de factura | Alcance fiscal del IGV por línea (ej. `10 - Gravado`) |
| **Tipo de Identificación** | Partner / Cliente | RUC, DNI, CE, Pasaporte, ID Extranjero, etc. |
| **Código UNSPC** | Producto | Código de producto estándar requerido por SUNAT en el XML |

---

## 5. Buenas Prácticas Recomendadas

1. **Revisar en Borrador antes de Confirmar**: Verifica el RUC/DNI, el Tipo de Documento y las cantidades antes de presionar *Confirmar*. El cron puede enviarlo a SUNAT en < 1 hora.
2. **Plazos de SUNAT**:
   * Las Facturas deben enviarse a SUNAT dentro de los **3 días calendario** posteriores a la fecha de emisión.
   * Las Notas de Crédito deben emitirse preferentemente dentro del mismo mes tributario para no generar desajustes en la declaración del IGV.
3. **Consulta de CDR**: Confirma que en el chatter figure el mensaje verde de SUNAT. Si el estado EDI queda en "Por Enviar", revisa los errores y reenvía.
4. **Cancelación vs Nota de Crédito**: Usa **Solicitar Cancelación** para errores de emisión (factura que no debió existir). Usa **Nota de Crédito** para operaciones reales que se revierten.
5. **Créditos IAP**: Monitorea el saldo de créditos IAP. Cada envío y cada cancelación consume **1 crédito**.
