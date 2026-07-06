# Deploy del frontend en Vercel (Fase 7C)

## Prerequisitos

- Backend FastAPI ya deployado en Railway (Fase 7B) con dominio publico
  (ej: `https://nutriavicola-api.up.railway.app`).
- CORS del backend permite el dominio Vercel: en Railway env vars,
  `NUTRI_CORS_ORIGINS=https://<tu-app>.vercel.app,https://*.vercel.app`.
- Cuenta Vercel (free tier suficiente para SPA estatico).

## Paso 1: apuntar `environment.prod.ts` al Railway URL

Editar [frontend/src/environments/environment.prod.ts](../frontend/src/environments/environment.prod.ts):

```typescript
export const environment = {
  production: true,
  apiBaseUrl: 'https://nutriavicola-api.up.railway.app',
  n8nWebhookMatch: '',  // opcional Fase 7D
};
```

Commit + push.

## Paso 2: crear proyecto en Vercel

1. Login en [vercel.com](https://vercel.com) con GitHub.
2. `Add New` -> `Project` -> selecciona el repo.
3. **Root Directory**: `frontend` (no la raiz).
4. **Framework Preset**: `Other`.
5. Build command / output se leen de [frontend/vercel.json](../frontend/vercel.json):
   - `buildCommand`: `npm run build -- --configuration production`
   - `outputDirectory`: `dist/frontend/browser`
   - `installCommand`: `npm ci`
   - `rewrites`: SPA rewrite `/(.*)` -> `/index.html`
6. `Deploy`.

Primera compilacion: ~1-2 min. Genera dominio `https://<proyecto>.vercel.app`.

## Paso 3: actualizar CORS del backend

En Railway del backend, ajustar:

```
NUTRI_CORS_ORIGINS=https://<proyecto>.vercel.app,https://<proyecto>-*.vercel.app
```

Restart del servicio de Railway. Los previews de Vercel (branches) usan
subdominios `<proyecto>-<hash>.vercel.app`; el patron con `-*` los cubre.

## Paso 4: verificacion

Abrir el dominio Vercel:

- Debe verse el toolbar con logo NutriAvicola.
- Dashboard carga lista de batches (si esta vacia, mensaje "No hay batches").
- Wizard: crear batch, subir pre_corte y flash, ver preview, generar.
- Descargas: los enlaces deben pegarle al Railway URL con signed download.

## Rollback

Vercel guarda todos los deploys. Si algo se rompe:

- `Deployments` -> selecciona el deploy anterior -> `Promote to Production`.

## Preview branches

Cada push a un branch != `main` genera un deploy preview con URL propia.
Ideal para probar cambios sin afectar produccion. Vercel comenta el
enlace en el PR de GitHub.

## Costos

- Vercel Hobby: gratis (100 GB bandwidth/mes, mas que suficiente para SPA
  corporativa interna).
- Si vas a comercial pasa a Pro (20 USD/mes por miembro).
