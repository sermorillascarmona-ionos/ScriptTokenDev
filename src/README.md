# Documentación de Módulos - src/

## Estructura de Módulos

### config/
Módulo de configuración de la aplicación.

#### settings.py
- **DatabaseConfig**: Configuración de SQL Server
  - `jdbc_url`: Propiedad calculada para URL JDBC
  - `connection_properties`: Propiedades de conexión
  
- **AppConfig**: Configuración general
  - `from_env()`: Carga desde variables de entorno
  - `validate()`: Valida configuración

### services/
Módulo de lógica de negocio.

#### database.py
- **TokenRepository**: Repositorio para tokens en SQL Server
  - `get_token_by_provisioning_id()`: Obtiene token de la DB
  - Maneja conexiones JDBC con jTDS
  - Gestión de errores detallada

#### file_manager.py
- **TokenFileManager**: Gestor de archivos de configuración
  - `get_current_token()`: Lee token actual
  - `update_token()`: Actualiza JSON y JS
  - `validate_paths()`: Valida que existan los archivos

#### auth_service.py
- **LoginService**: Servicio de autenticación HTTP
  - `perform_login()`: POST al endpoint de login
  - Manejo de SSL
  - Truncamiento de respuestas largas

#### token_service.py
- **TokenService**: Coordinador principal (Facade)
  - Orquesta todos los servicios
  - `get_current_token()`: Obtiene token actual
  - `update_token_manually()`: Actualización manual
  - `get_token_from_database()`: Obtiene de DB
  - `update_token_from_database()`: Obtiene y actualiza
  - `perform_login()`: Delega a LoginService
  - `auto_update()`: Modo automático completo

### web/
Módulo de interfaz web.

#### server.py
- **TokenWebServer**: Servidor HTTP principal
  - `start()`: Inicia servidor
  - `stop()`: Detiene servidor
  - Configuración de TCPServer

#### handler.py
- **TokenRequestHandler**: Manejador de peticiones HTTP
  - `do_GET()`: Renderiza página principal
  - `do_POST()`: Maneja acciones
  - `_handle_update_files()`: Actualización manual
  - `_handle_db_token()`: Obtención desde DB
  - `_handle_login_demo()`: Login demo

#### template_renderer.py
- **TemplateRenderer**: Motor de templates
  - `render()`: Renderiza template con contexto
  - `escape_html()`: Escapa HTML para seguridad

#### templates/index.html
- Template HTML principal
- Variables de template: `{{ variable }}`
- Estilos CSS incluidos
- JavaScript para animaciones

### cli/
Módulo de interfaz CLI (futuro).

### main.py
Punto de entrada de la aplicación.

- **Application**: Clase principal
  - `_load_environment()`: Carga .env
  - `_load_config()`: Carga y valida config
  - `run_web_server()`: Inicia servidor web
  - `run_auto_mode()`: Ejecuta modo automático
  - `run()`: Decide flujo según argumentos

- **main()**: Función de entrada
  - Manejo de excepciones global
  - KeyboardInterrupt
  - Errores fatales

## Dependencias entre Módulos

```
main.py
  └─> config/settings.py (AppConfig)
      └─> services/token_service.py (TokenService)
          ├─> services/database.py (TokenRepository)
          ├─> services/file_manager.py (TokenFileManager)
          └─> services/auth_service.py (LoginService)
      └─> web/server.py (TokenWebServer)
          ├─> web/handler.py (TokenRequestHandler)
          └─> web/template_renderer.py (TemplateRenderer)
              └─> web/templates/index.html
```

## Importación de Módulos

### Desde fuera de src/
```python
from src.config.settings import AppConfig
from src.services.token_service import TokenService
from src.web.server import TokenWebServer
```

### Desde dentro de src/ (relativo)
```python
from ..config.settings import AppConfig
from .database import TokenRepository
```

## Testing

### Ejemplo de test unitario
```python
import unittest
from src.config.settings import AppConfig, DatabaseConfig

class TestDatabaseConfig(unittest.TestCase):
    def test_jdbc_url(self):
        config = DatabaseConfig(
            host="localhost",
            port=1433,
            name="test",
            domain="TEST",
            user="user",
            password="pass"
        )
        expected = "jdbc:jtds:sqlserver://localhost:1433/test"
        self.assertEqual(config.jdbc_url, expected)
```

## Buenas Prácticas

### 1. Inyección de Dependencias
```python
# ✅ BIEN
class MyService:
    def __init__(self, config: AppConfig):
        self.config = config

# ❌ MAL
class MyService:
    def __init__(self):
        self.config = AppConfig.from_env()  # Acoplamiento
```

### 2. Type Hints
```python
# ✅ BIEN
def get_token(self, id: int | str) -> str:
    pass

# ❌ MAL
def get_token(self, id):  # Sin tipos
    pass
```

### 3. Manejo de Errores
```python
# ✅ BIEN
try:
    token = self.repository.get_token(id)
except Exception as e:
    raise RuntimeError(f"Error específico: {e}")

# ❌ MAL
token = self.repository.get_token(id)  # Sin manejo
```

### 4. Validación
```python
# ✅ BIEN
def update_token(self, token: str):
    if not token:
        raise ValueError("Token no puede estar vacío")
    # ...

# ❌ MAL
def update_token(self, token):
    # ... sin validación
```

## Extensión de Funcionalidad

### Agregar nuevo servicio
```python
# 1. Crear archivo: src/services/new_service.py
class NewService:
    def __init__(self, config):
        self.config = config
    
    def do_something(self):
        pass

# 2. Agregar a TokenService
from .new_service import NewService

class TokenService:
    def __init__(self, config):
        # ...
        self.new_service = NewService(config)
```

### Agregar nueva ruta web
```python
# En handler.py
def do_POST(self):
    # ...
    elif action == "new_action":
        self._handle_new_action(data)

def _handle_new_action(self, data):
    # Implementación
    pass
```

## Configuración de IDE

### PyCharm/IntelliJ
1. Marcar `src/` como Sources Root
2. Python interpreter: Python 3.8+
3. Instalar dependencias desde requirements.txt

### VS Code
```json
{
  "python.analysis.extraPaths": ["./src"],
  "python.autoComplete.extraPaths": ["./src"]
}
```

---

Para más información, consulta:
- `ARCHITECTURE.md` - Arquitectura completa
- `QUICKSTART.md` - Guía de inicio rápido

