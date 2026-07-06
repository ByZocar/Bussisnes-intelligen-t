# Frontend NutriAvicola (Fase 7C)

SPA Angular 22 (standalone components + Material 3) para operar el
pipeline PRE CORTE vs FLASH. Consume el backend FastAPI de las Fases 4-7A.

## Stack

- **Angular 22** con standalone components + signals + lazy routing.
- **Angular Material 3** con paleta corporativa NutriAvicola (navy + naranja).
- **SCSS** (sin Tailwind, sin React).
- **HttpClient** para consumir la API REST del backend.

## Rutas

- `/`                                 dashboard con contadores + tabla de batches
- `/batches/nuevo`                    wizard de 5 pasos (nombrar / pre-cortes / flash / preview / generar)
- `/batches/:id`                      detalle del batch (lectura + archivar)
- `/batches/:id/descargas`            lista de archivos generados con descarga individual + ZIP

## Desarrollo local

Prerequisitos: **Node.js 22 LTS** o superior, backend FastAPI corriendo en `http://localhost:8000`.

```powershell
cd frontend
npm install
npm start
```

Abre `http://localhost:4200`. El dev server hace proxy? No — usa el
`environment.ts` que apunta a `http://localhost:8000`. Si el backend
esta en otro host, ajusta `src/environments/environment.ts`.

## Build de produccion

```powershell
npm run build
```

Salida: `dist/frontend/browser/`. Bundle inicial ~100 KB gzipped, lazy
chunks por ruta (~10-45 KB c/u).

## Deploy en Vercel (Fase 7C)

1. Push del repo a GitHub.
2. En [vercel.com](https://vercel.com): `Add New Project` -> selecciona el
   repo -> `Root Directory` = `frontend`.
3. Framework preset: `Other` (Vercel detecta `vercel.json` con SPA rewrite).
4. Env vars: no aplica en runtime (Angular las embebe en build).
5. Para override del `apiBaseUrl` de prod: editar
   `src/environments/environment.prod.ts` y hacer commit.
   Alternativa dinamica: reemplazar `environment.prod.ts` por lectura de
   `window.__ENV__` inyectada por `index.html` desde variables Vercel.

Al hacer push a `main`, Vercel builda y deploya en ~1 min.

## Estructura

```
src/
  app/
    core/
      models.ts             interfaces TS equivalentes a Pydantic
      batches.service.ts    HttpClient wrapper con todos los endpoints
    features/
      dashboard/            dashboard.component.{ts,html,scss}
      batches/
        batch-wizard.component.{ts,html,scss}
        batch-detail.component.{ts,html,scss}
        downloads.component.{ts,html,scss}
    app.{ts,html,scss}      root con toolbar corporativo + <router-outlet>
    app.config.ts           providers globales
    app.routes.ts           rutas con lazy loading
  environments/
    environment.ts          dev (localhost:8000)
    environment.prod.ts     prod (URL Railway)
  assets/logo.jpg           logo NutriAvicola (copia de resources/)
  styles.scss               tema corporativo (paleta + utilitarias)
```

## Tests unitarios

Angular 22 usa el nuevo runner `@angular/build:unit-test` basado en
Vitest. Requiere setup adicional de un browser adapter:

```powershell
npm install --save-dev @vitest/browser-playwright
npx playwright install chromium
npm test -- --watch=false
```

`app.spec.ts` incluye tests base (crea componente, renderiza toolbar).

## Paleta corporativa

Colores definidos en `styles.scss` como CSS variables (`--nutri-*`) para
que los componentes los usen sin hardcodear hex. Ver
[AGENTS.md](../AGENTS.md#fase-7b---docker--railway-ready-2026-07-06)
para la definicion completa (misma paleta que el Excel export).
