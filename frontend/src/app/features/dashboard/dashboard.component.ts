import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { BatchesService } from '../../core/batches.service';
import { BatchSummary } from '../../core/models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule, RouterLink, MatButtonModule, MatCardModule, MatIconModule,
    MatProgressSpinnerModule, MatTooltipModule,
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent {
  private readonly svc = inject(BatchesService);

  loading = signal(true);
  error = signal<string | null>(null);
  batches = signal<BatchSummary[]>([]);

  constructor() {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.error.set(null);
    this.svc.list(false).subscribe({
      next: (bs) => { this.batches.set(bs); this.loading.set(false); },
      error: (e) => { this.error.set(String(e.message ?? e)); this.loading.set(false); },
    });
  }

  countByStatus(status: string): number {
    return this.batches().filter(b => b.status === status).length;
  }
}
