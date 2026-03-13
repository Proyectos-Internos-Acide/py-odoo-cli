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

## Política estricta sobre Odoo Studio

**Queda terminantemente prohibido** el uso, instalación, activación o configuración de **Odoo Studio** (módulo `web_studio`) en **cualquier instancia de Odoo** que se gestione mediante este proyecto o sus scripts derivados.

- **No se debe instalar ni activar Odoo Studio** desde la interfaz web de Odoo ni mediante llamadas XML-RPC/JSON-RPC, ni directamente ni de forma indirecta (por ejemplo, instalando módulos que lo activen como dependencia).
- Cualquier script, procedimiento o manual de trabajo asociado a este repositorio debe **respetar y hacer cumplir esta prohibición**.
- Si una instancia ya tuviera Odoo Studio instalado, se deberá coordinar su **desinstalación o desactivación** siguiendo las políticas internas de la organización antes de seguir usando `py-odoo-cli` sobre esa base de datos.

Esta prohibición es **mandatoria y no negociable** según las directrices del responsable funcional/técnico del proyecto.

---

## Instalación

**1. Clonar el repositorio**

```bash
git clone https://github.com/your-user/py-odoo-cli.git
cd py-odoo-cli
```

**2. Crear y activar un entorno virtual**

Requiere Python 3.11 o superior.

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e .
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

Opcionales: `ODOO_VERIFY_SSL` (true/false), `ODOO_TIMEOUT` (segundos, por defecto 60). Ver `.env.example` para comentarios.

---

---

## Flujo de trabajo con IA (entorno virtual)

La carpeta `knowledge/` contiene scripts y casos de uso específicos. El flujo recomendado es:

1. Configura tu `.env` con credenciales de Odoo.
2. Abre el proyecto en tu editor de IA (Cursor, etc.).
3. Pide a la IA que cree scripts para tu proyecto en `knowledge/<tu-proyecto>/`, por ejemplo: `"Crea un script para sincronizar productos desde mi ERP"`.
4. Ejecuta los scripts desde tu entorno virtual ya activado:

   ```bash
   python knowledge/hotel-trip-agency/setup_timezone.py
   python knowledge/mi-proyecto/mi_script.py
   ```

Los datos y scripts en `knowledge/` viven dentro del repositorio, lo que permite "alimentar el cerebro" del proyecto con información y casos de uso específicos que se mantienen entre ejecuciones. Ver [knowledge/README.md](knowledge/README.md) para más detalles.

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

Tras crear y activar el entorno virtual e instalar las dependencias (`pip install -e .`), puedes usar `python main.py <comando>` o, si instalas el paquete, el binario `odoo-cli`.

| Acción              | Comando |
|---------------------|---------|
| Probar conexión     | `python main.py test-connection` |
| Listar registros    | `python main.py list res.partner --limit 5 --fields name,email` |
| Listar con dominio  | `python main.py list res.partner --domain '[["is_company","=",true]]'` |
| Salida JSON o CSV   | `python main.py list res.partner --output json` |
| Módulos instalados  | `python main.py list-modules` |
| Parámetros sistema  | `python main.py list-config` |
| Crear registro      | `python main.py create res.partner --data '{"name":"Nuevo"}'` |
| Actualizar registro | `python main.py write res.partner 1 --data '{"email":"a@b.com"}'` |
| Eliminar registro   | `python main.py unlink res.partner 1,2,3` |

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

## Tests

Tests con unittest (requiere dependencias instaladas en tu entorno virtual):

```bash
python -m unittest discover -s tests -v
```

En cada push y pull request se ejecutan los tests en CI (GitHub Actions) para Python 3.11, 3.12 y 3.13.

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

## Origen del proyecto

Este proyecto nació de la necesidad de interactuar con Odoo sin depender de su interfaz visual para configurar módulos y realizar operaciones administrativas. La idea original y el desarrollo inicial fueron realizados por [Roger Infa](https://github.com/rogerinfas) como parte de su trabajo en una organización privada, buscando una forma más eficiente y programática de gestionar instancias de Odoo mediante XML-RPC.

---

<div align="center">

*py-odoo-cli — Servicio del CLI.*

</div>
