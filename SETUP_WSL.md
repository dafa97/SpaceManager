# Configuración del Entorno en WSL

## Opción Recomendada: Desarrollo en WSL

Ya que tienes Ubuntu 20.04 en WSL2, es mejor trabajar completamente dentro de WSL para evitar problemas de compatibilidad.

## Pasos de Configuración

### 1. Acceder a WSL

```bash
wsl
```

### 2. Actualizar el Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Instalar Docker en WSL

```bash
# Instalar dependencias
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Agregar la clave GPG de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Agregar el repositorio de Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Agregar tu usuario al grupo docker (para no usar sudo)
sudo usermod -aG docker $USER

# Iniciar el servicio Docker
sudo service docker start
```

### 4. Instalar Python 3.12

```bash
# Agregar repositorio deadsnakes
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Instalar Python 3.12
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Verificar instalación
python3.12 --version
```

### 5. Instalar Poetry

```bash
curl -sSL https://install.python-poetry.org | python3.12 -

# Agregar Poetry al PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verificar instalación
poetry --version
```

### 6. Copiar el Proyecto a WSL

Tienes dos opciones:

#### Opción A: Trabajar directamente en el sistema de archivos de WSL (Recomendado)

```bash
# Crear directorio en WSL
mkdir -p ~/projects
cd ~/projects

# Copiar desde Windows
cp -r /mnt/c/Users/User/Desktop/Python/SpaceManager .
cd SpaceManager
```

#### Opción B: Trabajar desde Windows pero ejecutar en WSL

Puedes acceder a tus archivos de Windows desde WSL en `/mnt/c/`:

```bash
cd /mnt/c/Users/User/Desktop/Python/SpaceManager
```

**Nota**: La Opción A es más rápida para operaciones de I/O.

### 7. Iniciar el Proyecto

```bash
# Navegar al directorio del backend
cd backend

# Instalar dependencias
poetry install

# Copiar variables de entorno
cp .env.example .env

# Volver al directorio raíz
cd ..

# Iniciar servicios con Docker Compose
docker compose up -d

# Ver logs
docker compose logs -f
```

### 8. Crear Migración Inicial

```bash
cd backend

# Crear migración
poetry run alembic revision --autogenerate -m "initial schema"

# Aplicar migración
poetry run alembic upgrade head
```

### 9. Acceder a la API

Desde tu navegador en Windows, visita:
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Comandos Útiles

### Docker

```bash
# Ver servicios corriendo
docker compose ps

# Ver logs
docker compose logs -f backend

# Detener servicios
docker compose down

# Reiniciar un servicio
docker compose restart backend

# Reconstruir imágenes
docker compose build
```

### Poetry

```bash
# Activar entorno virtual
poetry shell

# Instalar nueva dependencia
poetry add nombre-paquete

# Actualizar dependencias
poetry update
```

### Desarrollo

```bash
# Ejecutar servidor de desarrollo (sin Docker)
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0

# Ejecutar worker de Dramatiq
poetry run dramatiq app.workers.tasks

# Ejecutar tests
poetry run pytest
```

## Solución de Problemas

### Docker no inicia

```bash
# Verificar estado
sudo service docker status

# Iniciar Docker
sudo service docker start

# Si sigue sin funcionar, reiniciar WSL desde PowerShell (Windows):
# wsl --shutdown
# wsl
```

### Permisos de Docker

```bash
# Si obtienes errores de permisos
sudo usermod -aG docker $USER

# Cerrar y reabrir WSL para aplicar cambios
exit
# Luego: wsl
```

### Puerto 8000 ya en uso

```bash
# Ver qué está usando el puerto
sudo lsof -i :8000

# O cambiar el puerto en docker-compose.yml
# ports:
#   - "8001:8000"
```

## Alternativa: Docker Desktop para Windows

Si prefieres no usar Docker en WSL, puedes instalar Docker Desktop:

1. Descargar: https://www.docker.com/products/docker-desktop
2. Instalar y reiniciar
3. Habilitar integración con WSL2 en la configuración
4. Usar comandos desde PowerShell o WSL

## Próximos Pasos

Una vez que todo esté funcionando:

1. ✅ Probar endpoints en http://localhost:8000/docs
2. ✅ Registrar una organización
3. ✅ Crear espacios y reservas
4. ✅ Verificar aislamiento multi-tenant
5. 🚀 Comenzar desarrollo del frontend
