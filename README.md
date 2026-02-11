<!--
  py-odoo-cli · Cliente XML-RPC para Odoo
  Diseño sobrio y profesional. Sin emojis.
-->

<div align="center">

# py-odoo-cli

**Cliente Python desacoplado para Odoo vía XML-RPC**

---

</div>

Biblioteca reutilizable que centraliza la interacción con Odoo usando variables de entorno (`.env`) y una API mínima y predecible.

**Diseñado para trabajar con editores de IA**: Configura tu `.env`, abre el proyecto en tu editor de IA (Cursor, etc.), y pídele que cree scripts específicos para tu proyecto. La IA crea scripts en `knowledge/<tu-proyecto>/` que puedes ejecutar inmediatamente con Docker.

---

## Características

| Aspecto        | Descripción |
|----------------|-------------|
| **Desacoplada** | Lógica core separada de configuración y casos de uso. |
| **Configurable** | Credenciales y opciones vía `.env`. |
| **API sencilla** | Wrappers para `search_read`, `create`, `write`, `unlink`. |
| **CLI incluido** | Punto de entrada `main.py` para pruebas y tareas rápidas. |
| **Dockerizado** | Ejecuta sin instalar Python localmente. |
| **IA-friendly** | Diseñado para que editores de IA creen scripts en `knowledge/`. |

---

## Instalación

**1. Clonar el repositorio**

```bash
git clone https://github.com/your-user/py-odoo-cli.git
cd py-odoo-cli
```

**2. Instalar [UV](https://docs.astral.sh/uv/) y dependencias**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

**3. Configurar entorno**

Copia `.env.example` a `.env` y ajusta credenciales:

```bash
cp .env.example .env
```

Contenido mínimo de `.env`:

```env
ODOO_URL=https://tu-instancia.odoo.com
ODOO_DB=tu-base-de-datos
ODOO_USER=email@ejemplo.com
ODOO_PASSWORD=tu-api-key
```

---

## Instalación con Docker

**Sin necesidad de instalar Python localmente**

**1. Clonar el repositorio**

```bash
git clone https://github.com/your-user/py-odoo-cli.git
cd py-odoo-cli
```

**2. Configurar entorno**

Copia `.env.example` a `.env` y ajusta credenciales:

```bash
cp .env.example .env
```

**3. Construir la imagen**

```bash
docker-compose build
```

**4. Usar el CLI**

```bash
# Probar conexión
docker-compose run --rm odoo-cli test-connection

# Listar registros
docker-compose run --rm odoo-cli list res.partner --limit 5 --fields name,email

# Listar módulos instalados
docker-compose run --rm odoo-cli list-modules

# Listar parámetros del sistema
docker-compose run --rm odoo-cli list-config
```

**Nota:** El flag `--rm` elimina el contenedor después de ejecutar el comando. La carpeta `knowledge/` está montada como volumen para persistir datos y scripts.

**Alternativa con Docker directamente:**

```bash
# Construir imagen
docker build -t py-odoo-cli .

# Ejecutar comandos
docker run --rm --env-file .env -v $(pwd)/knowledge:/app/knowledge py-odoo-cli test-connection
docker run --rm --env-file .env -v $(pwd)/knowledge:/app/knowledge py-odoo-cli list res.partner --limit 5
```

**Ejecutar scripts de la carpeta `knowledge/`:**

La carpeta `knowledge/` contiene scripts y casos de uso específicos. Puedes ejecutarlos con Docker:

```bash
# Usando el script helper
./run-knowledge.sh knowledge/hotel-trip-agency/setup_timezone.py

# O directamente con docker-compose
docker-compose run --rm odoo-cli python knowledge/hotel-trip-agency/setup_timezone.py
```

**Flujo de trabajo con IA:**

1. Configura tu `.env` con credenciales de Odoo
2. Abre el proyecto en tu editor de IA (Cursor, etc.)
3. Pide a la IA que cree scripts para tu proyecto: *"Crea un script para sincronizar productos desde mi ERP"*
4. La IA crea `knowledge/<tu-proyecto>/` con los scripts
5. Ejecuta inmediatamente con Docker (sin reconstruir la imagen):
   ```bash
   docker-compose run --rm odoo-cli python knowledge/mi-proyecto/mi_script.py
   ```

Los datos y scripts en `knowledge/` se persisten como volumen, permitiendo "alimentar el cerebro" con información y casos de uso específicos que se mantienen entre ejecuciones. Ver [knowledge/README.md](knowledge/README.md) para más detalles.

---

## Uso

### Como biblioteca

```python
from odoo_cli import OdooClient

client = OdooClient()
uid = client.connect()

partners = client.search_read(
    'res.partner',
    [['customer_rank', '>', 0]],
    limit=5
)
for p in partners:
    print(p['name'])
```

### Desde la CLI

| Acción              | Comando |
|---------------------|---------|
| Probar conexión     | `uv run python main.py test-connection` |
| Listar registros    | `uv run python main.py list res.partner --limit 5 --fields name,email` |
| Módulos instalados  | `uv run python main.py list-modules` |
| Parámetros sistema  | `uv run python main.py list-config` |

---

## Estructura del proyecto

```
py-odoo-cli/
├── odoo_cli/              # Biblioteca core
│   ├── client.py          # Cliente y wrappers
│   ├── config.py          # Carga y validación
│   └── exceptions.py      # Excepciones propias (manejo de errores)
├── main.py                # CLI general
├── knowledge/             # Base de conocimiento (proyectos y casos de uso)
│   └── hotel-trip-agency/
│       ├── setup_timezone.py
│       └── debug_planning.py
└── tests/
```

### Carpeta `knowledge/`

Contiene proyectos concretos y casos de uso que usan `odoo_cli`. Cada proyecto vive en su propia carpeta con scripts, documentación y, si aplica, configuraciones propias. La raíz del repo se mantiene limpia y el conocimiento queda organizado por implementación.

Más detalles en [knowledge/README.md](knowledge/README.md).

---

## Manejo de errores

La biblioteca define excepciones propias para que puedas distinguir fallos de configuración, conexión o respuestas del servidor Odoo.

| Excepción | Cuándo se lanza |
|-----------|------------------|
| `OdooConfigError` | Faltan variables en `.env` o la configuración es inválida. |
| `OdooConnectionError` | No se puede conectar a la URL de Odoo o la autenticación falla. |
| `OdooFaultError` | Odoo devuelve un error (permisos, validación, regla de negocio). Incluye `fault_code` y `fault_string`. |
| `OdooExecutionError` | Fallo durante la ejecución (red, timeout, etc.). |

Todas heredan de `OdooClientError`, así que puedes capturar cualquier error de la biblioteca con una sola cláusula si lo prefieres.

**Ejemplo**

```python
from odoo_cli import OdooClient, OdooConfigError, OdooConnectionError, OdooFaultError

try:
    client = OdooClient()
    client.connect()
    client.create("res.partner", {"name": "Test"})
except OdooConfigError:
    print("Revisa tu archivo .env")
except OdooConnectionError:
    print("No se pudo conectar o credenciales incorrectas")
except OdooFaultError as e:
    print(f"Error de Odoo: {e.fault_string} (código: {e.fault_code})")
```

---

<div align="center">

*py-odoo-cli — Servicio del CLI.*

</div>
