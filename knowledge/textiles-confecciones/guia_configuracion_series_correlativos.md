# Guía Paso a Paso: Verificación y Configuración de Series y Correlativos en Odoo

Esta guía detalla cómo verificar, configurar y gestionar la serie **`F101`** (Factura) y **`B101`** (Boleta) desde el número **`00000005`** directamente en la interfaz web de Odoo.

---

## 1. Dónde verificar los Borradores ya configurados con F101-00000005 y B101-00000005

Para comprobar los comprobantes de prueba ya creados en tu Odoo:

1. Ingresa a tu Odoo: [`https://textiles-confecciones-atlas.odoo.com`](https://textiles-confecciones-atlas.odoo.com).
2. Abre la aplicación **Facturación** (o **Contabilidad**).
3. En el menú superior, ve a **Clientes** > **Facturas**.
4. Verás la lista de facturas en estado **Borrador**:
   * **`F101-00000005`**: Factura a *COLEGIO MÉDICO DEL PERÚ* por S/ 1.00.
   * **`B101-00000005`**: Boleta a *CLIENTE BOLETA PRUEBA* por S/ 1.00.

---

## 2. Cómo funciona el inicio de la Serie en Odoo (Localización Perú - LATAM)

En Odoo Enterprise con localización peruana (`l10n_latam`), los correlativos se controlan directamente en el comprobante:

```
[Tipo de Documento]   +   [Número de Documento]   ──(Al Confirmar)──> Secuencia Fijada
 (01) Factura             F101-00000005                                Siguiente: F101-00000006
 (03) Boleta              B101-00000005                                Siguiente: B101-00000006
```

### Paso a paso para iniciar una serie manualmente desde la interfaz:

1. **Crear una Factura nueva**:
   * Clic en **Nuevo** en *Clientes > Facturas*.
2. **Seleccionar el Tipo de Documento**:
   * En el campo **Tipo de Documento**, selecciona:
     * **`(01) Factura`** (para Facturas con RUC).
     * **`(03) Boleta`** (para Boletas con DNI o consumidor final).
3. **Establecer la Serie y Correlativo inicial**:
   * En la parte superior del formulario (o en el campo **Número de documento** / **Number**), Odoo permite escribir directamente el correlativo que deseas inaugurar:
     * Para Factura: escribe **`F101-00000005`**
     * Para Boleta: escribe **`B101-00000005`**
4. **Presionar "Confirmar"**:
   * Al hacer clic en el botón morado **Confirmar**:
     1. Odoo valida la estructura del número (`4 caracteres de serie + guion + 8 dígitos`).
     2. El sistema **registra en memoria la secuencia** para ese diario y tipo de documento.
     3. A partir de ese momento, la siguiente factura que crees se generará **automáticamente** como `F101-00000006`, luego `F101-00000007`, y así sucesivamente sin necesidad de escribir el número a mano.

---

## 3. Dónde verificar la Configuración General de SUNAT en la Interfaz

Para revisar que el certificado digital y las credenciales SOL estén enlazadas:

1. Ve a **Contabilidad** (o **Facturación**) > **Configuración** > **Ajustes**.
2. Desplázate hacia abajo hasta la sección **Facturación Electrónica Peruana** (*Peruvian Electronic Invoicing*):
   * **Proveedor EDI**: Debe estar marcado en **SUNAT**.
   * **Certificado (PE)**: Debe mostrar **`Certificado Digital SUNAT - TEXTILES ATLAS`**.
   * **Usuario SOL**: `20558074427FARIDESO` *(formato RUC + Usuario)*.
   * **Contraseña SOL**: `••••••••`
   * **Modo de prueba (*Test Environment*)**: Desmarcado (Modo Producción Oficial).

---

## 4. Dónde verificar el Diario de Ventas (Uso de Documentos)

1. Ve a **Contabilidad** > **Configuración** > **Diarios Contables**.
2. Abre el diario **Ventas** (*código `INV`*).
3. En la pestaña **Ajustes avanzados**:
   * Verifica que la casilla **Utilizar Documentos** (*Use Documents / l10n_latam_use_documents*) esté **activa**. Esto es lo que permite a Odoo desglosar series `F101`, `B101`, Notas de Crédito, etc.

---

## 5. Resumen de Reglas de SUNAT para Series

| Tipo de Comprobante | Regla de Serie SUNAT | Formato Odoo | Siguiente automático |
| :--- | :--- | :--- | :--- |
| **Factura Electrónica** | Debe iniciar con **F** (4 caracteres) | `F101-00000005` | `F101-00000006` |
| **Boleta Electrónica** | Debe iniciar con **B** (4 caracteres) | `B101-00000005` | `B101-00000006` |
| **Nota de Crédito (Factura)** | Debe iniciar con **F** (ej. FC01 / FN01) | `FC01-00000001` | `FC01-00000002` |
| **Nota de Crédito (Boleta)** | Debe iniciar con **B** (ej. BC01 / BN01) | `BC01-00000001` | `BC01-00000002` |
