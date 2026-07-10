"""Runner unico de VALIDACION de agentes contra la verdad de referencia.

Corre los evals de reconstruccion (PRE CORTE y CEN vs SAP): le da a los agentes
REALES solo los archivos + el brief, y compara su propuesta contra los profiles
deterministicos verificados. Es el "gate" que dice si los agentes lo hacen bien.

Requiere GEMINI_API_KEY en .env (usa Gemini de pago; cada corrida cuesta unos
centavos y tarda ~1-2 min por caso).

Uso:
    venv\\Scripts\\python.exe scripts/validar_agentes.py
    venv\\Scripts\\python.exe scripts/validar_agentes.py --caso cen
    venv\\Scripts\\python.exe scripts/validar_agentes.py --caso pre_corte
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CASOS = {
    "pre_corte": "scripts/eval_reconstruccion_pre_corte.py",
    "cen": "scripts/eval_reconstruccion_cen.py",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validacion de agentes vs verdad de referencia.")
    parser.add_argument("--caso", choices=list(CASOS) + ["todos"], default="todos")
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()

    casos = list(CASOS) if args.caso == "todos" else [args.caso]
    resultados: list[tuple[str, int]] = []
    for caso in casos:
        print("\n" + "#" * 70)
        print(f"# VALIDACION AGENTES: {caso}")
        print("#" * 70)
        p = subprocess.run([args.python, CASOS[caso]], cwd=str(ROOT))
        resultados.append((caso, p.returncode))

    print("\n" + "=" * 70)
    print("SCORECARD DE VALIDACION DE AGENTES")
    print("=" * 70)
    for caso, code in resultados:
        estado = "PASA (>=80%)" if code == 0 else "NO PASA (<80%)"
        print(f"  {caso:12s} -> {estado}")
    todos_ok = all(code == 0 for _, code in resultados)
    print("-" * 70)
    print("RESULTADO:", "TODOS PASAN" if todos_ok else "HAY CASOS POR MEJORAR")
    return 0 if todos_ok else 1


if __name__ == "__main__":
    sys.exit(main())
