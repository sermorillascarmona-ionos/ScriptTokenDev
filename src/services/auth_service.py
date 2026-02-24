"""
Servicio para autenticación mediante login.
"""
import urllib.request
import urllib.parse
import ssl
from typing import Optional


class LoginService:
    """Servicio para realizar login en el panel."""

    def __init__(self, login_url: str):
        """
        Inicializa el servicio de login.

        Args:
            login_url: URL del endpoint de login
        """
        self.login_url = login_url
        self.ssl_context = ssl._create_unverified_context()

    def perform_login(
        self,
        provisioning_id: str,
        section: str = "none",
        locale: str = "af_AF"
    ) -> tuple[int, dict, str]:
        """
        Realiza un POST al formulario de login.

        Args:
            provisioning_id: ID de aprovisionamiento
            section: Sección del panel a cargar
            locale: Configuración regional

        Returns:
            Tupla (status_code, headers, body)

        Raises:
            RuntimeError: Si falla la petición
        """
        data = {
            "provisioningId": provisioning_id,
            "dcdjwt": "",
            "section": section,
            "debug": "1",
            "hmr": "none",
            "console": "none",
            "locale": locale,
        }

        encoded = urllib.parse.urlencode(data).encode("utf-8")
        request = urllib.request.Request(self.login_url, data=encoded, method="POST")
        request.add_header("User-Agent", "Mozilla/5.0 (TokenUpdaterBot)")
        request.add_header("Content-Type", "application/x-www-form-urlencoded")

        try:
            with urllib.request.urlopen(request, context=self.ssl_context) as response:
                body = response.read().decode("utf-8", errors="replace")
                status = response.status
                headers = dict(response.getheaders())

            # Truncar body si es muy largo
            max_len = 2000
            if len(body) > max_len:
                body = body[:max_len] + "\n\n...[truncado]..."

            return status, headers, body

        except Exception as e:
            raise RuntimeError(f"Error al hacer login: {e}")

