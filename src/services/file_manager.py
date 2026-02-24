"""
Servicio para gestión de archivos de tokens.
"""
import json
import re
from pathlib import Path
from typing import Optional


class TokenFileManager:
    """Gestor de archivos de configuración de tokens."""

    def __init__(self, json_path: str, js_path: str):
        """
        Inicializa el gestor de archivos.

        Args:
            json_path: Ruta al archivo JSON de configuración
            js_path: Ruta al archivo JavaScript de configuración
        """
        self.json_path = Path(json_path)
        self.js_path = Path(js_path)

    def get_current_token(self) -> str:
        """
        Obtiene el token actual de los archivos de configuración.
        Intenta primero desde JSON, luego desde JS.

        Returns:
            Token actual o cadena vacía si no se encuentra
        """
        token = self._get_token_from_json()
        if token:
            return token

        return self._get_token_from_js()

    def update_token(self, new_token: str) -> None:
        """
        Actualiza el token en ambos archivos de configuración.

        Args:
            new_token: Nuevo token JWT a guardar

        Raises:
            RuntimeError: Si no se puede actualizar algún archivo
        """
        self._update_json_token(new_token)
        self._update_js_token(new_token)

    def _get_token_from_json(self) -> str:
        """Obtiene el token desde el archivo JSON."""
        try:
            if not self.json_path.exists():
                return ""

            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return data.get("dev", {}).get("panel_token", "")
        except Exception:
            return ""

    def _get_token_from_js(self) -> str:
        """Obtiene el token desde el archivo JavaScript."""
        try:
            if not self.js_path.exists():
                return ""

            with open(self.js_path, "r", encoding="utf-8") as f:
                content = f.read()

            match = re.search(r'const\s+auth\s*=\s*"(.*?)";', content, re.DOTALL)
            return match.group(1) if match else ""
        except Exception:
            return ""

    def _update_json_token(self, new_token: str) -> None:
        """Actualiza el token en el archivo JSON."""
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "dev" not in data:
            data["dev"] = {}

        data["dev"]["panel_token"] = new_token

        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _update_js_token(self, new_token: str) -> None:
        """Actualiza el token en el archivo JavaScript."""
        with open(self.js_path, "r", encoding="utf-8") as f:
            content = f.read()

        pattern = r'(^\s*(?:export\s+)?(?:const|let|var)\s+auth\s*=\s*)(["\']).*?\2\s*;?\s*$'
        new_content, num_replacements = re.subn(
            pattern,
            lambda m: f'{m.group(1)}"{new_token}";',
            content,
            count=1,
            flags=re.MULTILINE | re.DOTALL,
        )

        if num_replacements == 0:
            raise RuntimeError(
                'No se encontró una asignación a "auth" en config.js '
                '(const/let/var auth = "...")'
            )

        with open(self.js_path, "w", encoding="utf-8") as f:
            f.write(new_content)

    def validate_paths(self) -> list[str]:
        """
        Valida que los archivos existan.

        Returns:
            Lista de mensajes de advertencia
        """
        warnings = []

        if not self.json_path.exists():
            warnings.append(f"No existe el archivo JSON: {self.json_path}")

        if not self.js_path.exists():
            warnings.append(f"No existe el archivo JS: {self.js_path}")

        return warnings

