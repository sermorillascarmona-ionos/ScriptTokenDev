"""
Aplicación principal - Punto de entrada.
"""
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from src.config.settings import AppConfig
from src.services.token_service import TokenService
from src.web.server import TokenWebServer


class Application:
    """Aplicación principal de Token Helper."""

    def __init__(self):
        """Inicializa la aplicación."""
        self._load_environment()
        self.config = self._load_config()
        self.token_service = TokenService(self.config)

    def _load_environment(self):
        """Carga las variables de entorno desde .env"""
        env_path = Path(__file__).parent.parent / '.env'

        if env_path.exists():
            load_dotenv(env_path)
            print("✅ Configuración cargada desde .env")
        else:
            print("⚠️  Archivo .env no encontrado, usando valores por defecto")
            print(f"   Copia .env.example a .env y configura tus credenciales")

    def _load_config(self) -> AppConfig:
        """Carga y valida la configuración."""
        config = AppConfig.from_env()

        errors = config.validate()
        if errors:
            print("❌ Errores de configuración:")
            for error in errors:
                print(f"   • {error}")

            # Solo salir si hay errores críticos
            if "jTDS no encontrado" in str(errors):
                print("\n💡 Descarga jTDS desde:")
                print("   https://sourceforge.net/projects/jtds/files/jtds/1.3.1/")
                sys.exit(1)

        return config

    def run_web_server(self):
        """Inicia el servidor web."""
        server = TokenWebServer(self.config)
        server.start()

    def run_auto_mode(self, provisioning_id: str):
        """
        Ejecuta el modo automático.

        Args:
            provisioning_id: ID de aprovisionamiento
        """
        try:
            self.token_service.auto_update(provisioning_id)
        except Exception as e:
            print(f"❌ Error en modo automático: {e}")
            sys.exit(1)

    def run(self):
        """Ejecuta la aplicación según los argumentos de línea de comandos."""
        if len(sys.argv) > 1 and sys.argv[1] == "--auto":
            provisioning_id = sys.argv[2] if len(sys.argv) > 2 else None

            if not provisioning_id:
                print("❌ Falta provisioning ID")
                print("   Uso: python main.py --auto <provisioning_id>")
                sys.exit(1)

            self.run_auto_mode(provisioning_id)
        else:
            self.run_web_server()


def main():
    """Punto de entrada principal."""
    try:
        app = Application()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Hasta luego!")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

