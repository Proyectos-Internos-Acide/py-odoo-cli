# Registro de Emisión Exitosa a SUNAT - Textiles y Confecciones Atlas

**Fecha de Emisión**: 25 de Septiembre de 2026  
**Empresa Emisora**: TEXTILES Y CONFECCIONES ATLAS E.I.R.L. (RUC: `20558074427`)  
**Proveedor EDI**: Conexión Directa a SUNAT con Certificado Digital Tributario propio  
**Estado General**: **ACEPTADO POR SUNAT (CDR Generado)**

---

## 1. Factura Electrónica

* **Número**: **`F101-00000005`** (ID Odoo: `2`)
* **Tipo de Documento**: `01 - Factura`
* **Cliente**: `COLEGIO MÉDICO DEL PERÚ`
* **RUC Cliente**: `20139589638`
* **Dirección**: `Malecón de la Reserva N° 791, Lima`
* **Ítem**: `Polo 100% Algodón - Muestra Prueba` (1 Unidad)
* **Total**: **S/ 1.00** (Base gravada S/ 0.85 + IGV 18% S/ 0.15)
* **Archivo ZIP firmado y CDR**: `20558074427-01-F101-00000005.zip`
* **Respuesta SUNAT en Odoo**: *"The EDI document was successfully created and signed by the government."*
* **Estado en Odoo**: `Registrado` (`posted`) / `Enviado a SUNAT` (`sent`)

---

## 2. Boleta de Venta Electrónica

* **Número**: **`B101-00000005`** (ID Odoo: `3`)
* **Tipo de Documento**: `03 - Boleta`
* **Cliente**: `CLIENTE BOLETA PRUEBA`
* **DNI Cliente**: `72190044`
* **Ítem**: `Polo 100% Algodón - Muestra Prueba` (1 Unidad)
* **Total**: **S/ 1.00** (Base gravada S/ 0.85 + IGV 18% S/ 0.15)
* **Archivo ZIP firmado y CDR**: `20558074427-03-B101-00000005.zip`
* **Respuesta SUNAT en Odoo**: *"The EDI document was successfully created and signed by the government."*
* **Estado en Odoo**: `Registrado` (`posted`) / `Enviado a SUNAT` (`sent`)

---

## 3. Notas de Crédito Electrónicas Emitidas (Anulación de Comprobantes)

Ambos comprobantes de prueba fueron anulados formalmente ante SUNAT mediante sus respectivas Notas de Crédito Electrónicas con el motivo reglamentario **`01 - Anulación de la operación`**:

### A. Nota de Crédito para la Factura (F101-00000005)
* **Número**: **`FC01-00000001`** (ID Odoo: `4`)
* **Tipo de Documento**: `07 - Nota de Crédito`
* **Documento Modificado**: `F101-00000005` (COLEGIO MÉDICO DEL PERÚ)
* **Motivo SUNAT**: `01 - Anulación de la operación`
* **Monto Revertido**: **-S/ 1.00**
* **Archivo ZIP y CDR**: `20558074427-07-FC01-00000001.zip`
* **Respuesta SUNAT**: *"The EDI document was successfully created and signed by the government."*
* **Estado**: `sent` (Aceptado) / Factura original conciliada a saldo S/ 0.00.

### B. Nota de Crédito para la Boleta (B101-00000005)
* **Número**: **`BC01-00000001`** (ID Odoo: `5`)
* **Tipo de Documento**: `07 - Nota de Crédito Boleta`
* **Documento Modificado**: `B101-00000005` (CLIENTE BOLETA PRUEBA)
* **Motivo SUNAT**: `01 - Anulación de la operación`
* **Monto Revertido**: **-S/ 1.00**
* **Archivo ZIP y CDR**: `20558074427-07-BC01-00000001.zip`
* **Respuesta SUNAT**: *"The EDI document was successfully created and signed by the government."*
* **Estado**: `sent` (Aceptado) / Boleta original conciliada a saldo S/ 0.00.

---

## 4. Estado de las Secuencias en Odoo

* **Próxima Factura**: **`F101-00000006`**
* **Próxima Boleta**: **`B101-00000006`**
* **Próxima Nota de Crédito Factura**: **`FC01-00000002`**
* **Próxima Nota de Crédito Boleta**: **`BC01-00000002`**

