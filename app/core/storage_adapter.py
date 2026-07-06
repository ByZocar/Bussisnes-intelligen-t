"""Adapter de storage: disco local o Supabase Storage (Fase 7B/7E).

Este modulo define la interfaz `Storage` y dos implementaciones:

- **`LocalStorage`**: default para dev y para Railway con volumen persistente
  montado en `NUTRI_DATA_DIR`. No requiere dependencias extra.
- **`SupabaseStorage`**: activado cuando `SUPABASE_URL` + `SUPABASE_SERVICE_KEY`
  estan definidas. Sube blobs a un bucket privado y sirve signed URLs
  temporales. Requiere `pip install supabase` (dep opcional).

Los endpoints de API llaman `get_storage()` para obtener la instancia
apropiada. El resto del codigo no sabe (ni le importa) donde estan los
blobs realmente.

Contrato: los blobs se identifican por `(bucket, key)`. Ejemplos:
- `("uploads", "batch_<id>/pre_corte/<carga_id>.xlsx")`
- `("outputs", "batch_<id>/cumplimiento_20260214.xlsx")`

Ambas implementaciones son **sincronas**. Para altos volumenes puede
migrarse a `asyncio` en el futuro; por ahora la latencia de disco/red
domina y no vale la pena la complejidad extra.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Iterator, Protocol, runtime_checkable

from app.config import (
    DATA_DIR,
    SUPABASE_BUCKET_OUTPUTS,
    SUPABASE_BUCKET_UPLOADS,
    SUPABASE_SERVICE_KEY,
    SUPABASE_URL,
    storage_backend_activo,
)


class StorageError(RuntimeError):
    """Fallo del adapter (409/500 en API)."""


@runtime_checkable
class Storage(Protocol):
    """Interfaz uniforme para persistencia de blobs (raw uploads + outputs)."""

    backend_name: str

    def put(self, bucket: str, key: str, data: bytes) -> str:
        """Guarda `data` bajo `(bucket, key)`. Retorna una ruta/URL logica."""
        ...

    def get(self, bucket: str, key: str) -> bytes:
        """Descarga los bytes. Lanza `FileNotFoundError` si no existe."""
        ...

    def exists(self, bucket: str, key: str) -> bool:
        ...

    def delete(self, bucket: str, key: str) -> bool:
        """Retorna True si borro, False si no existia."""
        ...

    def list(self, bucket: str, prefix: str = "") -> list[str]:
        """Lista keys que empiezan por `prefix`."""
        ...

    def public_url(self, bucket: str, key: str, expires_in: int = 3600) -> str:
        """Devuelve una URL descargable (signed en Supabase, `file://` en local)."""
        ...


# ---------------------------------------------------------------------------
# LocalStorage: default para dev y para Railway con volumen persistente
# ---------------------------------------------------------------------------
class LocalStorage:
    """Storage sobre el filesystem local (o volumen montado en Railway).

    Estructura en disco: `<DATA_DIR>/<bucket>/<key>`. Los directorios se
    crean bajo demanda.
    """

    backend_name = "local"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else DATA_DIR

    def _path(self, bucket: str, key: str) -> Path:
        # Prevencion basica de path traversal: normalizamos y validamos.
        clean_key = key.replace("\\", "/").lstrip("/")
        base = (self.root / bucket).resolve()
        target = (base / clean_key).resolve()
        try:
            target.relative_to(base)
        except ValueError as exc:
            raise StorageError(f"Path traversal detectado: {key}") from exc
        return target

    def put(self, bucket: str, key: str, data: bytes) -> str:
        p = self._path(bucket, key)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return str(p)

    def get(self, bucket: str, key: str) -> bytes:
        p = self._path(bucket, key)
        if not p.exists():
            raise FileNotFoundError(f"{bucket}/{key} no existe en {self.root}")
        return p.read_bytes()

    def exists(self, bucket: str, key: str) -> bool:
        return self._path(bucket, key).exists()

    def delete(self, bucket: str, key: str) -> bool:
        p = self._path(bucket, key)
        if not p.exists():
            return False
        p.unlink()
        return True

    def list(self, bucket: str, prefix: str = "") -> list[str]:
        base = (self.root / bucket).resolve()
        if not base.exists():
            return []
        prefix_norm = prefix.replace("\\", "/").lstrip("/")
        out: list[str] = []
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(base).as_posix()
            if rel.startswith(prefix_norm):
                out.append(rel)
        return sorted(out)

    def public_url(self, bucket: str, key: str, expires_in: int = 3600) -> str:
        p = self._path(bucket, key)
        return p.as_uri()


# ---------------------------------------------------------------------------
# SupabaseStorage: opcional, activado por env vars
# ---------------------------------------------------------------------------
class SupabaseStorage:
    """Storage sobre Supabase Storage (buckets privados con signed URLs).

    Requiere `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` en env, y la libreria
    `supabase` instalada. Si falta la libreria, el constructor lanza
    `StorageError` claro.
    """

    backend_name = "supabase"

    def __init__(
        self,
        url: str | None = None,
        service_key: str | None = None,
    ) -> None:
        self._url = url or SUPABASE_URL
        self._key = service_key or SUPABASE_SERVICE_KEY
        if not self._url or not self._key:
            raise StorageError(
                "SupabaseStorage requiere SUPABASE_URL y SUPABASE_SERVICE_KEY."
            )
        try:
            from supabase import create_client  # type: ignore[import-not-found]
        except ImportError as exc:
            raise StorageError(
                "SupabaseStorage requiere 'pip install supabase'. Sin ella, "
                "usa LocalStorage."
            ) from exc
        self._client = create_client(self._url, self._key)

    def _api(self, bucket: str) -> Any:
        return self._client.storage.from_(bucket)

    def put(self, bucket: str, key: str, data: bytes) -> str:
        self._api(bucket).upload(
            path=key,
            file=data,
            file_options={"upsert": "true"},
        )
        return f"supabase://{bucket}/{key}"

    def get(self, bucket: str, key: str) -> bytes:
        try:
            return self._api(bucket).download(key)
        except Exception as exc:
            raise FileNotFoundError(f"{bucket}/{key} no existe en Supabase") from exc

    def exists(self, bucket: str, key: str) -> bool:
        try:
            self._api(bucket).download(key)
            return True
        except Exception:
            return False

    def delete(self, bucket: str, key: str) -> bool:
        try:
            self._api(bucket).remove([key])
            return True
        except Exception:
            return False

    def list(self, bucket: str, prefix: str = "") -> list[str]:
        try:
            items = self._api(bucket).list(path=prefix or None)
            return [item["name"] for item in items]
        except Exception:
            return []

    def public_url(self, bucket: str, key: str, expires_in: int = 3600) -> str:
        signed = self._api(bucket).create_signed_url(key, expires_in)
        # supabase-py returns dict with 'signedURL' or 'signed_url'
        if isinstance(signed, dict):
            return signed.get("signedURL") or signed.get("signed_url") or ""
        return str(signed)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------
_INSTANCE: Storage | None = None


def get_storage() -> Storage:
    """Retorna la instancia singleton segun `storage_backend_activo()`."""
    global _INSTANCE
    if _INSTANCE is not None:
        return _INSTANCE
    backend = storage_backend_activo()
    if backend == "supabase":
        _INSTANCE = SupabaseStorage()
    else:
        _INSTANCE = LocalStorage()
    return _INSTANCE


def reset_storage_singleton() -> None:
    """Limpia el singleton (util para tests)."""
    global _INSTANCE
    _INSTANCE = None


# Nombres de bucket estandar; los endpoints los importan de aca para no
# hardcodear strings sueltas en el codigo.
BUCKET_UPLOADS = SUPABASE_BUCKET_UPLOADS  # "uploads" por default
BUCKET_OUTPUTS = SUPABASE_BUCKET_OUTPUTS  # "outputs" por default
