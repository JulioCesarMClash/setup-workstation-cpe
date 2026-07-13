---
name: git-branch-strategy
description: >
  Define y aplica la estrategia de ramas Git: 3 ramas permanentes (main/staging/develop),
  ramas de trabajo desde develop, jerarquía epic/task/subtask dentro de develop,
  gates de promoción develop→staging (unit tests) y staging→main (DQS + integration tests),
  y reglas de PR con aprobación obligatoria de equipo.
  Trigger: operaciones Git, branch strategy, PR, merge entre ambientes, gate de promoción.
license: Apache-2.0
metadata:
  author: julio-martinez
  version: "2.0"
  tier: MID-HIGH
  model: claude-sonnet-4-6
  analysis: >
    v1.0: Verificado por Scrum Master + Dev Senior via Gemma4:31b.
    v2.0: Extendido con modelo de 3 ambientes y gates de promoción (2026-06-05).
---

# Git Branch Strategy — Ambientes + Jerarquía

> Gobernanza completa en Obsidian: `000_SISTEMA_OPERATIVO/050_Estandar_Git_Workflow_Ambientes.md`

---

## Modelo de ambientes (obligatorio en todo repositorio)

```
develop  →  staging  →  main
(integración)  (QA)  (producción)
```

### Ramas permanentes

| Rama | Base de trabajo | Puede recibir push directo |
|------|----------------|---------------------------|
| `main` | No | PROHIBIDO — solo PR desde `staging` |
| `staging` | No | PROHIBIDO — solo PR desde `develop` |
| `develop` | Sí — todas las ramas de trabajo | Solo releases/hotfixes críticos |

### Ramas de trabajo (todas salen de `develop`, todas mergean a `develop`)

```
feature/{JIRA-KEY}-{slug}
fix/{JIRA-KEY}-{slug}
devops/{JIRA-KEY}-{slug}
refactor/{JIRA-KEY}-{slug}
docs/{JIRA-KEY}-{slug}
```

---

## Gate 1 — develop → staging (todos bloqueantes)

| ID | Check | Cómo verificar |
|----|-------|----------------|
| DSG-01 | Linting + tipado sin errores (`ruff`, `mypy`) | CI / `ruff check . && mypy .` |
| DSG-02 | 100% unit tests en verde | `pytest` sin failures |
| DSG-03 | ≥80% cobertura en módulos nuevos/modificados | `pytest --cov` |
| DSG-04 | Branch actualizado con `develop` (rebase hecho) | `git log develop..HEAD` |
| DSG-05 | ≥1 aprobación de miembro del equipo del repo | GitHub/GitLab review |
| DSG-06 | Commits semánticos + `Refs: JIRA-KEY` | Review del PR |
| DSG-07 | Sin TODOs/FIXMEs sin ticket en código nuevo | `rg "TODO|FIXME|HACK" src/` |

Tipo de merge: **squash merge**

---

## Gate 2 — staging → main (todos bloqueantes)

| ID | Check | Cómo verificar |
|----|-------|----------------|
| SMG-01 | Gate 1 completo (DSG-01 a DSG-07) | Evidencia del PR a staging |
| SMG-02 | DQS: cardinalidad exacta por dimensión | `pytest` — no `> 0`, no `any()` |
| SMG-03 | DQS: reconciliación matemática `sum(partes)==total` | `pytest` — reconciliación |
| SMG-04 | DQS: edge cases (nulls, vacíos, cero, strings) | `pytest` — casos negativos |
| SMG-05 | DQS: idempotencia — doble run sin duplicados | `pytest` — doble ejecución |
| SMG-06 | DQS: sin orphan rows post replace/re-run | `pytest` — FK/batch_id assert |
| SMG-07 | Tests de integración en verde (BD real) | `pytest tests/integration/` |
| SMG-08 | Smoke tests de endpoints en staging | `pytest tests/api/` o curl |
| SMG-09 | Suite completa sin regresiones | `pytest` full |
| SMG-10 | ≥1 aprobación de miembro del equipo del repo | GitHub/GitLab review |

Tipo de merge: **merge commit** (preservar historial de staging)

---

## Reglas de PR (todos los niveles)

- Auto-aprobación: **PROHIBIDA**
- Branch debe estar actualizado antes de pedir review
- PR sin tests nuevos en código de lógica: **se rechaza**
- Descripción obligatoria: qué cambia, por qué, cómo probarlo, `Refs: JIRA-KEY`

---

## Anti-patterns críticos

