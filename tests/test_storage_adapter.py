"""Tests del storage adapter (Fase 7B).

LocalStorage se prueba a fondo (default en dev y Railway con volumen).
SupabaseStorage se prueba solo lo instanciable + guardas de env; la
integracion real con Supabase queda para Fase 7E con credenciales.
"""
from __future__ import annotations

import pytest

from app.core.storage_adapter import (
    LocalStorage,
    Storage,
    StorageError,
    SupabaseStorage,
    get_storage,
    reset_storage_singleton,
)


@pytest.fixture(autouse=True)
def _reset_singleton():
    reset_storage_singleton()
    yield
    reset_storage_singleton()


# ---------- LocalStorage ----------

def test_local_storage_implementa_protocol(tmp_path):
    s = LocalStorage(root=tmp_path)
    assert isinstance(s, Storage)
    assert s.backend_name == "local"


def test_local_put_get_delete_round_trip(tmp_path):
    s = LocalStorage(root=tmp_path)
    data = b"hola mundo binario \x00 \xff"
    path_logico = s.put("uploads", "batch_1/pre_corte/1.xlsx", data)
    assert path_logico.endswith("1.xlsx")
    assert s.exists("uploads", "batch_1/pre_corte/1.xlsx")
    assert s.get("uploads", "batch_1/pre_corte/1.xlsx") == data
    assert s.delete("uploads", "batch_1/pre_corte/1.xlsx") is True
    assert not s.exists("uploads", "batch_1/pre_corte/1.xlsx")
    assert s.delete("uploads", "batch_1/pre_corte/1.xlsx") is False


def test_local_get_no_existente_lanza_filenotfound(tmp_path):
    s = LocalStorage(root=tmp_path)
    with pytest.raises(FileNotFoundError):
        s.get("uploads", "no-existe")


def test_local_list_devuelve_keys_con_prefix(tmp_path):
    s = LocalStorage(root=tmp_path)
    s.put("outputs", "batch_a/x1.xlsx", b"x")
    s.put("outputs", "batch_a/x2.xlsx", b"y")
    s.put("outputs", "batch_b/y1.xlsx", b"z")
    assert s.list("outputs", "batch_a/") == ["batch_a/x1.xlsx", "batch_a/x2.xlsx"]
    assert len(s.list("outputs")) == 3
    assert s.list("outputs", "nada") == []


def test_local_public_url_es_file_uri(tmp_path):
    s = LocalStorage(root=tmp_path)
    s.put("uploads", "a.txt", b"1")
    url = s.public_url("uploads", "a.txt")
    assert url.startswith("file:")


def test_local_bloquea_path_traversal(tmp_path):
    s = LocalStorage(root=tmp_path)
    with pytest.raises(StorageError):
        s.put("uploads", "../../etc/passwd", b"hack")
    with pytest.raises(StorageError):
        s.get("uploads", "../../secret")


# ---------- SupabaseStorage (instanciacion, sin conexion real) ----------

def test_supabase_falta_credenciales_falla_claro(monkeypatch):
    import app.core.storage_adapter as adapter
    monkeypatch.setattr(adapter, "SUPABASE_URL", None)
    monkeypatch.setattr(adapter, "SUPABASE_SERVICE_KEY", None)
    with pytest.raises(StorageError, match="SUPABASE_URL"):
        adapter.SupabaseStorage(url=None, service_key=None)


def test_supabase_se_instancia_con_credenciales_dummy():
    """Verifica que la clase se puede construir con creds fake (sin conectar).

    El constructor de `supabase.create_client` no valida la URL en ese
    momento; solo la usa al hacer la primera llamada. Asi que este test
    prueba que las guardas de env pasan y la instancia queda armada.
    """
    try:
        s = SupabaseStorage(
            url="https://dummy.supabase.co",
            service_key="sk_fake_xxx",
        )
        assert s.backend_name == "supabase"
    except StorageError as exc:
        # Si la lib supabase no esta instalada, la clase lo dice claro.
        assert "supabase" in str(exc).lower()


# ---------- Factory ----------

def test_get_storage_devuelve_local_por_default(monkeypatch):
    import app.config as cfg
    import app.core.storage_adapter as adapter
    monkeypatch.setattr(cfg, "SUPABASE_URL", None)
    monkeypatch.setattr(cfg, "SUPABASE_SERVICE_KEY", None)
    monkeypatch.setattr(adapter, "SUPABASE_URL", None)
    monkeypatch.setattr(adapter, "SUPABASE_SERVICE_KEY", None)
    reset_storage_singleton()
    s = adapter.get_storage()
    assert s.backend_name == "local"


def test_get_storage_es_singleton(monkeypatch):
    import app.config as cfg
    import app.core.storage_adapter as adapter
    monkeypatch.setattr(cfg, "SUPABASE_URL", None)
    monkeypatch.setattr(cfg, "SUPABASE_SERVICE_KEY", None)
    monkeypatch.setattr(adapter, "SUPABASE_URL", None)
    monkeypatch.setattr(adapter, "SUPABASE_SERVICE_KEY", None)
    reset_storage_singleton()
    a = get_storage()
    b = get_storage()
    assert a is b
