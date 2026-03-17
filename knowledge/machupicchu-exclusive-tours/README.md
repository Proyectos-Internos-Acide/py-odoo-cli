# Template para Nuevos Proyectos

Este directorio contiene templates y ejemplos para que la IA pueda crear nuevos scripts en `knowledge/`.

## Flujo de Trabajo Recomendado

1. **Usuario configura `.env`** con sus credenciales de Odoo
2. **Usuario abre el proyecto en su editor de IA** (Cursor, etc.)
3. **Usuario le pide a la IA**: "Crea un script para sincronizar productos desde mi ERP a Odoo"
4. **IA crea una carpeta** en `knowledge/` con el nombre del proyecto (ej: `knowledge/mi-erp-integration/`)
5. **IA crea scripts** usando el template `script_template.py` como referencia
6. **Usuario ejecuta** con Docker: `docker-compose run --rm odoo-cli python knowledge/mi-erp-integration/sync_products.py`

## Estructura de un Proyecto

```
knowledge/
└── mi-proyecto/
    ├── README.md              # Documentación del proyecto
    ├── sync_products.py       # Script principal
    ├── sync_customers.py      # Otros scripts relacionados
    └── data/                  # Datos específicos del proyecto (opcional)
        └── products.csv
```

## Importar odoo_cli

Todos los scripts deben importar `odoo_cli` así:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient
```

Con Docker, esto funciona automáticamente porque el código está montado en el contenedor.

## Ejecutar Scripts

```bash
# Con docker-compose (recomendado)
docker-compose run --rm odoo-cli python knowledge/mi-proyecto/mi_script.py

# Con el script helper
./run-knowledge.sh knowledge/mi-proyecto/mi_script.py
```
