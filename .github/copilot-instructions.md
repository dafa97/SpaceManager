## Instrucciones rápidas para agentes (SpaceManager)

Este proyecto es un backend FastAPI multi-tenant (schema-based) con un frontend Next.js. Estas notas se enfocan en lo que un agente IA necesita saber para ser productivo aquí.

- Arquitectura general
  - `backend/` contiene la API (FastAPI + SQLAlchemy async) y workers (Dramatiq + Redis).
  - Multi-tenancy basado en *PostgreSQL schemas*: las entidades públicas (organizations, users) viven en `public` y los datos por tenant (spaces, reservations) en schemas `tenant_<slug>`.
  - `frontend/` es una app Next.js conectada a la API; no es necesario editar para tareas backend.

- Puntos de entrada y archivos clave
  - `backend/app/main.py` — configuración de FastAPI, CORS y routers.
  - `backend/app/middleware/tenant.py` — extrae `tenant_id` del JWT y expone `request.state.schema_name`/`tenant_id`.
  - `backend/app/api/dependencies/auth.py` — decodifica JWT y devuelve `User` (inyecta `tenant_id` en `user.tenant_id`).
  - `backend/app/api/routes/*.py` — implementaciones de endpoints (ejemplo: `spaces.py` usa `set_tenant_schema` para ejecutar `SET search_path`).
  - `backend/app/core/database.py` — engine async y `AsyncSessionLocal` (use `get_db` como dependencia).
  - `backend/pyproject.toml` — dependencias y herramientas (Poetry, Black, Ruff, pytest).
  - `backend/README.md` — comandos de desarrollo y despliegue (migraciones, worker, docker-compose).

- Patrón y convenciones importantes (no genéricos)
  - Async por defecto: usa `AsyncSession`, `async` endpoints, y `asyncpg`-compatible SQLAlchemy 2.0.
  - Multi-tenant: no assumes que las consultas automáticas cambian de schema; comúnmente se llama a `SET search_path TO <schema>, public` (ver helper `set_tenant_schema` en `spaces.py`) o se confía en middleware que resuelve `request.state`.
  - JWT payload: contiene `sub` (user id) y `tenant_id`. Las dependencias de auth usan esto para validar usuario y asignar `user.tenant_id`.
  - Pydantic v2: los esquemas usan `model_dump()` para serializar/extraer dicts para modelos SQLAlchemy.
  - Modelos: `User` está en `public` (ver `__table_args__ = {"schema": "public"}`), mientras que modelos como `Space` no declaran schema (se espera que el search_path apunte al schema del tenant).

- Comandos útiles (desarrollo local)
  - Instalar deps: `cd backend && poetry install`
  - Levantar servicios de infraestructura: `docker-compose up -d postgres redis`
  - Migraciones: `poetry run alembic revision --autogenerate -m "msg"` y `poetry run alembic upgrade head`
  - Server dev: `poetry run uvicorn app.main:app --reload`
  - Worker: `poetry run dramatiq app.workers.tasks`
  - Tests: `poetry run pytest` (pytest-asyncio está presente)

- Ejemplos concretos que un agente puede usar
  - Para crear un nuevo endpoint que consulte datos tenant-específicos: 1) usar la dependencia `db: AsyncSession = Depends(get_db)`, 2) resolver `current_user = Depends(get_current_active_user)`, 3) ejecutar `await db.execute(text("SET search_path TO <schema>, public"))` o invocar helper `set_tenant_schema(db, current_user)` antes de consultas.
  - Para validar auth: revisar `backend/app/api/dependencies/auth.py` — replicar la decodificación JWT (jose) y la verificación que lanza `HTTPException` con `WWW-Authenticate` cuando corresponde.

- Errores/advertencias específicas
  - No cambiar la forma de inyectar `tenant_id` sin propagar el cambio a middleware + dependencias; muchas partes del código asumen la presencia de `user.tenant_id` o `request.state.schema_name`.
  - Evitar operaciones sincronas de I/O en endpoints async; usa las utilidades async existentes (DB y Dramatiq para background tasks).

- Qué buscar cuando se modifica código
  - Si tocas modelos o migraciones, actualiza `alembic/versions/` y prueba `poetry run alembic upgrade head` en un entorno con Postgres.
  - Si añades nuevos env vars, agrégalos a `.env.example` y a `backend/README.md` si aplican.

Si algo no está claro o necesitas más ejemplos (migraciones, tests unitarios concretos, o el flujo completo de registro de tenant), dime qué sección quieres ampliar y lo desarrollo.

### Ejemplos prácticos (copiar/usar)

- Endpoint tenant-aware (tomado de `backend/app/api/routes/spaces.py`):

```py
# Dependencias: db: AsyncSession = Depends(get_db)
# current_user: User = Depends(get_current_active_user)
await set_tenant_schema(db, current_user)
result = await db.execute(select(Space).offset(skip).limit(limit))
spaces = result.scalars().all()
```

- Forzar search_path manualmente (ejemplo usado en helpers):

```py
from sqlalchemy import text
schema_name = "tenant_my-company"
await db.execute(text(f"SET search_path TO {schema_name}, public"))
```

- JWT payload esperado (ver `backend/app/api/dependencies/auth.py`):

```json
{
  "sub": "123",        # user id
  "tenant_id": "10",  # organization id used to resolve schema
  "exp": 1690000000
}
```

- Comandos útiles (PowerShell):

```powershell
cd backend; poetry install
poetry run alembic revision --autogenerate -m "add something"
poetry run alembic upgrade head
docker-compose up -d postgres redis
poetry run uvicorn app.main:app --reload
poetry run dramatiq app.workers.tasks
poetry run pytest -q
```

Estos ejemplos son trozos directamente aplicables y reflejan patrones ya presentes en el código (`set_tenant_schema`, `get_current_active_user`, uso de `AsyncSession`).
