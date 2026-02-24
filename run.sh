#!/bin/bash
# Script de utilidades para Token Helper

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function print_header() {
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}🔐 Token Helper - Utilities${NC}"
    echo -e "${GREEN}================================${NC}\n"
}

function check_dependencies() {
    echo -e "${YELLOW}Verificando dependencias...${NC}"

    # Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 no está instalado${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Python 3: $(python3 --version)${NC}"

    # pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}❌ pip3 no está instalado${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ pip3 instalado${NC}"

    # Archivo .env
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
        echo -e "   Crea uno basándote en .env.example"
    else
        echo -e "${GREEN}✅ Archivo .env encontrado${NC}"
    fi

    # Driver jTDS
    if [ ! -f jtds-1.3.1.jar ]; then
        echo -e "${RED}❌ jtds-1.3.1.jar no encontrado${NC}"
        echo -e "   Descárgalo desde: https://sourceforge.net/projects/jtds/files/jtds/1.3.1/"
        exit 1
    fi
    echo -e "${GREEN}✅ Driver jTDS encontrado${NC}"

    echo ""
}

function install_deps() {
    echo -e "${YELLOW}Instalando dependencias Python...${NC}"
    pip3 install -r requirements.txt
    echo -e "${GREEN}✅ Dependencias instaladas${NC}\n"
}

function run_web() {
    echo -e "${YELLOW}Iniciando servidor web...${NC}"
    python3 main.py
}

function run_auto() {
    if [ -z "$1" ]; then
        echo -e "${RED}❌ Falta el provisioning ID${NC}"
        echo "   Uso: ./run.sh auto <provisioning_id>"
        exit 1
    fi

    echo -e "${YELLOW}Ejecutando modo automático...${NC}"
    python3 main.py --auto "$1"
}

function show_help() {
    echo "Uso: ./run.sh [comando] [argumentos]"
    echo ""
    echo "Comandos disponibles:"
    echo "  check       Verifica dependencias y configuración"
    echo "  install     Instala dependencias de Python"
    echo "  web         Inicia el servidor web (por defecto)"
    echo "  auto <id>   Ejecuta modo automático con el provisioning ID"
    echo "  help        Muestra esta ayuda"
    echo ""
}

# Main
print_header

case "${1:-web}" in
    check)
        check_dependencies
        ;;
    install)
        check_dependencies
        install_deps
        ;;
    web)
        check_dependencies
        run_web
        ;;
    auto)
        check_dependencies
        run_auto "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Comando desconocido: $1${NC}\n"
        show_help
        exit 1
        ;;
esac

