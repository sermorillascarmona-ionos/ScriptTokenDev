"""
Repositorio para operaciones con la base de datos.
"""
from typing import Optional
import jaydebeapi

from ..config.settings import DatabaseConfig


class TokenRepository:
    """Repositorio para obtener tokens desde SQL Server."""

    def __init__(self, config: DatabaseConfig, jtds_jar_path: str):
        """
        Inicializa el repositorio.

        Args:
            config: Configuración de la base de datos
            jtds_jar_path: Ruta al archivo JAR del driver jTDS
        """
        self.config = config
        self.jtds_jar_path = jtds_jar_path

    def get_token_by_provisioning_id(self, provisioning_id: int | str) -> tuple[str, str]:
        """
        Obtiene el token JWT más reciente para un provisioning ID.

        Args:
            provisioning_id: ID de aprovisionamiento

        Returns:
            Tupla (username, jwt_token)

        Raises:
            RuntimeError: Si no se puede conectar o no se encuentra el token
        """
        print(f"\n🔌 Conectando a SQL Server con jTDS...")
        print(f"📍 Host: {self.config.host}:{self.config.port}/{self.config.name}")

        connection = None
        cursor = None

        try:
            connection = self._create_connection()
            print(f"  ✅ Conexión exitosa!")

            cursor = connection.cursor()
            token_data = self._execute_token_query(cursor, provisioning_id)

            return self._process_token_result(token_data)

        except Exception as e:
            raise self._create_connection_error(e)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def _create_connection(self):
        """Crea la conexión JDBC a la base de datos."""
        print(f"  → Usuario: {self.config.domain}\\{self.config.user}")

        return jaydebeapi.connect(
            "net.sourceforge.jtds.jdbc.Driver",
            self.config.jdbc_url,
            self.config.connection_properties,
            self.jtds_jar_path
        )

    def _execute_token_query(self, cursor, provisioning_id: int | str):
        """Ejecuta la consulta SQL para obtener el token."""
        print(f"  📊 Consultando token para CPPR_PROVISIONINGID = {provisioning_id}")

        sql = """
        SELECT TOP 1 ACUS_USERNAME, ACUT_JWT_TOKEN
        FROM ngcs..CORE_PROVISIONED_PRODUCTS
            JOIN ngcs..ACL_USERS ON CORE_PROVISIONED_PRODUCTS.CPPR_ID = ACL_USERS.ACUS_PROVISIONEDPRODUCTID
            LEFT JOIN ngcs..ACL_USER_TOKENS ON ACL_USERS.ACUS_ID = ACL_USER_TOKENS.ACUT_USERID
        WHERE CPPR_PROVISIONINGID = ?
        ORDER BY ACL_USER_TOKENS.ACUT_LAST_RESFRESH DESC
        """

        cursor.execute(sql, (provisioning_id,))
        return cursor.fetchone()

    def _process_token_result(self, token_data) -> tuple[str, str]:
        """Procesa el resultado de la consulta."""
        if not token_data:
            raise RuntimeError(
                f"No se encontró ningún token para el provisioning ID especificado"
            )

        username, jwt_token = token_data
        print(f"  ✅ Token encontrado para usuario: {username}")

        if not jwt_token:
            raise RuntimeError(f"El usuario {username} no tiene ACUT_JWT_TOKEN")

        jwt_token = str(jwt_token)
        if not jwt_token.startswith("Bearer "):
            jwt_token = "Bearer " + jwt_token

        return username, jwt_token

    def _create_connection_error(self, original_error: Exception) -> RuntimeError:
        """Crea un mensaje de error detallado para problemas de conexión."""
        error_msg = (
            f"\n{'='*60}\n"
            f"❌ ERROR: No se pudo conectar a SQL Server\n"
            f"{'='*60}\n\n"
            f"🔧 Configuración:\n"
            f"   • Host: {self.config.host}:{self.config.port}\n"
            f"   • Database: {self.config.name}\n"
            f"   • Usuario: {self.config.domain}\\{self.config.user}\n\n"
            f"📋 Error:\n   {str(original_error)}\n\n"
            f"💡 Verifica:\n"
            f"   1. VPN conectada\n"
            f"   2. Credenciales correctas en .env\n"
            f"   3. Permisos del usuario en la base de datos\n"
            f"{'='*60}\n"
        )
        return RuntimeError(error_msg)

