import { CommonModule } from '@angular/common';
import { Component, Input, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { BatchesService } from '../../core/batches.service';
import { BatchDetailResponse } from '../../core/models';

@Component({
  selector: 'app-batch-detail',
  standalone: true,
  imports: [
    CommonModule, RouterLink, MatButtonModule, MatCardModule, MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './batch-detail.component.html',
  styleUrl: './batch-detail.component.scss',
})
export class BatchDetailComponent {
  private readonly svc = inject(BatchesService);
  private readonly router = inject(Router);

  @Input() id!: string;

  loading = signal(true);
  batch = signal<BatchDetailResponse | null>(null);
  error = signal<string | null>(null);

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.svc.get(this.id).subscribe({
      next: (b) => { this.batch.set(b); this.loading.set(false); },
      error: (e) => { this.error.set(String(e?.message ?? e)); this.loading.set(false); },
    });
  }

  archive(): void {
    if (!confirm('Archivar este batch?')) return;
    this.svc.archive(this.id).subscribe(() => this.router.navigate(['/']));
  }
}
