-- Crear tablas faltantes en el esquema public
CREATE SCHEMA IF NOT EXISTS public;

-- Crear tabla users si no existe
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para users
CREATE INDEX IF NOT EXISTS ix_public_users_email ON public.users (email);
CREATE INDEX IF NOT EXISTS ix_public_users_id ON public.users (id);

-- Crear tabla organizations si no existe
CREATE TABLE IF NOT EXISTS public.organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    schema_name VARCHAR(63) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    email VARCHAR(255),
    phone VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para organizations
CREATE INDEX IF NOT EXISTS ix_public_organizations_id ON public.organizations (id);
CREATE INDEX IF NOT EXISTS ix_public_organizations_name ON public.organizations (name);
CREATE INDEX IF NOT EXISTS ix_public_organizations_slug ON public.organizations (slug);
