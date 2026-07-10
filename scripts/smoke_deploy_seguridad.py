from __future__ import annotations

import argparse
import sys

import httpx


def _expect(cond: bool, message: str) -> None:
    if not cond:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test de seguridad post-deploy (Railway/Vercel)."
    )
    parser.add_argument("--base-url", required=True, help="Ej: https://api.up.railway.app")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--origin", default=None, help="Origin esperado para validar CORS")
    parser.add_argument(
        "--allow-docs",
        action="store_true",
        help="Permitir /docs abierto (solo dev).",
    )
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    with httpx.Client(base_url=base, timeout=20.0, follow_redirects=False) as client:
        health = client.get("/health")
        _expect(health.status_code == 200, f"/health debe responder 200, obtuvo {health.status_code}")

        docs = client.get("/docs")
        if args.allow_docs:
            _expect(docs.status_code in {200, 404}, f"/docs inesperado: {docs.status_code}")
        else:
            _expect(docs.status_code in {401, 403, 404}, f"/docs no debe estar publico: {docs.status_code}")

        open_noauth = client.get("/batches")
        _expect(open_noauth.status_code == 401, f"/batches sin auth debe ser 401, obtuvo {open_noauth.status_code}")

        login_headers = {}
        if args.origin:
            login_headers["Origin"] = args.origin
        login = client.post(
            "/auth/login",
            json={"email": args.email, "password": args.password},
            headers=login_headers,
        )
        _expect(login.status_code == 200, f"login fallo: {login.status_code} {login.text}")

        set_cookie = ",".join(login.headers.get_list("set-cookie"))
        lower_cookie = set_cookie.lower()
        _expect("httponly" in lower_cookie, "Cookie de sesion debe incluir HttpOnly")
        _expect("secure" in lower_cookie, "Cookie de sesion debe incluir Secure")
        _expect("samesite=none" in lower_cookie, "Cookie de sesion debe incluir SameSite=None")
        if args.origin:
            allow_origin = login.headers.get("access-control-allow-origin")
            _expect(allow_origin == args.origin, f"CORS reflect esperado {args.origin}, obtuvo {allow_origin}")

        me = client.get("/auth/me")
        _expect(me.status_code == 200, f"/auth/me debe responder 200 tras login, obtuvo {me.status_code}")

        csrf_cookie = client.cookies.get("nutri_csrf")
        _expect(bool(csrf_cookie), "Debe existir cookie CSRF tras login")

        no_csrf = client.post("/batches", json={"nombre": "smoke-sin-csrf"})
        _expect(no_csrf.status_code == 403, f"Mutacion sin CSRF debe ser 403, obtuvo {no_csrf.status_code}")

        with_csrf = client.post(
            "/batches",
            json={"nombre": "smoke-seguridad"},
            headers={"X-CSRF-Token": csrf_cookie},
        )
        _expect(with_csrf.status_code in {200, 201}, f"POST /batches con CSRF fallo: {with_csrf.status_code}")
        payload = with_csrf.json()
        batch_id = payload.get("id")

        if batch_id:
            client.delete(f"/batches/{batch_id}", headers={"X-CSRF-Token": csrf_cookie})

        print("SMOKE_SECURITY_OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"SMOKE_SECURITY_FAIL: {exc}")
        raise SystemExit(1) from exc
