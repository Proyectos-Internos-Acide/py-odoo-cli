## CM Line - Producción y Unidades de Medida

Este proyecto contiene scripts para configurar **unidades de medida estándar** para CM Line, orientadas a productos que se venden en **unidades, paquetes, cientos y millares**, además de algunos empaques frecuentes.

El objetivo es:
- **Estandarizar las UoM** en Odoo.
- **Facilitar precios por cantidad** (unidad, ciento, millar, paquete).
- Dejar una base documentada que puedas ajustar según tu operación real.

---

## Modelo de Unidades (supuestos)

Se parte de la unidad base estándar de Odoo:
- **`Units`** (uom estándar de Odoo) = venta unitaria / pieza.

Sobre esa base, el script crea (si no existen) las siguientes UoM en la **misma categoría**:

- **Paquete 25**: 1 paquete = 25 unidades.
- **Paquete 50**: 1 paquete = 50 unidades.
- **Docena**: 1 docena = 12 unidades.
- **Ciento**: 1 ciento = 100 unidades.
- **Millar**: 1 millar = 1000 unidades.
- **Caja 1000**: 1 caja = 1000 unidades (pensada como caja completa de producto, usualmente 20 paquetes de 50).
- **Bolsa 50**: 1 bolsa = 50 unidades.
- **Saco 25**: 1 saco = 25 unidades.
- **Bobina**: 1 bobina = 1 unidad (pensada como “pieza” completa; el largo real depende del producto).

Además, en la categoría de **volumen**, se crean:

- **Galón**: 1 galón = 3.785 litros.
- **Metro cúbico**: 1 m³ = 1000 litros.

> **Importante:** Estos factores son supuestos razonables. Si tu operación usa otros tamaños (por ejemplo, caja de 500 unidades, bolsa de 100, etc.), puedes:
> - Ajustar los factores editando la UoM en Odoo, o
> - Pedirme que adaptemos el script a tus reglas específicas.

---

## Script principal

El script principal de este proyecto es:

- `setup_uom.py`: se conecta a Odoo usando `OdooClient` y:
  - Detecta automáticamente la categoría de `Units` (unidad base).
  - Detecta automáticamente la categoría de `L` (litros) para volumen.
  - Crea (si no existen) todas las unidades descritas arriba.
  - No toca unidades existentes, solo añade nuevas.

---

## Cómo ejecutar el script

### Con Docker Compose (recomendado)

Desde la raíz del proyecto `py-odoo-cli`:

```bash
docker-compose run --rm odoo-cli python knowledge/cmline-production/setup_uom.py
```

### Sin Docker (usando el entorno virtual local)

```bash
cd /ruta/a/py-odoo-cli-1
.venv/bin/python knowledge/cmline-production/setup_uom.py
```

El script:
- Muestra la categoría detectada para unidades y volumen.
- Informa qué UoM ya existían y cuáles se acaban de crear.

---

## Relación con precios y costos

Con este modelo puedes:

- Definir un **precio por Unidad** y luego:
  - Crear reglas de lista de precios para `Ciento`, `Millar`, `Paquete 25`, `Paquete 50`, etc.
  - Hacer que Odoo ajuste automáticamente precios y costos según la UoM seleccionada en la línea de venta / compra.

El script **no toca precios ni productos**, solo prepara la base de unidades de medida para que luego puedas:
- Configurar precios por UoM.
- Usar las UoM correctas en productos y movimientos de inventario.

