#!/bin/bash
# Script helper para ejecutar scripts de la carpeta knowledge con Docker

set -e

if [ $# -lt 1 ]; then
    echo "Uso: ./run-knowledge.sh <ruta-del-script> [argumentos...]"
    echo ""
    echo "Ejemplos:"
    echo "  ./run-knowledge.sh knowledge/hotel-trip-agency/setup_timezone.py"
    echo "  ./run-knowledge.sh knowledge/cmline-eirl-inventory/debug_customer.py"
    exit 1
fi

SCRIPT_PATH="$1"
shift  # Remover el primer argumento, dejar el resto para pasar al script

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Error: El archivo '$SCRIPT_PATH' no existe"
    exit 1
fi

echo "🚀 Ejecutando $SCRIPT_PATH con Docker..."
docker-compose run --rm odoo-cli python "$SCRIPT_PATH" "$@"
