"""
Gestión de configuración de la aplicación.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class DatabaseConfig:
    """Configuración de la base de datos SQL Server."""
    host: str
    port: int
    name: str
    domain: str
    user: str
    password: str
    tds_version: str = "8.0"

    @property
    def jdbc_url(self) -> str:
        """Genera la URL JDBC para la conexión."""
        return f"jdbc:jtds:sqlserver://{self.host}:{self.port}/{self.name}"

    @property
    def connection_properties(self) -> dict:
        """Propiedades de conexión JDBC."""
        return {
            "user": self.user,
            "password": self.password,
            "domain": self.domain,
            "useNTLMv2": "true",
            "TDS": self.tds_version,
        }


@dataclass
class AppConfig:
    """Configuración general de la aplicación."""
    json_path: str
    js_path: str
    port: int
    login_url: str
    jtds_jar_path: str
    database: DatabaseConfig

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Carga la configuración desde variables de entorno."""
        db_config = DatabaseConfig(
            host=os.getenv("DB_HOST", "dev-ngcs-sqldb.dev-ngcs.lan"),
            port=int(os.getenv("DB_PORT", "1433")),
            name=os.getenv("DB_NAME", "ngcs"),
            domain=os.getenv("DB_DOMAIN", "ARSYSLAN"),
            user=os.getenv("DB_USER", "usuario"),
            password=os.getenv("DB_PASSWORD", ""),
            tds_version=os.getenv("TDS_VERSION", "8.0"),
        )

        base_path = Path(__file__).parent.parent.parent

        return cls(
            json_path=os.getenv("JSON_PATH", "/ruta/al/http-client.private.env.json"),
            js_path=os.getenv("JS_PATH", "/ruta/al/config.js"),
            port=int(os.getenv("PORT", "8000")),
            login_url=os.getenv(
                "LOGIN_URL",
                "https://com-cloudpanel-arsys-dev.com.schlund.de/loginany"
            ),
            jtds_jar_path=str(base_path / "jtds-1.3.1.jar"),
            database=db_config,
        )

    def validate(self) -> list[str]:
        """Valida la configuración y retorna una lista de errores."""
        errors = []

        if not self.database.password:
            errors.append("DB_PASSWORD no está configurado")

        if not Path(self.jtds_jar_path).exists():
            errors.append(f"Driver jTDS no encontrado: {self.jtds_jar_path}")

        return errors

