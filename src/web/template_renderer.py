"""
Motor de renderizado de templates HTML.
"""
from pathlib import Path
from typing import Dict, Any


class TemplateRenderer:
    """Renderizador simple de templates HTML."""

    def __init__(self, templates_dir: str = None):
        """
        Inicializa el renderizador.

        Args:
            templates_dir: Directorio donde se encuentran los templates
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "templates"

        self.templates_dir = Path(templates_dir)

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Renderiza un template con el contexto proporcionado.

        Args:
            template_name: Nombre del archivo de template
            context: Diccionario con variables para reemplazar

        Returns:
            HTML renderizado
        """
        template_path = self.templates_dir / template_name

        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()

        # Reemplazar variables simples {{ variable }}
        for key, value in context.items():
            placeholder = f"{{{{ {key} }}}}"
            template = template.replace(placeholder, str(value))

        return template

    def escape_html(self, text: str) -> str:
        """Escapa caracteres especiales de HTML."""
        return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("{", "&#123;")
            .replace("}", "&#125;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))

