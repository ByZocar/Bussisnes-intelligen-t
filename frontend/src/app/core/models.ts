// TypeScript interfaces equivalentes a los Pydantic schemas del backend
// (app/api/schemas.py). Mantener sincronizado.

export type BatchStatus =
  | 'draft'
  | 'ready_to_match'
  | 'matching'
  | 'matched'
  | 'failed'
  | 'archived';

export interface FlashInfo {
  flash_carga_id: number;
  filename: string;
  periodo_year: number | null;
  periodo_month: number | null;
  num_filas_original: number | null;
}

export interface BatchSummary {
  id: string;
  status: BatchStatus;
  nombre: string | null;
  notas: string | null;
  created_at: string | null;
  updated_at: string | null;
  num_pre_cortes: number;
  flash: FlashInfo | null;
  output_dir: string | null;
}

export interface BatchPreCorteItem {
  carga_id: number;
  filename: string;
  fecha_archivo: string | null;
  fecha_produccion: string | null;
  hash_sha256: string;
  num_filas_original: number;
  num_filas_procesadas: number;
  cargado_en: string | null;
  agregado_en: string | null;
}

export interface BatchDetailResponse extends BatchSummary {
  pre_cortes: BatchPreCorteItem[];
}

export interface FileUploadResponse {
  carga_id: number;
  tipo: 'pre_corte' | 'flash';
  filename: string;
  hash_sha256: string;
  num_filas_original: number;
  num_filas_procesadas: number;
  fecha_archivo: string | null;
  fecha_produccion: string | null;
  ya_existia: boolean;
  notificacion_presente: boolean | null;
  num_filas_sin_sap: number | null;
  catalog_coverage_pct: number | null;
  dias_saltados: number | null;
  motivos_saltados: string[] | null;
}

export interface ZipUploadIgnorado { filename: string; motivo: string; }

export interface ZipUploadResponse {
  procesados: FileUploadResponse[];
  ignorados: ZipUploadIgnorado[];
}

export interface DiaColision {
  fecha: string;
  pre_corte_carga_ids: number[];
}

export interface PreviewDia {
  fecha_produccion: string;
  materiales_matched: number;
  materiales_solo_pre: number;
  materiales_solo_flash: number;
  plan_total: number;
  real_total: number;
  delta_total: number;
  cumplimiento_pct: number;
}

export interface SaltoNoLaboral {
  filename: string;
  fecha_produccion_resuelta: string;
  dias_saltados: number;
  motivos: string[];
}

export interface PreviewResponse {
  batch_id: string;
  dias: PreviewDia[];
  colisiones: DiaColision[];
  fechas_no_laborales_saltadas: SaltoNoLaboral[];
  flash_periodo_ok: boolean;
  flash_periodo_mensajes: string[];
  listo_para_confirmar: boolean;
}

export interface GenerateResponse {
  batch_id: string;
  consolidado_filename: string;
  dailies_filenames: string[];
  zip_filename: string;
  fechas_procesadas: string[];
  fechas_sin_datos_en_rango: string[];
}

export interface DownloadItem {
  filename: string;
  size_bytes: number;
  kind: 'consolidado' | 'daily' | 'zip';
}

export interface DownloadsResponse {
  batch_id: string;
  output_dir: string;
  items: DownloadItem[];
}

export interface DiaNoLaboral {
  fecha: string;
  motivo: string;
  es_domingo: boolean;
}

export interface CalendarioAnoResponse {
  year: number;
  festivos: DiaNoLaboral[];
  cobertura_desde: string;
  cobertura_hasta: string;
}
