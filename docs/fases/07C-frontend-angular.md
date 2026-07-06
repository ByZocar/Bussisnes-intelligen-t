# Fase 7C — Frontend Angular 22

**Estado:** completada  
**Fecha de referencia:** 2026-07-06

## Objetivo

UI operativa para crear batches, subir archivos, revisar preview y descargar
excels generados.

## Stack

- Angular 22 standalone + signals + lazy routes.
- Angular Material 3 — paleta NutriAvicola (navy `#0F2E4C`, naranja `#E87722`).

## Rutas lazy

| Ruta | Componente |
|------|------------|
| `/` | Dashboard — contadores y batches recientes |
| `/batches/new` | Wizard 5 pasos (nombrar, pre-cortes, flash, preview, generar) |
| `/batches/:id` | Detalle read-only + archivar |
| `/batches/:id/downloads` | Consolidado, dailies, ZIP |

## Servicio

- `BatchesService` — wrapper HttpClient de los 16 endpoints `/batches`.

## Deploy

- `frontend/vercel.json` — SPA rewrite.
- `docs/deploy_vercel.md` — actualizar `environment.prod.ts` con URL Railway.

## Verificacion

Build production ~100 KB gzip inicial. CORS validado contra backend local
`:8000`.

## Asset requerido

`frontend/src/assets/logo.jpg` (copiado desde `resources/image_720508810_0.jpg`
por el script de historial si no existe).
