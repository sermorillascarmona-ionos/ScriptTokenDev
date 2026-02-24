"""
Servidor HTTP para la interfaz web.
"""
import socketserver

from ..config.settings import AppConfig
from ..services.token_service import TokenService
from .handler import TokenRequestHandler
from .template_renderer import TemplateRenderer


class TokenWebServer:
    """Servidor web para la interfaz de gestión de tokens."""

    def __init__(self, config: AppConfig):
        """
        Inicializa el servidor web.

        Args:
            config: Configuración de la aplicación
        """
        self.config = config
        self.token_service = TokenService(config)
        self.renderer = TemplateRenderer()
        self.httpd = None

    def start(self):
        """Inicia el servidor web."""
        # Configurar variables de clase en el handler
        TokenRequestHandler.token_service = self.token_service
        TokenRequestHandler.renderer = self.renderer

        print(f"🚀 Iniciando servidor web en http://0.0.0.0:{self.config.port}")
        print(f"📁 Archivos configurados:")
        print(f"   • JSON: {self.config.json_path}")
        print(f"   • JS: {self.config.js_path}")

        # Validar rutas
        warnings = self.token_service.file_manager.validate_paths()
        for warning in warnings:
            print(f"⚠️  {warning}")

        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = socketserver.TCPServer(
            ("", self.config.port),
            TokenRequestHandler
        )

        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido")
            self.stop()

    def stop(self):
        """Detiene el servidor web."""
        if self.httpd:
            self.httpd.shutdown()


