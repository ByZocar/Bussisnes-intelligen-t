import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent),
    title: 'NutriAvicola — PRE CORTE vs FLASH',
  },
  {
    path: 'batches/nuevo',
    loadComponent: () =>
      import('./features/batches/batch-wizard.component').then(m => m.BatchWizardComponent),
    title: 'Nuevo batch',
  },
  {
    path: 'batches/:id',
    loadComponent: () =>
      import('./features/batches/batch-detail.component').then(m => m.BatchDetailComponent),
    title: 'Detalle del batch',
  },
  {
    path: 'batches/:id/descargas',
    loadComponent: () =>
      import('./features/batches/downloads.component').then(m => m.DownloadsComponent),
    title: 'Descargas del batch',
  },
  { path: '**', redirectTo: '' },
];
