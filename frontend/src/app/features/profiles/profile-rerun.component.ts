import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ProfilesService } from '../../core/profiles.service';
import { DownloadItem, GenerateResponse } from '../../core/profile-models';

@Component({
  selector: 'app-profile-rerun',
  standalone: true,
  imports: [
    CommonModule, RouterLink, MatButtonModule, MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './profile-rerun.component.html',
  styleUrl: './profile-rerun.component.scss',
})
export class ProfileRerunComponent {
  private readonly svc = inject(ProfilesService);
  private readonly route = inject(ActivatedRoute);

  readonly profileId = this.route.snapshot.paramMap.get('id') ?? '';

  leftFile = signal<File | null>(null);
  rightFile = signal<File | null>(null);
  homologacionFile = signal<File | null>(null);
  busy = signal(false);
  error = signal<string | null>(null);
  result = signal<GenerateResponse | null>(null);
  downloads = signal<DownloadItem[]>([]);

  readonly canSubmit = computed(
    () => !!this.leftFile() && !!this.rightFile() && !this.busy(),
  );

  onFileSelected(side: 'left' | 'right' | 'homologacion', evt: Event): void {
    const input = evt.target as HTMLInputElement;
    const file = (input.files ?? [])[0] ?? null;
    if (side === 'left') this.leftFile.set(file);
    else if (side === 'right') this.rightFile.set(file);
    else this.homologacionFile.set(file);
    input.value = '';
  }

  submit(): void {
    if (!this.canSubmit()) return;
    this.busy.set(true);
    this.error.set(null);
    this.result.set(null);
    this.downloads.set([]);
    this.svc
      .reejecutar(
        this.profileId, this.leftFile()!, this.rightFile()!,
        this.homologacionFile(),
      )
      .subscribe({
        next: (res) => {
          this.result.set(res);
          this.svc.downloads(this.profileId).subscribe({
            next: (d) => { this.downloads.set(d); this.busy.set(false); },
            error: () => this.busy.set(false),
          });
        },
        error: (e) => {
          this.busy.set(false);
          const detail = e?.error?.detail ?? e?.message ?? String(e);
          this.error.set(typeof detail === 'string' ? detail : JSON.stringify(detail));
        },
      });
  }

  downloadHref(filename: string): string {
    return this.svc.downloadUrl(this.profileId, filename);
  }

  kpiList(kpis: Record<string, unknown> | undefined): { id: string; value: string }[] {
    if (!kpis) return [];
    return Object.entries(kpis)
      .filter(([, v]) => v == null || typeof v !== 'object')
      .map(([id, v]) => ({ id, value: v == null ? '—' : String(v) }));
  }
}
