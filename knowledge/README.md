# Base de Conocimiento

Esta carpeta contiene proyectos específicos y casos de uso que utilizan la biblioteca `py-odoo-cli`. Cada proyecto representa una implementación real o un conjunto de scripts desarrollados para resolver problemas específicos de Odoo.

## Propósito

- **Organización**: Mantiene la raíz del proyecto limpia y estructurada
- **Conocimiento**: Documenta soluciones y patrones específicos de cada proyecto
- **Reutilización**: Permite compartir scripts y conocimiento entre proyectos similares
- **Escalabilidad**: Facilita agregar nuevos proyectos sin afectar la estructura base

## Estructura de un Proyecto

Cada proyecto dentro de `knowledge/` debe tener:

```
knowledge/
└── nombre-proyecto/
    ├── README.md              # Documentación del proyecto
    ├── script1.py            # Scripts específicos
    ├── script2.py
    └── *.md                   # Documentación adicional
```

## Proyectos actuales

Algunos proyectos incluidos en esta carpeta:

- `hotel-trip-agency`: gestión de timezones en instancias de Odoo relacionadas con hoteles y agencias de viajes.
- `cmline-eirl-inventory` y `cmline-production`: inventario y unidades de medida para CM Line.
- `machu-picchu-exclusive-tours`: actividades y configuración para un proyecto de tours en Machu Picchu.
- `peru-flores-tours-test`: pruebas y automatización para un sitio web de turismo.
- `production-inventory`: flujos completos de compra y venta con lotes y ubicaciones.
- `test-crm`: configuración y datos de ejemplo para flujos CRM.
- `tohalino`: facturación electrónica y flujos relacionados con SUNAT.

## Ejecutar scripts con entorno virtual

Los scripts de `knowledge/` se ejecutan desde tu entorno virtual de Python ya activado:

```bash
python knowledge/hotel-trip-agency/setup_timezone.py
python knowledge/machu-picchu-exclusive-tours/generar_actividades_turismo.py
python knowledge/tohalino/electronic-invoicing/create_test_invoice.py
```

## Flujo de Trabajo con IA

Este proyecto está diseñado para trabajar con editores de IA (como Cursor):

1. **Configura tu `.env`** con las credenciales de tu instancia Odoo
2. **Abre el proyecto** en tu editor de IA
3. **Pide a la IA** que cree scripts para tu proyecto específico:
   - "Crea un script para sincronizar productos desde mi ERP"
   - "Necesito un script que actualice los precios de productos"
   - "Crea un script para migrar datos de clientes"
4. **La IA crea una carpeta** en `knowledge/<nombre-proyecto>/` con los scripts
5. **Ejecuta los scripts** desde tu entorno virtual:
   ```bash
   python knowledge/mi-proyecto/mi_script.py
   ```

## Agregar un Nuevo Proyecto

1. Crea una nueva carpeta dentro de `knowledge/` con un nombre descriptivo
2. Agrega tus scripts específicos del proyecto (puedes usar `_template/script_template.py` como referencia)
3. Incluye un `README.md` explicando el propósito y uso del proyecto
4. Asegúrate de que los scripts importen correctamente `odoo_cli`:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient
```

**Nota:** Mientras tu entorno virtual esté activado y el paquete esté instalado en modo editable (`pip install -e .`), los scripts pueden importar `odoo_cli` directamente sin pasos adicionales.

## Notas

- Todos los proyectos comparten la misma biblioteca `odoo_cli` desde la raíz
- Cada proyecto puede tener su propia configuración si es necesario
- Los scripts deben ser independientes y documentados
