FROM python:3.13-slim

# Instalar UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración del proyecto
COPY pyproject.toml uv.lock ./

# Instalar dependencias usando UV
RUN uv sync --frozen

# Copiar el código de la aplicación
COPY . .

# Hacer el script principal ejecutable
RUN chmod +x main.py

# Establecer el PATH para incluir el entorno virtual de UV
ENV PATH="/app/.venv/bin:$PATH"

# Punto de entrada por defecto (puede ser sobrescrito)
ENTRYPOINT ["python", "main.py"]
