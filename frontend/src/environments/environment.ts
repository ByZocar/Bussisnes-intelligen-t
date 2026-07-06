// Config runtime. En prod (Vercel) se reemplaza via `environment.prod.ts`
// generado automaticamente por `angular.json > fileReplacements`.
//
// Alternativa: leer `window.__ENV__` inyectada por Vercel Edge Config.
export const environment = {
  production: false,
  apiBaseUrl: 'http://localhost:8000',
  n8nWebhookMatch: '', // opcional Fase 7D
};
