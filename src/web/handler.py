"""
Manejador HTTP para el servidor web.
"""
import http.server
import urllib.parse
from typing import Optional

from ..services.token_service import TokenService
from .template_renderer import TemplateRenderer


class TokenRequestHandler(http.server.BaseHTTPRequestHandler):
    """Manejador de peticiones HTTP para la interfaz web."""

    # Variables de clase compartidas
    token_service: TokenService = None
    renderer: TemplateRenderer = None

    def __init__(self, *args, **kwargs):
        """Inicializa el manejador."""
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Maneja peticiones GET."""
        self.render_page()

    def do_POST(self):
        """Maneja peticiones POST."""
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        data = urllib.parse.parse_qs(body)

        action = (data.get("action", [""])[0] or "").strip()

        if action == "update_files":
            self._handle_update_files(data)
        elif action == "db_token":
            self._handle_db_token(data)
        elif action == "login_demo":
            self._handle_login_demo(data)
        else:
            self.render_page(error="Acción desconocida.")

    def render_page(
        self,
        message: str = "",
        error: str = "",
        current_token_override: Optional[str] = None,
        db_result: str = "",
        login_result: str = "",
        token_from_db: bool = False,
    ):
        """
        Renderiza la página principal.

        Args:
            message: Mensaje de éxito a mostrar
            error: Mensaje de error a mostrar
            current_token_override: Token a mostrar (si no se especifica, se obtiene del archivo)
            db_result: Resultado de la consulta a la base de datos
            login_result: Resultado del login
            token_from_db: Si el token fue obtenido de la base de datos
        """
        current_token = (
            current_token_override
            if current_token_override is not None
            else self.token_service.get_current_token()
        )

        # Construir bloques HTML
        msg_html = self._build_message_block(message, error)
        db_html = self._build_db_result_block(db_result)
        login_html = self._build_login_result_block(login_result)
        token_animation_class = "token-updated" if token_from_db else ""

        # Contexto para el template
        context = {
            "msg_block": msg_html,
            "current_token": current_token,
            "json_path": self.token_service.config.json_path,
            "js_path": self.token_service.config.js_path,
            "db_result_block": db_html,
            "login_result_block": login_html,
            "token_animation_class": token_animation_class,
        }

        html = self.renderer.render("index.html", context)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _build_message_block(self, message: str, error: str) -> str:
        """Construye el bloque de mensajes."""
        msg_html = ""
        if message:
            msg_html += f'<div class="alert alert-success">✅ {message}</div>'
        if error:
            msg_html += f'<div class="alert alert-error">❌ {error}</div>'
        return msg_html

    def _build_db_result_block(self, db_result: str) -> str:
        """Construye el bloque de resultados de la base de datos."""
        if not db_result:
            return ""

        escaped_result = self.renderer.escape_html(db_result)
        return (
            f"<h3 style='margin-top: 20px; color: #495057;'>📊 Resultado:</h3>"
            f"<pre>{escaped_result}</pre>"
        )

    def _build_login_result_block(self, login_result: str) -> str:
        """Construye el bloque de resultados del login."""
        if not login_result:
            return ""

        escaped_result = self.renderer.escape_html(login_result)
        return (
            f"<h3 style='margin-top: 20px; color: #495057;'>📋 Respuesta del servidor:</h3>"
            f"<pre>{escaped_result}</pre>"
        )

    def _handle_update_files(self, data: dict):
        """Maneja la actualización manual del token."""
        token_list = data.get("token", [])
        if not token_list:
            self.render_page(error="El token no puede estar vacío.")
            return

        new_token = token_list[0].strip()
        if not new_token:
            self.render_page(error="El token no puede estar vacío.")
            return

        try:
            self.token_service.update_token_manually(new_token)
            self.render_page(
                message="Token actualizado correctamente en ambos archivos.",
                current_token_override=new_token,
            )
        except Exception as e:
            self.render_page(error=f"Error al actualizar: {e}")

    def _handle_db_token(self, data: dict):
        """Maneja la obtención del token desde la base de datos."""
        prov = (data.get("provisioningId", [""])[0] or "").strip()
        if not prov:
            self.render_page(
                error="ProvisioningId no puede estar vacío para sacar el token de la DB."
            )
            return

        try:
            # Intentar convertir a int si es posible
            try:
                prov_val = int(prov)
            except ValueError:
                prov_val = prov

            db_token = self.token_service.update_token_from_database(prov_val)
            db_info = f"CPPR_PROVISIONINGID = {prov}\n\nToken devuelto por la DB:\n{db_token}"

            self.render_page(
                message="Token obtenido desde la DB y actualizado en los archivos.",
                current_token_override=db_token,
                db_result=db_info,
                token_from_db=True,
            )
        except Exception as e:
            self.render_page(error=f"Error obteniendo token desde DB: {e}")

    def _handle_login_demo(self, data: dict):
        """Maneja el login demo."""
        prov = (data.get("provisioningId", [""])[0] or "").strip()
        section = (data.get("section", ["none"])[0] or "none").strip()
        locale = (data.get("locale", ["af_AF"])[0] or "af_AF").strip()

        if not prov:
            self.render_page(
                error="ProvisioningId no puede estar vacío para el login demo."
            )
            return

        try:
            status, headers, body = self.token_service.perform_login(prov, section, locale)

            headers_txt = "\n".join(f"{k}: {v}" for k, v in headers.items())
            result = f"STATUS: {status}\n\nHEADERS:\n{headers_txt}\n\nBODY:\n{body}"

            self.render_page(
                message="Login demo ejecutado. Revisa el resultado abajo.",
                login_result=result,
            )
        except Exception as e:
            self.render_page(error=str(e))

