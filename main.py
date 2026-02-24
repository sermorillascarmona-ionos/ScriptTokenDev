#!/usr/bin/env python3
"""
Token Helper - Gestor de Tokens JWT para desarrollo
====================================================

Script de entrada principal. Delega la ejecución a la aplicación modular.

Uso:
    python3 main.py                    # Inicia el servidor web
    python3 main.py --auto <prov_id>   # Modo automático
"""

if __name__ == "__main__":
    from src.main import main
    main()

