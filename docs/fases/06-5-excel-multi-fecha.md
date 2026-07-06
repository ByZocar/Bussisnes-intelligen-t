# Fase 6.5 — Excel multi-fecha (batch mensual)

**Estado:** completada  
**Fecha de referencia:** 2026-07-06

## Objetivo

Cuando el usuario sube N PRE CORTE del mes contra un FLASH unico, generar:

| Salida | Contenido |
|--------|-----------|
| N x `cumplimiento_YYYYMMDD.xlsx` | Daily por fecha de produccion |
| 1 x `cumplimiento_consolidado_*` | Rango completo + hoja **Por_Semana** |
| 1 x `cumplimiento_batch_*.zip` | Consolidado + todos los dailies |

## Mejora visual

Agrupacion de `fecha_produccion` en tablas: la fecha aparece solo en la
primera fila del grupo; borde medium naranja al cambio de grupo (sin merge de
celdas, compatible con filtros Excel).

## API publica

- `export_cumplimiento_xlsx(desde, hasta, ...)`
- `export_cumplimiento_diario(fecha, ...)`
- `export_batch_completo(desde, hasta, output_dir, ...)`

## Nota

Los dailies **no** incluyen hoja Por_Semana (solo aporta en consolidado).
