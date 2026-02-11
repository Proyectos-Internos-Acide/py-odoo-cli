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

## Proyectos Actuales

### hotel-trip-agency
Scripts y herramientas para gestión de timezones en instancias de Odoo relacionadas con hoteles y agencias de viajes.

## Ejecutar Scripts con Docker

Los scripts de `knowledge/` pueden ejecutarse directamente con Docker sin necesidad de instalar Python localmente:

```bash
# Usando el script helper (recomendado)
./run-knowledge.sh knowledge/hotel-trip-agency/setup_timezone.py

# O directamente con docker-compose
docker-compose run --rm odoo-cli python knowledge/hotel-trip-agency/setup_timezone.py
```

La carpeta `knowledge/` está montada como volumen en Docker, por lo que todos los datos, scripts y documentación se persisten y están disponibles en cada ejecución.

## Agregar un Nuevo Proyecto

1. Crea una nueva carpeta dentro de `knowledge/` con un nombre descriptivo
2. Agrega tus scripts específicos del proyecto
3. Incluye un `README.md` explicando el propósito y uso del proyecto
4. Asegúrate de que los scripts importen correctamente `odoo_cli`:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from odoo_cli import OdooClient
```

**Nota:** Si usas Docker, los scripts pueden importar directamente sin necesidad de ajustar `sys.path`, ya que el código está en el contenedor.

## Notas

- Todos los proyectos comparten la misma biblioteca `odoo_cli` desde la raíz
- Cada proyecto puede tener su propia configuración si es necesario
- Los scripts deben ser independientes y documentados
