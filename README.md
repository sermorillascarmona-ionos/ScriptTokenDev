## Token Helper - Requisitos e instalación

### Requisitos previos
- Python 3.8 o superior
- Acceso a la VPN corporativa (para conexión a SQL Server)
- Acceso a los archivos de configuración y credenciales

### Instalación de dependencias (Ubuntu y Linux Mint)

#### 1. Instalar Python y pip

Ubuntu y Mint ya incluyen Python 3, pero asegúrate de tenerlo actualizado:

```bash
sudo apt update
sudo apt install python3 python3-pip
```

#### 2. Instalar dependencias Python

```bash
pip3 install jaydebeapi python-dotenv
```

#### 3. Descargar el driver jTDS

Descarga el archivo `jtds-1.3.1.jar` desde:
https://sourceforge.net/projects/jtds/files/jtds/1.3.1/

Colócalo en la misma carpeta que `token_helper.py`.

#### 4. Configurar el archivo `.env`

Copia el ejemplo y edítalo con tus credenciales:

```bash
cp .env.example .env
nano .env
```

Variables principales:
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_DOMAIN`, `DB_USER`, `DB_PASSWORD`
- `JSON_PATH`, `JS_PATH`, `PORT`, `LOGIN_URL`

#### 5. Ejecutar el script

```bash
python3 token_helper.py
```

Accede a la interfaz web en: http://localhost:8000 (o el puerto configurado)

### Notas adicionales
- **VPN**: Debes estar conectado a la VPN para acceder a la base de datos SQL Server.
- **Permisos**: Asegúrate de tener permisos de lectura/escritura en los archivos de configuración.
- **Soporte**: Si falta alguna dependencia, instálala con `pip3 install <paquete>`.

---

### Ejemplo de archivo `.env`:

```
DB_HOST=dev-ngcs-sqldb.dev-ngcs.lan
DB_PORT=1433
DB_NAME=ngcs
DB_DOMAIN=ARSYSLAN
DB_USER=usuario
DB_PASSWORD=tu_password
JSON_PATH=/ruta/al/http-client.private.env.json
JS_PATH=/ruta/al/config.js
PORT=8000
LOGIN_URL=https://com-cloudpanel-ionos-dev.com.schlund.de:36888/loginany
TDS_VERSION=8.0
```

---

**Desarrollado por el equipo ArsysLab**