| Prohibido | Consecuencia |
|-----------|-------------|
| `git push --force` a `main`/`staging` | Rollback + revisión de incidente |
| Push directo a `main` o `staging` | Revertir + PR retroactivo |
| Auto-aprobación | PR invalidado |
| Merge sin tests en lógica nueva | Bloquea Gate 1 |
| Skipear DQS en pipelines de datos | Incidente crítico de datos |
| Commitear `.env` o credenciales | Rotación inmediata de credenciales + `git filter-repo` |
| Commitear logs de runtime | `git rm --cached` + entrada en `.gitignore` |
| Repo sin `.gitignore` | Bloquea el Gate 1 (DSG-08) |

---

## .gitignore — Reglas del Skill

### Checklist al crear un repositorio nuevo (obligatorio)

- [ ] Copiar template: `cp ~/.skills/git-branch-strategy/assets/gitignore-python-hexagonal.txt .gitignore`
- [ ] Crear `secrets/.gitkeep` para preservar estructura del directorio
- [ ] Crear `.env.example` con todas las variables necesarias (sin valores reales)
- [ ] Verificar `git status` — no debe mostrar `.venv/`, `__pycache__/`, ni ningún `.env`
- [ ] El `.gitignore` va en el **primer commit** del repositorio — nunca después

### Regla de oro del .gitignore

```
¿Otro equipo necesita este archivo para correr el proyecto? → commitear
¿El archivo contiene un secreto, contraseña o token?       → NUNCA commitear
¿Es un log o artefacto generado en ejecución?              → NO commitear
¿Es un .md?                                                → SÍ commitear
```

### Reparar archivo sensible ya commiteado

```bash
git rm --cached <archivo>       # sacar del tracking
echo "<archivo>" >> .gitignore  # ignorar para siempre
git commit -m "chore: remove sensitive file from tracking\n\nRefs: JIRA-KEY"
# Si ya fue pusheado: ROTAR CREDENCIALES INMEDIATAMENTE
```

### Recursos

- **Template**: `assets/gitignore-python-hexagonal.txt`
- **Gobernanza completa**: `000_SISTEMA_OPERATIVO/050_Estandar_Git_Workflow_Ambientes.md` — sección `.gitignore`

---

## Análisis de roles (Scrum Master + Dev Senior)

> Ejecutado via `gemma4:31b` antes de definir la estrategia.

### Veredicto Scrum Master — ✅ Aprobar con condiciones
- **Ventaja:** Trazabilidad espejo entre jerarquía Jira y Git. Visibilidad real del progreso por épica.
- **Riesgo:** Merge Hell al integrar múltiples tasks simultáneas hacia la épica. Overhead burocrático si se aplica a todas las tareas sin distinción.
- **Condición:** Subtask-branch solo para tareas con sub-tareas complejas (>2 días). Definir TTL obligatorio por nivel. Sincronización de merges durante sprint review.

### Veredicto Dev Senior — ✅ Aprobar con condiciones
- **Ventaja:** Aislamiento claro por unidad de trabajo. Rollback quirúrgico por nivel. Historial limpio si se usa squash merge.
- **Riesgo:** Branch drift si las ramas viven demasiado sin rebase. Conflictos compuestos al propagar subtask→task→epic. CI/CD se complica si no hay claridad sobre qué rama es desplegable.
- **Condición:** Rebase frecuente desde la rama padre. Squash merge obligatorio subtask→task. Epic-branch nunca es desplegable directamente; solo main.

---

## Pregunta obligatoria antes de crear cualquier rama

Antes de crear una rama, preguntar:

> **"¿Este ticket necesita casarse con un branch de desarrollo?"**

| Respuesta | Acción |
|---|---|
| **Sí** | Crear rama con patrón de nivel correspondiente |
| **No** | Registrar como contexto en Jira únicamente. Sin branch. |
| **Sin ticket** | Usar fallback `{tipo}/{slug}` y advertir falta de trazabilidad |

---

## Jerarquía de ramas

```
main (o develop)
 └── epic/{EPIC-KEY}-{slug}          ← Nivel 1: Épica
       └── feat/{TASK-KEY}-{slug}    ← Nivel 2: Task
             └── fix/{SUB-KEY}-{slug} ← Nivel 3: Sub-task (condicional)
```

---

## Naming por nivel

### Nivel 1 — Epic Branch
```
epic/{EPIC-KEY}-{slug-epica}
```
Ejemplos:
- `epic/DAT-E1-analytics-pipeline`
- `epic/DV-E5-auth-refactor`

**Sale de:** `main` (o `develop` si el proyecto lo usa)  
**Merge hacia:** `main` — solo al cerrar la épica completa

---

### Nivel 2 — Task Branch
```
{tipo}/{TASK-KEY}-{slug-tarea}
```
Ejemplos:
- `feat/DAT-42-carga-incremental`
- `fix/DAT-17-timeout-checkout`
- `refactor/DAT-99-auth-session`

**Sale de:** La epic-branch correspondiente  
**Merge hacia:** La epic-branch — con squash merge

