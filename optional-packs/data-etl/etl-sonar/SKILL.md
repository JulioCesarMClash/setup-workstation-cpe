---
name: etl-sonar
description: >
  Analizador estático de calidad tipo SonarQube para proyectos ETL Python hexagonales.
  Detecta bugs silenciosos, violaciones hexagonales, code smells, DQS violations y dead code.
  Trigger: cuando el usuario pide auditoría, "busca bugs", "revisa el código", "code quality", "sonar", o al iniciar trabajo en el ETL.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
allowed-tools: Read, Bash, Grep, Glob
---

## When to Use

- Usuario pide auditoría de código ETL
- Antes de un release o PR de cambios grandes
- Después de refactorings cross-layer
- Al incorporar código nuevo a la arquitectura hexagonal

## Severity Levels

| Level    | Criterio                                                          |
|----------|-------------------------------------------------------------------|
| CRITICAL | Rompe arquitectura hexagonal o produce bugs silenciosos en prod  |
| HIGH     | Viola SOLID, stubs sin ABC, private API crossing, silent except  |
| MEDIUM   | Code smells, typing deprecated, DQS violations en tests          |
| LOW      | Missing `__all__`, duplicated logic, minor inconsistencies        |
| INFO     | Cosmético, sugerencias de mejora sin impacto funcional           |

---

## Analysis Layers

### L1 — Domain (`etl/domain/`)
- [ ] Ningún import de pandas, psycopg2, pymysql, sqlalchemy, requests
- [ ] Dataclasses con tipos completos (sin `Optional` de `typing` — usar `X | None`)
- [ ] Todos los campos del dominio coinciden con lo que usan los pipelines
- [ ] Sin lógica de negocio que acceda a DB o filesystem

### L2 — Ports (`etl/ports/`)
- [ ] Clases solo ABC puras — sin imports de infraestructura
- [ ] Sin `import pandas as pd` en puertos
- [ ] Todos los métodos abstractos tienen type hints completos
- [ ] Ports solo dependen de dominio + stdlib

### L3 — Adapters (`etl/adapters/`)
- [ ] Cada adapter hereda de su Port/ABC correspondiente
- [ ] Ningún stub con todos los métodos en `raise NotImplementedError`
- [ ] No importa private functions (`_nombre`) de otros módulos
- [ ] Manejo explícito de errores (no bare `except Exception: pass`)
- [ ] Sin hardcoded paths relativos al CWD

### L4 — Application (`etl/application/`)
- [ ] Use cases NO instancian adaptadores concretos internamente
- [ ] Dependencias inyectadas por constructor, no importadas
- [ ] DTOs con type hints completos
- [ ] Sin imports de `etl.adapters.*` en use cases

### L5 — Pipelines (`etl/pipelines/`, `etl/pipelines/services/`)
- [ ] Sin bare `except Exception: pass` sin log
- [ ] `except Exception:` re-raise o log explícito, nunca silencioso
- [ ] Paths de archivos usando `Path(__file__).resolve()` no CWD-relative
- [ ] Sin `from typing import Dict/List/Tuple` — usar builtins Python 3.10+

### L6 — Scripts (`etl/scripts/`)
- [ ] Sin lógica de negocio — solo orquestación
- [ ] Dialecto no computado dos veces con lógica divergente
- [ ] `except Exception:` siempre con `raise` o log antes de continuar

### L7 — Tests (`etl/tests/`)
- [ ] Sin `assert result is not None` como validación primaria (DQS)
- [ ] Sin `assert len(x) > 0` — usar conteo exacto
- [ ] Sin `.any()` como sustituto de cardinalidad
- [ ] Idempotencia verificada (dos runs, mismo resultado)
- [ ] Reconciliación matemática presente: `sum(parts) == total`

---

## Rules Catalog

