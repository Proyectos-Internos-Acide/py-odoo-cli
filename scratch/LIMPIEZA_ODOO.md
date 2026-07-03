# 🧹 Guía de Limpieza de Odoo — Wayki Trek

> **Propósito:** Eliminar leads, oportunidades, contactos de prueba y cotizaciones
> de Odoo **definitivamente** (no solo archivar), y reiniciar el correlativo de ventas.

---

## ⚠️ IMPORTANTE: Por qué no funciona el método normal

Esta instancia de **Odoo SaaS 19.2** tiene un **bug conocido** en el ORM que impide
eliminar registros vía API estándar (`unlink`) y vía la interfaz web en algunos modelos:

```
TypeError: unhashable type: 'list'
```

El error ocurre en `crm_lead.unlink()`, `mail_thread.unlink()` e `ir.actions.server.run()`
cuando se llaman vía XML-RPC. También falla `write({'active': False})` en `sale.order`.

**La solución que funciona:** inyectar SQL directo (`env.cr.execute`) en la
**server action 643** (que ya existe y tiene el contexto correcto), ejecutarla
vía **JSON-RPC** (`/web/dataset/call_kw`), y luego restaurar el código original.

---

## 📁 Scripts disponibles

| Script | Descripción |
|--------|-------------|
| `scratch/cleanup_jsonrpc.py` | ✅ **EL QUE FUNCIONA** — Limpieza completa vía JSON-RPC + SQL directo |
| `scratch_fix_action_643.py` | Restaura el código de la action 643 (correo confirmación) |
| `scratch/cleanup_full.py` | Intento anterior (falla por bug ORM al crear server actions) |
| `scratch/cleanup_via_643.py` | Intento anterior (falla vía XML-RPC) |

---

## 🚀 Procedimiento de limpieza paso a paso

### Requisitos previos

```bash
cd /home/acide/py-odoo-cli
# activar entorno virtual si es necesario
```

Verificar que el archivo de configuración tiene las credenciales correctas:
- `ODOO_URL=https://wayki-trek.odoo.com`
- `ODOO_DB=wayki-trek`
- `ODOO_USER=network@waykitrek.net`
- `ODOO_PASSWORD=...`

---

### Paso 1: Ejecutar la limpieza

```bash
.venv/bin/python scratch/cleanup_jsonrpc.py
```

El script hace lo siguiente **automáticamente**:

1. Conecta a Odoo vía XML-RPC (para leer datos) y JSON-RPC (para ejecutar)
2. Obtiene todos los IDs de leads/oportunidades (activos e inactivos)
3. Obtiene los contactos a eliminar (excluye usuarios y empresa)
4. Construye SQL con el **orden correcto de FK** (Foreign Keys)
5. Inyecta el SQL en la **server action 643** temporalmente
6. Ejecuta la acción vía JSON-RPC
7. **Restaura el código original** de la acción 643 automáticamente
8. Reinicia el correlativo de ventas a 1

---

### Paso 2: Verificar el resultado

```bash
.venv/bin/python -c "
import sys
sys.path.insert(0, 'knowledge/wayki-trek-develop/29_custom_quote_app')
from odoo_cli import OdooClient
client = OdooClient()
client.connect()
leads  = client.search_read('crm.lead', [('active', 'in', [True, False])], ['id'])
quotes = client.search_read('sale.order', [], ['id'])
seqs   = client.search_read('ir.sequence', [('code', '=', 'sale.order')], ['id', 'number_next_actual'])
print(f'Leads en BD:        {len(leads)}')
print(f'Cotizaciones:       {len(quotes)}')
for s in seqs:
    print(f\"Correlativo ventas: {s['number_next_actual']}\")
"
```

Resultado esperado:
```
Leads en BD:        0
Cotizaciones:       0
Correlativo ventas: 1
```

---

### Paso 3 (si algo falló): Restaurar la acción 643

Si el script no terminó limpiamente y la acción 643 quedó con el SQL en lugar del
código de correo, ejecutar:

```bash
.venv/bin/python scratch_fix_action_643.py
```

---

## 🔧 Cómo funciona internamente

### Por qué usamos la server action 643 como "vehículo"

La action 643 ya existe en Odoo con `model_id` correctamente configurado.
Crear una nueva server action falla por el mismo bug del ORM. Llamar `run()`
vía XML-RPC también falla. La única ruta que funciona es:

1. Modificar el `code` de la action 643 via XML-RPC (esto SÍ funciona)
2. Ejecutar la action via JSON-RPC en `/web/dataset/call_kw` (que tiene otra ruta interna)
3. Restaurar el código original

### Orden correcto de dependencias FK (PostgreSQL)

Para eliminar un `crm.lead` sin errores de FK:

