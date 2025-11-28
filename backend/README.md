# SpaceManager Backend

Multi-tenant space rental management API built with FastAPI, PostgreSQL, and Redis.

## Features

- 🏢 **Multi-tenant Architecture**: Schema-based tenant isolation
- 🔐 **JWT Authentication**: Secure token-based authentication
- 🚀 **Async Everything**: FastAPI + SQLAlchemy async + asyncpg
- 📦 **Background Tasks**: Dramatiq + Redis for async processing
- 🐳 **Docker Ready**: Full Docker Compose setup for development
- 📊 **Auto-generated API Docs**: Interactive Swagger UI and ReDoc

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (async with asyncpg)
- **ORM**: SQLAlchemy 2.0+ (async)
- **Migrations**: Alembic
- **Task Queue**: Dramatiq + Redis
- **Authentication**: JWT (python-jose)
- **Validation**: Pydantic v2
- **Package Manager**: Poetry

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── dependencies/    # Dependency injection
│   │   └── routes/          # API endpoints
│   ├── core/                # Core configuration
│   ├── middleware/          # Custom middleware
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── workers/             # Dramatiq tasks
│   └── main.py              # FastAPI app
├── migrations/              # Alembic migrations
├── tests/                   # Test suite
├── pyproject.toml           # Poetry dependencies
├── Dockerfile               # Production container
└── alembic.ini              # Alembic config
```

## Getting Started

### Prerequisites

- Python 3.12+
- Poetry
- Docker & Docker Compose (for local development)

### Installation

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Install dependencies with Poetry**
   ```bash
   poetry install
   ```

3. **Copy environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and update the values as needed.

4. **Start services with Docker Compose**
   ```bash
   cd ..
   docker-compose up -d postgres redis
   ```

5. **Run database migrations**
   ```bash
   poetry run alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

### Using Docker Compose (Recommended)

Start all services (PostgreSQL, Redis, Backend, Worker):

```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f backend
```

Stop services:
```bash
docker-compose down
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Migrations

Create a new migration:
```bash
poetry run alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
poetry run alembic upgrade head
```

Rollback migration:
```bash
poetry run alembic downgrade -1
```

## Background Tasks

Start Dramatiq worker:
```bash
poetry run dramatiq app.workers.tasks
```

The worker will process background tasks like:
- Sending reservation confirmations
- Generating monthly reports
- Cleaning up expired reservations

## Multi-tenant Architecture

This application uses **schema-based multi-tenancy**:

- Each organization gets its own PostgreSQL schema
- The `public` schema stores organizations and users
- Tenant-specific data (spaces, reservations) is stored in tenant schemas
- JWT tokens include tenant context
- Middleware automatically sets the correct schema for each request

### Creating a New Tenant

Register a new organization via the `/api/v1/auth/register` endpoint:

```json
{
  "email": "admin@example.com",
  "password": "securepassword",
  "full_name": "Admin User",
  "organization_name": "My Company",
  "organization_slug": "my-company"
}
```

This will:
1. Create a new organization in the `public` schema
2. Create a new PostgreSQL schema (`tenant_my-company`)
3. Create the first user (as superuser)
4. Return a JWT token

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user and organization
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Spaces
- `POST /api/v1/spaces` - Create space
- `GET /api/v1/spaces` - List spaces
- `GET /api/v1/spaces/{id}` - Get space
- `PUT /api/v1/spaces/{id}` - Update space
- `DELETE /api/v1/spaces/{id}` - Delete space

### Reservations
- `POST /api/v1/reservations` - Create reservation
- `GET /api/v1/reservations` - List user's reservations
- `GET /api/v1/reservations/{id}` - Get reservation
- `PUT /api/v1/reservations/{id}` - Update reservation
- `DELETE /api/v1/reservations/{id}` - Cancel reservation

## Development

### Code Formatting

Format code with Black:
```bash
poetry run black .
```

Lint with Ruff:
```bash
poetry run ruff check .
```

### Testing

Run tests:
```bash
poetry run pytest
```

With coverage:
```bash
poetry run pytest --cov=app
```

## Deployment

### Railway (Recommended)

1. Create a new project on Railway
2. Add PostgreSQL and Redis services
3. Deploy the backend service from this directory
4. Set environment variables
5. Run migrations: `alembic upgrade head`

### Manual Deployment

1. Build the Docker image:
   ```bash
   docker build -t spacemanager-backend .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 \
     -e DATABASE_URL=your-db-url \
     -e REDIS_URL=your-redis-url \
     -e SECRET_KEY=your-secret-key \
     spacemanager-backend
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | - |
| `REDIS_URL` | Redis connection URL | - |
| `SECRET_KEY` | JWT secret key (min 32 chars) | - |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 30 |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | [] |
| `DEBUG` | Debug mode | False |
| `ENVIRONMENT` | Environment name | production |

## License

MIT

## Next Steps

- [ ] Implement email sending for notifications
- [ ] Add file upload to DigitalOcean Spaces
- [ ] Create admin dashboard endpoints
- [ ] Add inventory management
- [ ] Implement payment processing
- [ ] Add analytics and reporting
- [ ] Create CLI tool for management tasks
