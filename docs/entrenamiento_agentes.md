# Entrenamiento y validacion de los agentes

Los agentes (SchemaScout, MappingArchitect, KpiDesigner, ReportDesigner) NO se
"entrenan" con fine-tuning: son Gemini via Pydantic AI. "Entrenar" aqui = iterar
sus **prompts + ejemplos** usando casos de referencia deterministicos como
verdad, y **validar** midiendo que tan cerca queda su propuesta de esa verdad.

## Verdad de referencia (golden cases)

Ya verificados de forma deterministica (el motor reproduce los KPIs correctos):

| Caso | Profile de referencia | Fixtures | Entregable correcto |
|---|---|---|---|
| PRE CORTE vs FLASH | `profiles/pre_corte_v1.json` | `tests/fixtures/PRE_CORTE_muestra.xlsx`, `FLASH_muestra.csv`, `homologacion.xlsx` | `export_cumplimiento_xlsx` (5-6 hojas) |
| CEN vs SAP | `profiles/cen_vs_sap_v1_borrador.json` | `tests/fixtures/cen/cen_junio_muestra.xlsx`, `sap_junio_muestra.xlsx` | `render_excel` + `render_pbip` |

Estos son la "verdad" contra la que se puntuan los agentes. El proceso
predefinido del catalogo usa exactamente estos profiles/pipelines, asi que lo
que el analista recibe es siempre el resultado verificado.

## Respuestas estandar de la entrevista (contexto de negocio)

Cuando el eval corre a los agentes, estas son las respuestas de negocio que un
analista daria (documentadas en `scripts/e2e_flujo_cen.py`):

- **CEN vs SAP**: grano = linea de producto por orden; join CEN "Numero de la
  Orden de compra" vs SAP col56 y CEN "Codigo item proveedor" vs SAP col40
  (normalizar espacios y ceros); real = cantidad entregada SAP (col42);
  devoluciones = tipo_operacion DEVOLUCIONES (col13) con motivo col62, aparte;
  ventas sin orden CEN = canales TAT/PUNTOS PROPIOS/EMPLEADOS (no son error).
- **PRE CORTE vs FLASH**: plan = `notificado` del RESUMEN; real = `Cantidad
  Neta` del FLASH del dia; join por codigo SAP MATERIAL; FLASH se agrupa por
  material y se filtra por la fecha de produccion.

## Validacion (el gate)

```
venv\Scripts\python.exe scripts/validar_agentes.py            # ambos casos
venv\Scripts\python.exe scripts/validar_agentes.py --caso cen
venv\Scripts\python.exe scripts/validar_agentes.py --caso pre_corte
```

Cada eval (`scripts/eval_reconstruccion_*.py`) corre a los agentes REALES
(requiere `GEMINI_API_KEY`), y puntua la propuesta **por semantica** (a que
columnas del archivo apunta cada pieza), no por nombres:

- Llaves de cruce correctas (material; o orden+item en CEN).
- Join outer, grano ajustado con group_by.
- KPI de cumplimiento real/plan; devoluciones aparte (CEN).
- Nivel de servicio y desgloses declarados (CEN).
- Reporte con portada + no_cruzados.

**Gate: score >= 80%.** El resultado se registra en `rubrica.md`.

## Ciclo de mejora ("entrenamiento")

1. Correr `validar_agentes.py` y leer los `[FAIL]` + las preguntas que emiten.
2. Ajustar los prompts en `app/agents/crew.py` (heuristicas, ejemplos, el
   principio de entrevista) para cubrir el fallo, sin cambiar el motor.
3. Re-correr el eval hasta pasar el gate en ambos casos.
4. Registrar el score y el costo (telemetria LLM) en `rubrica.md`.

## Anadir un caso nuevo

1. Verificar primero el resultado de forma deterministica (profile a mano +
   numeros comprobados), como se hizo con PRE CORTE y CEN.
2. Crear `scripts/eval_reconstruccion_<caso>.py` con los checks semanticos.
3. Registrarlo en `CASOS` de `scripts/validar_agentes.py`.

## Nota importante

La entrevista LLM es **no deterministica**: cada corrida puede variar. Por eso
el uso recurrente en produccion se hace con los **procesos predefinidos**
(deterministicos, verificados). La entrevista con agentes es para casos
**nuevos** o de correccion, y el eval mide su calidad antes de promover un
profile a predefinido.