```sql
-- Paso 1: obtener IDs de mensajes del lead
SELECT id FROM mail_message WHERE model='crm.lead' AND res_id IN (...ids...);

-- Paso 2: limpiar tablas hijas de mail_message (ANTES de borrar mail_message)
DELETE FROM mail_notification WHERE mail_message_id IN (...msg_ids...);
DELETE FROM mail_message_res_partner_rel WHERE mail_message_id IN (...msg_ids...);
DELETE FROM mail_tracking_value WHERE mail_message_id IN (...msg_ids...);
-- Tabla opcional (SAVEPOINT):
DELETE FROM mail_message_res_partner_needaction_rel WHERE mail_message_id IN (...);

-- Paso 3: borrar los mensajes
DELETE FROM mail_message WHERE id IN (...msg_ids...);

-- Paso 4: limpiar el resto de relaciones del lead
DELETE FROM mail_activity WHERE res_model='crm.lead' AND res_id IN (...ids...);
DELETE FROM mail_followers WHERE res_model='crm.lead' AND res_id IN (...ids...);
-- Tabla opcional (SAVEPOINT):
DELETE FROM calendar_event_crm_lead_rel WHERE crm_lead_id IN (...ids...);
DELETE FROM rating_rating WHERE res_model='crm.lead' AND res_id IN (...ids...);

-- Paso 5: finalmente el lead
DELETE FROM crm_lead WHERE id IN (...ids...);
```

Para `res.partner` (contactos): misma secuencia, cambiando `model='res.partner'`
y terminando con `DELETE FROM res_partner WHERE id IN (...)`.

### SAVEPOINTs para tablas opcionales

Algunas tablas pueden no existir en todas las versiones de Odoo. Si el DELETE
falla, PostgreSQL aborta la transacción completa. Con SAVEPOINTs se maneja así:

```python
env.cr.execute("SAVEPOINT sp_cal")
try:
    env.cr.execute("DELETE FROM calendar_event_crm_lead_rel WHERE crm_lead_id IN (...)")
    env.cr.execute("RELEASE SAVEPOINT sp_cal")
except Exception:
    env.cr.execute("ROLLBACK TO SAVEPOINT sp_cal")
```

---

## 📋 Qué NO se elimina (siempre protegido)

- ✅ Todos los **productos, tours y servicios** (`product.template`, `product.product`)
- ✅ Los **4 usuarios** del sistema y sus partners vinculados
- ✅ La **empresa Wayki Trek** y su partner
- ✅ Partners del sistema con ID 1-9 (internos de Odoo)
- ✅ La **configuración SMTP** y servidores de correo entrante/saliente
- ✅ La **server action 643** (código restaurado al terminar)
- ✅ Todas las **automatizaciones y etapas** del CRM
- ✅ **Secuencias** (excepto que se reinicia el número a 1)

---

## 🔄 Personalizar qué se limpia

Editar `scratch/cleanup_jsonrpc.py`:

### Solo limpiar leads (NO contactos):
Buscar `if pt:` y comentar ese bloque completo.

### No reiniciar el correlativo:
Buscar la sección `Reiniciar correlativo` y comentarla.

### Limpiar también mensajes de correo (`mail.mail`):
Agregar en el bloque SQL de leads:
```python
env.cr.execute("DELETE FROM mail_mail WHERE model='crm.lead' AND res_id IN {lt}")
```

### Cambiar correlativo a otro número (ej. empezar en 10):
```python
client.write('ir.sequence', [s['id']], {'number_next_actual': 10})
```

---

## 🆘 Solución de problemas

### `unhashable type: 'list'` al ejecutar `ir.actions.server.run`
**Causa:** Bug del ORM de Odoo SaaS 19.2 vía XML-RPC.
**Solución:** Usar `cleanup_jsonrpc.py` (ya usa JSON-RPC).

### `InFailedSqlTransaction: current transaction is aborted`
**Causa:** Un DELETE falla por FK constraint y aborta toda la transacción.
**Solución:** Envolver el DELETE problemático en un SAVEPOINT (ver sección anterior).

### La acción 643 no envía correos después de la limpieza
**Causa:** El script no restauró el código original.
**Solución:**
```bash
.venv/bin/python scratch_fix_action_643.py
```
Luego verificar:
```bash
.venv/bin/python -c "
import sys
sys.path.insert(0, 'knowledge/wayki-trek-develop/29_custom_quote_app')
from odoo_cli import OdooClient
c = OdooClient(); c.connect()
a = c.search_read('ir.actions.server', [('id','=',643)], ['name','code'])
print(a[0]['name'])
print(a[0]['code'][:300])
"
```
El código debe empezar con algo como `record = env['crm.lead'].browse(...)` o
`email_from = ...`, NO con `DELETE FROM`.

### Los leads aparecen "archivados" en Odoo pero no eliminados
Si se ejecutó una limpieza anterior con `active=False` en vez de SQL directo,
los registros están en la BD con `active=False`. El script `cleanup_jsonrpc.py`
incluye `active IN (True, False)` en sus queries, así que los eliminará también.

---

## 📅 Historial de limpiezas

| Fecha | Registros eliminados | Notas |
|-------|---------------------|-------|
| 2026-07-03 | ~1652 leads, 8 contactos, 1 cotización | Primera limpieza producción |

*Actualizar esta tabla con cada limpieza futura.*
