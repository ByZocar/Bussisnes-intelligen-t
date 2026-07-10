"""Tests de app.config (Fase 7B): env vars, CORS parsing, storage backend."""
from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _restore_env(monkeypatch):
    """Cada test corre con un env vars limpio; monkeypatch revierte al final."""
    yield


def _reload_config():
    """Reimporta app.config para que reconstruya globals con nuevos env."""
    import app.config as cfg
    return importlib.reload(cfg)


def test_data_dir_default_es_repo_data(tmp_path, monkeypatch):
    monkeypatch.delenv("NUTRI_DATA_DIR", raising=False)
    cfg = _reload_config()
    assert cfg.DATA_DIR.name == "data"


def test_data_dir_override_por_env(tmp_path, monkeypatch):
    monkeypatch.setenv("NUTRI_DATA_DIR", str(tmp_path / "custom_data"))
    cfg = _reload_config()
    assert cfg.DATA_DIR == tmp_path / "custom_data"
    assert cfg.DATA_DIR.exists()


def test_api_port_lee_PORT_de_railway(monkeypatch):
    monkeypatch.setenv("PORT", "3131")
    monkeypatch.delenv("NUTRI_API_PORT", raising=False)
    cfg = _reload_config()
    assert cfg.API_PORT == 3131


def test_api_port_fallback_a_nutri_api_port(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.setenv("NUTRI_API_PORT", "9999")
    cfg = _reload_config()
    assert cfg.API_PORT == 9999


def test_cors_origins_parseado_de_csv(monkeypatch):
    monkeypatch.setenv(
        "NUTRI_CORS_ORIGINS",
        "https://app.vercel.app, http://localhost:4200,",
    )
    cfg = _reload_config()
    assert cfg.API_CORS_ORIGINS == [
        "https://app.vercel.app",
        "http://localhost:4200",
    ]


def test_storage_backend_local_por_default(monkeypatch):
    import app.config as cfg
    monkeypatch.setattr(cfg, "SUPABASE_URL", None)
    monkeypatch.setattr(cfg, "SUPABASE_SERVICE_KEY", None)
    assert cfg.storage_backend_activo() == "local"


def test_storage_backend_supabase_cuando_hay_credenciales(monkeypatch):
    import app.config as cfg
    monkeypatch.setattr(cfg, "SUPABASE_URL", "https://x.supabase.co")
    monkeypatch.setattr(cfg, "SUPABASE_SERVICE_KEY", "sk_test_xxx")
    assert cfg.storage_backend_activo() == "supabase"


def test_security_issues_detecta_faltantes_en_produccion(monkeypatch):
    monkeypatch.setenv("NUTRI_ENV", "production")
    monkeypatch.setenv("NUTRI_ENABLE_API_DOCS", "true")
    monkeypatch.setenv("NUTRI_AUTH_COOKIE_SECURE", "false")
    monkeypatch.setenv("NUTRI_AUTH_COOKIE_SAMESITE", "lax")
    monkeypatch.delenv("ADMIN_INITIAL_PASSWORD", raising=False)
    cfg = _reload_config()
    issues = cfg.security_config_issues()
    assert any("NUTRI_ENABLE_API_DOCS=false" in i for i in issues)
    assert any("NUTRI_AUTH_COOKIE_SECURE=true" in i for i in issues)
    assert any("NUTRI_AUTH_COOKIE_SAMESITE=none" in i for i in issues)
    assert any("ADMIN_INITIAL_PASSWORD" in i for i in issues)


def test_security_issues_vacio_con_config_segura_en_produccion(monkeypatch):
    monkeypatch.setenv("NUTRI_ENV", "production")
    monkeypatch.setenv("NUTRI_ENABLE_API_DOCS", "false")
    monkeypatch.setenv("NUTRI_AUTH_COOKIE_SECURE", "true")
    monkeypatch.setenv("NUTRI_AUTH_COOKIE_SAMESITE", "none")
    monkeypatch.setenv("ADMIN_EMAIL", "admin@test.local")
    monkeypatch.setenv("ADMIN_INITIAL_PASSWORD", "AdminPass123!_Prod")
    monkeypatch.setenv("NUTRI_CORS_ORIGINS", "https://app.vercel.app")
    cfg = _reload_config()
    assert cfg.security_config_issues() == []
