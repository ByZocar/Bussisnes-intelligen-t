# Fase 7B — Docker + Railway

**Estado:** completada  
**Fecha de referencia:** 2026-07-06

## Objetivo

Imagen production-ready para Railway con configuracion por variables de entorno
y abstraccion de almacenamiento local vs Supabase.

## Artefactos de deploy

| Archivo | Proposito |
|---------|-----------|
| `Dockerfile` | Multi-stage, usuario non-root `nutri`, HEALTHCHECK |
| `railway.json` | Builder Docker, restart policy |
| `.dockerignore` | Excluye tests, venv, data local |
| `.env.example` | Template documentado |
| `docs/deploy_railway.md` | Guia paso a paso |

## Variables clave

| Variable | Uso |
|----------|-----|
| `NUTRI_DATA_DIR` | `/data` en Railway (volumen) |
| `PORT` | Inyectada por Railway |
| `NUTRI_CORS_ORIGINS` | Origenes del frontend Vercel |
| `SUPABASE_*` | Activa `SupabaseStorage` (Fase 7E) |

## Modulo

- `app/core/storage_adapter.py` — Protocol `Storage`, `LocalStorage`,
  `SupabaseStorage`, factory `get_storage()`.

## Tests

- `tests/test_config.py`
- `tests/test_storage_adapter.py`

## Script auxiliar

- `scripts/setup_supabase.py` — crea buckets `uploads`/`outputs` (idempotente).
