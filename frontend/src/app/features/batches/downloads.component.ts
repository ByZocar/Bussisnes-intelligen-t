import { CommonModule } from '@angular/common';
import { Component, Input, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { BatchesService } from '../../core/batches.service';
import { DownloadItem, DownloadsResponse } from '../../core/models';

@Component({
  selector: 'app-downloads',
  standalone: true,
  imports: [
    CommonModule, RouterLink, MatButtonModule, MatCardModule, MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './downloads.component.html',
  styleUrl: './downloads.component.scss',
})
export class DownloadsComponent {
  private readonly svc = inject(BatchesService);

  @Input() id!: string;

  loading = signal(true);
  error = signal<string | null>(null);
  data = signal<DownloadsResponse | null>(null);

  ngOnInit(): void {
    this.svc.downloads(this.id).subscribe({
      next: (d) => { this.data.set(d); this.loading.set(false); },
      error: (e) => { this.error.set(String(e?.message ?? e)); this.loading.set(false); },
    });
  }

  href(item: DownloadItem): string {
    return this.svc.downloadUrl(this.id, item.filename);
  }

  humanSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  }

  filterKind(kind: DownloadItem['kind']): DownloadItem[] {
    return this.data()?.items.filter(i => i.kind === kind) ?? [];
  }
}