Tipos válidos: `feat`, `fix`, `refactor`, `docs`, `chore`, `ci`, `test`

---

### Nivel 3 — Subtask Branch (condicional)
```
{tipo}/{SUBTASK-KEY}-{slug-subtarea}
```
Ejemplos:
- `feat/DAT-42-1-postgres-connection`
- `feat/DAT-42-2-mapping-schema`

**Sale de:** La task-branch correspondiente  
**Merge hacia:** La task-branch — con squash merge  
**Solo crear si** se cumplen las condiciones del Subtask Gate (ver abajo)

---

## Subtask Gate — cuándo crear nivel 3

Crear subtask-branch **solo si se cumplen al menos 2 de estas condiciones:**

- [ ] La sub-tarea tiene estimación >2 días
- [ ] La sub-tarea tiene un entregable independiente (archivo, módulo, migración)
- [ ] El trabajo de la sub-tarea puede revisarse por separado antes de mergear a la task
- [ ] Hay riesgo real de conflicto con otra sub-tarea de la misma task

**No crear subtask-branch cuando:**
- Es un hotfix o cambio de configuración menor
- La sub-tarea dura <1 día
- Solo hay una sub-tarea en la task

---

## TTL (Time-to-Live) por nivel

| Nivel | TTL máximo | Si se excede... |
|---|---|---|
| subtask-branch | 3 días hábiles | Rebase desde task-branch o cerrrar/mergear |
| task-branch | 1 sprint (2 semanas) | Rebase desde epic-branch o escalar al SM |
| epic-branch | Duración de la épica | Revisión en sprint review; no puede vivir indefinidamente |

---

## Reglas de merge

### Subtask → Task
- **Tipo:** Squash merge
- **Commit message:** `feat(scope): descripción\n\nRefs: SUBTASK-KEY`
- Borrar la rama subtask tras el merge
- Correr tests locales antes del merge

### Task → Epic
- **Tipo:** Squash merge (o merge commit si el historial es valioso)
- **Commit message:** `feat(scope): descripción completa de la task\n\nRefs: TASK-KEY`
- Borrar la rama task tras el merge
- Verificar que `sdd-verify` esté completo para el cambio

### Epic → Develop
- **Tipo:** Merge commit (preservar historial de la épica)
- **Requiere:** PR formal con evidencia de `sdd-verify`, Jira Epic en estado Done
- Borrar la rama epic tras el merge
- Nada va directo a `main`: la promoción `develop → staging → main` sigue el modelo de 3 ambientes (Gate 1 / Gate 2) de forma independiente de la jerarquía Jira
- La epic-branch **nunca se despliega directamente** a producción

---

## Reglas de rebase

- Cada rama debe rebase desde su rama padre **al menos una vez por día** en días activos de desarrollo.
- Antes de abrir un PR de task → epic, rebase obligatorio desde epic.
- Antes de abrir un PR de epic → main, rebase obligatorio desde main.
- Rebase en ramas compartidas requiere coordinación explícita (anunciar en canal del equipo).

---

## Footer de commits (obligatorio con ticket)

Todo commit en una rama con ticket Jira debe incluir:

```
Refs: JIRA-KEY
```

Ejemplo:
```
feat(db): add incremental load logic

Refs: DAT-42
```

---

## Flujo completo de una épica

```
1. Crear epic-branch desde main cuando se inicia la épica
2. Por cada task del sprint:
   a. Preguntar: ¿necesita branch?
   b. Crear task-branch desde epic-branch
   c. (Si aplica Subtask Gate) Crear subtask-branches desde task-branch
   d. Desarrollar, rebasear diario
   e. Squash merge subtask → task
   f. Squash merge task → epic
3. Al cierre de épica: PR epic → develop con evidencia completa (main se alcanza después, vía staging, por el modelo de 3 ambientes)
```

---

## Integración con sdd-tasks

| Estado SDD | Nivel de rama | Acción recomendada |
|---|---|---|
| Task `[ ]` | — | Branch aún no creado |
| Task activa | task-branch abierta | En desarrollo |
| Task `[x]`, verify pendiente | task-branch lista para merge | Abrir PR task → epic |
| Subtask `[ ]` | — | Evaluar Subtask Gate |
| Subtask activa | subtask-branch abierta | En desarrollo |
| Subtask `[x]` | subtask-branch lista | Squash merge → task |

---

## Anti-patterns

- Crear subtask-branch para cada sub-tarea sin pasar por el Subtask Gate.
- Mergear epic → main sin PR ni `sdd-verify`.
- Ramas que superan su TTL sin rebase ni resolución.
- Usar `git push --force` en una epic-branch compartida sin coordinación.
- Dejar ramas mergeadas sin borrar.
- Abrir PR desde subtask directamente a main saltándose niveles.
