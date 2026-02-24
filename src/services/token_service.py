"""
Servicio de aplicación que coordina las operaciones.
"""
from ..config.settings import AppConfig
from .database import TokenRepository
from .file_manager import TokenFileManager
from .auth_service import LoginService


class TokenService:
    """Servicio principal para gestión de tokens."""

    def __init__(self, config: AppConfig):
        """
        Inicializa el servicio con la configuración.

        Args:
            config: Configuración de la aplicación
        """
        self.config = config
        self.repository = TokenRepository(config.database, config.jtds_jar_path)
        self.file_manager = TokenFileManager(config.json_path, config.js_path)
        self.auth_service = LoginService(config.login_url)

    def get_current_token(self) -> str:
        """Obtiene el token actual de los archivos de configuración."""
        return self.file_manager.get_current_token()

    def update_token_manually(self, new_token: str) -> None:
        """
        Actualiza el token manualmente en los archivos.

        Args:
            new_token: Nuevo token JWT
        """
        self.file_manager.update_token(new_token)

    def get_token_from_database(self, provisioning_id: int | str) -> str:
        """
        Obtiene el token desde la base de datos.

        Args:
            provisioning_id: ID de aprovisionamiento

        Returns:
            Token JWT con prefijo Bearer
        """
        username, token = self.repository.get_token_by_provisioning_id(provisioning_id)
        return token

    def update_token_from_database(self, provisioning_id: int | str) -> str:
        """
        Obtiene el token desde la base de datos y lo actualiza en los archivos.

        Args:
            provisioning_id: ID de aprovisionamiento

        Returns:
            Token obtenido
        """
        token = self.get_token_from_database(provisioning_id)
        self.file_manager.update_token(token)
        return token

    def perform_login(
        self,
        provisioning_id: str,
        section: str = "none",
        locale: str = "af_AF"
    ) -> tuple[int, dict, str]:
        """
        Realiza login en el panel.

        Args:
            provisioning_id: ID de aprovisionamiento
            section: Sección del panel
            locale: Configuración regional

        Returns:
            Tupla (status, headers, body)
        """
        return self.auth_service.perform_login(provisioning_id, section, locale)

    def auto_update(self, provisioning_id: int | str) -> str:
        """
        Modo automático: hace login y obtiene el token de la BD.

        Args:
            provisioning_id: ID de aprovisionamiento

        Returns:
            Token actualizado
        """
        print("🤖 Modo automático activado")
        print(f"📌 Provisioning ID: {provisioning_id}")

        # Realizar login
        self.perform_login(str(provisioning_id))

        # Obtener y actualizar token
        import time
        time.sleep(2)
        token = self.update_token_from_database(provisioning_id)

        print("✅ Token obtenido y actualizado correctamente")
        return token