| ID     | Layer      | Severity | Rule                                              | Fix |
|--------|------------|----------|---------------------------------------------------|-----|
| ETL-01 | Application | CRITICAL | Use case importa adapter concreto                | Inyectar port por constructor |
| ETL-02 | Ports       | CRITICAL | `import pandas` en archivo de puerto             | Mover a adapter; port usa `Any` o `Sequence` |
| ETL-03 | Adapters    | HIGH     | Adapter no hereda de su ABC/Port                 | Agregar `(WarehouserRepository)` etc. en class def |
| ETL-04 | Adapters    | HIGH     | Todos los métodos son `raise NotImplementedError`| Implementar o marcar como `@abstractmethod` en ABC |
| ETL-05 | Adapters    | HIGH     | Import de función privada (`_nombre`) cross-module| Hacer pública la función o mover a shared util |
| ETL-06 | Pipelines   | HIGH     | `except Exception: pass` o `except Exception: return`| Agregar `logging.warning(...)` antes del pass |
| ETL-07 | Pipelines   | HIGH     | `Path("etl/...")` hardcoded relativo al CWD      | `Path(__file__).resolve().parents[N] / "..."` |
| ETL-08 | Domain      | MEDIUM   | `from typing import Optional/List/Dict`          | Reemplazar con `X \| None`, `list`, `dict` |
| ETL-09 | Domain      | MEDIUM   | Campo de dominio faltante (presente en pipeline) | Agregar al dataclass con tipo correcto |
| ETL-10 | Ports       | MEDIUM   | Método abstracto sin type hints                  | Agregar `-> ReturnType` y tipos en params |
| ETL-11 | Tests       | MEDIUM   | `assert result is not None`                      | Reemplazar con assert de valor exacto o estructura |
| ETL-12 | Tests       | MEDIUM   | `assert x.any()` sin conteo exacto               | `assert (df["col"] == val).sum() == expected_n` |
| ETL-13 | Scripts     | LOW      | Dialecto computado dos veces con lógica diferente| Unificar en una función `_resolve_dialect(conn)` |
| ETL-14 | Pipelines   | LOW      | Sin `__all__` en módulo de helpers compartidos   | Agregar `__all__ = [...]` explícito |
| ETL-15 | Domain      | LOW      | Tipo `bool` en dominio pero pipeline usa `0/1`   | Normalizar en pipeline antes de construir dominio |
| ETL-16 | Adapters    | INFO     | `from typing import Dict` en adapter             | Reemplazar con builtin `dict` |
| ETL-17 | Scripts/Adapters | CRITICAL | `ALTER TABLE ... (DISABLE\|ENABLE) TRIGGER` SQL crudo en script o adapter — bypassea triggers para TODAS las conexiones concurrentes a la tabla | Usar `SET session_replication_role = 'replica'`/`'origin'` (scoped a la sesión) en lugar de ALTER TABLE |
| ETL-18 | Scripts     | HIGH     | Script en `scripts/` hace INSERT/UPDATE/DELETE sobre `audit.historical_records` o `audit.ingest_log` sin llamar `try_acquire_folder_lock`/`folder_lock` en ningún punto del archivo — riesgo de doble escritura concurrente con `sync_drive.py` | Envolver la lógica de escritura en `with folder_lock(repo, folder_id):` de `scripts/_folder_utils.py` |
| ETL-19 | Scripts     | HIGH     | Script define su propia función delete+clear (patrón `def _delete.*records` o similar) sobre `historical_records`/`ingest_log`, en lugar de usar `PgHistoricalRepo.reset_file()` | Reemplazar con `repo.reset_file(drive_file_id)` para el purge atómico single-transaction (H2.3). Excepción documentada: `scripts/ingest_mensual.py::_delete_mensual_records` (N2-exempt — delete por período, no por archivo; documentado en su docstring de módulo) |

---

## Output Format

Al ejecutar la auditoría, reportar en esta estructura:

```
## ETL-SONAR REPORT — <fecha>

### CRITICAL (N)
- [ETL-01] etl/application/use_cases/load_facts.py:3 — Use case importa SqlSourceReader directamente
  Fix: Inyectar SourceReaderPort por constructor en LoadFactsUseCase.__init__

### HIGH (N)
- [ETL-03] etl/adapters/mariadb_warehouse.py:1 — MariaDbWarehouse no hereda de WarehouseRepository
  Fix: class MariaDbWarehouse(WarehouseRepository):

### MEDIUM (N) ...
### LOW (N) ...
### INFO (N) ...

---
Total: N hallazgos | CRITICAL: N | HIGH: N | MEDIUM: N | LOW: N | INFO: N
Suite: N passed — estado previo a fix
```

---

## Execution Protocol

1. Leer `CLAUDE.md` para verificar Data Quality Shield activo
2. Auditar por layer en orden: Domain → Ports → Adapters → Application → Pipelines → Scripts → Tests
3. Para cada capa: usar `rg` y `Read` para inspeccionar imports, firmas y excepciones
4. Cruzar hallazgos contra Rules Catalog
5. Reportar con output format arriba
6. Para cada CRITICAL/HIGH: proponer el fix concreto (línea + cambio mínimo)
7. Preguntar al usuario: ¿implemento los fixes? ¿cuáles primero?

## Commands

```bash
# Verificar imports prohibidos en domain/ports
rg "import pandas|import pymysql|import psycopg2|from etl.adapters" etl/domain/ etl/ports/

# Buscar adapters sin herencia de ABC
rg "^class [A-Z]" etl/adapters/ --multiline

# Buscar bare excepts silenciosos
rg "except Exception:\s*$|except Exception:\s*pass" etl/ -n

# Verificar DQS violations en tests
rg "assert.*is not None|assert.*> 0|\.any\(\)" etl/tests/ -n

# Buscar deprecated typing imports
rg "from typing import (Optional|List|Dict|Tuple|Iterable)" etl/ -n

# ETL-17: ALTER TABLE ... DISABLE/ENABLE TRIGGER crudo (bypass global de triggers)
rg -n "ALTER TABLE.*(DISABLE|ENABLE) TRIGGER" scripts/ src/

# ETL-18: escrituras a historical_records/ingest_log sin folder_lock (two-step check)
rg -l "historical_records|ingest_log" scripts/*.py
# Para cada archivo del listado anterior, verificar que NO aparezca en:
rg -l "folder_lock|try_acquire_folder_lock" scripts/*.py

# ETL-19: funciones _delete*records propias en vez de repo.reset_file()
rg -n "def _delete.*records" scripts/*.py
# Cualquier match que NO sea scripts/ingest_mensual.py es violación

# Run suite completa
pytest etl/tests/ -q --tb=short
```

## Scope

Esta skill cubre el proyecto `ELT_analisis_Script`.
Stack: Python 3.12 · pandas · pytest · PostgreSQL/MariaDB · Hexagonal Architecture · dbutils.
DQS Shield: obligatorio — ver `000_Gobernanza_Data_Quality_Shield.md`.
