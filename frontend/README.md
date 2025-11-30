# SpaceManager Frontend

## Testing y configuración de API

- Base URL en tests: los handlers de MSW están configurados para `http://localhost:3000/api`. Durante las pruebas (Vitest), el cliente de API (`src/lib/api.ts` y `src/lib/auth.ts`) fuerza esa URL para asegurar compatibilidad.
- Entornos no-test: en desarrollo/producción, el cliente usa `NEXT_PUBLIC_API_URL` (sin barra final) y agrega `/api` automáticamente. Ejemplo: `NEXT_PUBLIC_API_URL=http://localhost:8000` → `http://localhost:8000/api`.
- Refresh de tokens: el interceptor usa `${baseURL}/auth/refresh` y evita redirecciones durante `NODE_ENV=test`.

### Ejecutar tests

```bash
pnpm install
pnpm test
```

En Docker (contenedor `spacemanager_frontend`):

```powershell
docker exec spacemanager_frontend npm test -- --run
```

### Variables de entorno

- `NEXT_PUBLIC_API_URL`: origen del backend (sin `/api`). Ejemplo: `http://localhost:8000`.

### Notas

- Los componentes de autenticación (`src/app/login/page.tsx`, `src/app/register/page.tsx`) guardan tokens en `localStorage` tras login/registro.
- Durante tests, se mockean `window.location` y `localStorage` en `src/__tests__/utils/setup.ts`.
