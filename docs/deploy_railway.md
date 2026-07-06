# Deploy en Railway (Fase 7B)

Guia paso a paso para deployar la API en Railway con volumen persistente
+ Supabase Storage opcional.

## Prerequisitos

- Cuenta en [Railway.com](https://railway.com) (plan Hobby, 5 USD/mes).
- Repo en GitHub (Railway se conecta via GitHub App).
- Proyecto Supabase (opcional, para Fase 7E): [supabase.com](https://supabase.com).
- Docker instalado localmente **solo si quieres smoke test**; para deploy
  no es necesario — Railway builda el `Dockerfile` en su infraestructura.

## Estructura de archivos relevante

- [Dockerfile](../Dockerfile) — multi-stage, non-root, python:3.14-slim, healthcheck `/health`.
- [.dockerignore](../.dockerignore) — excluye `tests/`, `data/`, `venv/`, `.git/`, `.env`.
- [railway.json](../railway.json) — config de build + healthcheck + restart policy.
- [requirements.txt](../requirements.txt) — deps runtime (Pillow, supabase, fastapi, uvicorn...).
- [.env.example](../.env.example) — template. En Railway se llenan desde la UI.

## Paso 1: crear proyecto en Railway

1. Login en [railway.com](https://railway.com) con GitHub.
2. `New Project` -> `Deploy from GitHub repo` -> selecciona el repo.
3. Railway detecta `Dockerfile` y `railway.json` automaticamente.

## Paso 2: configurar volumen persistente

**Critico**: SQLite + uploads viven en `/data`. Sin volumen, cada deploy
borra el historico.

1. En el servicio -> `Settings` -> `Volumes` -> `+ New Volume`.
2. Mount path: `/data`.
3. Size: 1 GB (mas que suficiente para meses de operacion).

## Paso 3: variables de entorno

En `Settings` -> `Variables` agregar:

```
NUTRI_DATA_DIR=/data
NUTRI_LOGS_DIR=/data/logs
NUTRI_API_HOST=0.0.0.0
NUTRI_CORS_ORIGINS=https://<tu-app>.vercel.app,https://<preview>.vercel.app
```

`PORT` la inyecta Railway automaticamente; no la definas manualmente.

Si vas a usar Supabase Storage (Fase 7E):

```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_KEY=sb_secret_...   # la SECRET, no la publishable
SUPABASE_BUCKET_UPLOADS=uploads
SUPABASE_BUCKET_OUTPUTS=outputs
```

Sin estas, la app usa `LocalStorage` sobre el volumen `/data`. Los tests
`test_storage_backend_local_por_default` y `test_get_storage_devuelve_local_por_default`
verifican este fallback.

## Paso 4: deploy y verificacion

Al hacer push a `main`:

1. Railway builda el `Dockerfile` (~2-4 min primera vez, ~30-60 s subsiguientes).
2. Corre `HEALTHCHECK` cada 30 s contra `/health`.
3. Si `/health` responde 200, el deploy se marca `Success`.

Verifica en logs:

```
INFO:     Uvicorn running on http://0.0.0.0:$PORT (Press CTRL+C to quit)
INFO:     Application startup complete.
```

Genera un dominio publico: `Settings` -> `Networking` -> `Generate Domain`.
Prueba:

```
curl https://<tu-servicio>.up.railway.app/health
```

Debe responder `{"status":"ok","version":"...","now":"..."}`.

Documentacion Swagger: `https://<tu-servicio>.up.railway.app/docs`.

## Paso 5: setup Supabase Storage (Fase 7E)

Cuando tengas la SECRET KEY:

1. Ponla en `SUPABASE_SERVICE_KEY` (Railway + `.env` local).
2. Corre `python scripts/setup_supabase.py` -> crea buckets `uploads` y
   `outputs` como privados.
3. Restart del servicio en Railway. El `StorageAdapter` detecta las env
   vars y usa `SupabaseStorage` automaticamente.

## Smoke build local (opcional)

Requiere Docker Desktop corriendo:

```powershell
docker build -t nutriavicola-api:local .
docker run --rm -p 8000:8000 -v ${PWD}/data-local:/data nutriavicola-api:local
```

Luego `curl http://127.0.0.1:8000/health`.

Para test con Supabase real:

```powershell
docker run --rm -p 8000:8000 -v ${PWD}/data-local:/data --env-file .env nutriavicola-api:local
```

## Rotacion de credenciales

Cuando cierres el proyecto:

1. Supabase -> Settings -> API -> **Rotate** publishable + secret keys.
2. Supabase -> Settings -> Database -> **Reset** password.
3. Railway -> Variables -> actualiza los valores nuevos.
4. Borra el `.env` local.

## Troubleshooting

- **Build falla por wheel de Pillow / numpy**: la imagen usa Python 3.14
  y algunos wheels binarios pueden no existir aun. El builder tiene
  `build-essential`; compila desde source si es necesario (tarda mas).
- **Healthcheck falla**: verifica que `PORT` este siendo respetado y que
  no haya errores de import en logs. `NUTRI_DATA_DIR` debe apuntar a un
  directorio con permisos (`/data` con el volumen montado).
- **Supabase 403 "row-level security policy"**: estas usando la
  publishable key en vez de la secret. Cambia a `sb_secret_...`.
- **SQLite lock**: SQLite serializa writes. Un solo replica (por default).
  Si necesitas escalar, migra a Postgres (Fase 7F opcional).
