---
name: jira-ticket-hierarchy
description: >
  Crea y gestiona la jerarquía completa de tickets Jira en 5 tipos:
  Épica → Task / Spike / Bug → Sub-task. Paso a paso, repo-agnóstico.
  Incluye nomenclatura estandarizada, árbol de decisión, campos obligatorios,
  label helper con taxonomía y casamiento con rama Git (git-branch-strategy).
  Genera el jira_epic_tree.json para BUNKER_TOOLS si está disponible.
license: Apache-2.0
metadata:
  author: julio-martinez
  version: "1.0"
  tier: MID-HIGH
  model: claude-sonnet-4-6
  audit: "Revisado por Gemma4:31b (rol SDD auditor). Gap detectado en skill anterior: solo generaba reportes cosméticos sin garantizar trazabilidad entre niveles."
  related_skills:
    - git-branch-strategy
    - senior-vcs-commander
    - jira-evidence-formatter
    - generic-jira-subtask-reporter
    - ponytail
---

# Jira Ticket Hierarchy — Creación Paso a Paso

## Paso 0 — Detectar PROJECT_KEY (repo-agnóstico)

Antes de crear cualquier ticket, detectar el `PROJECT_KEY` del repositorio en este orden:

| Fuente | Qué leer | Campo |
|---|---|---|
| `CLAUDE.md` | Primera línea de proyecto o encabezado | Nombre del proyecto |
| `package.json` | `"name"` | Nombre del paquete |
| `pyproject.toml` | `[project] name` | Nombre del proyecto |
| `pom.xml` | `<artifactId>` | ID del artefacto |
| `.git/config` | `[remote "origin"] url` | Nombre del repo |
| **Preguntar al usuario** | Si ninguna fuente aplica | Pedir PROJECT_KEY explícitamente |

El `PROJECT_KEY` debe tener entre 2 y 6 caracteres en mayúsculas (ej. `DAT`, `DV`, `API`, `AUTH`).

Si hay un `PROJECT_KEY` de Jira ya configurado en el entorno (ej. variable de entorno, `.env`), usarlo directamente.

---

## Paso 1 — Árbol de decisión: ¿Qué tipo de ticket crear?

```
¿Es un objetivo estratégico que abarca múltiples sprints y varias entregas?
  └─ SÍ → ÉPICA

¿Es trabajo planificado con un entregable concreto dentro de una épica?
  └─ SÍ → TASK

¿Es una investigación o exploración antes de comprometerse a una solución?
  └─ SÍ → SPIKE

¿Es un defecto o comportamiento inesperado en producción o QA?
  └─ SÍ → BUG

¿Es una unidad de trabajo específica que forma parte de una Task?
  └─ SÍ → SUB-TASK
```

**Regla de oro:** Si dudas entre Task y Spike, pregunta: *"¿Ya sabemos cómo hacerlo?"*
- Sí → Task
- No → Spike (investigar primero, task después)

---

## Paso 2 — Nomenclatura por tipo de ticket

### ÉPICA

```
[{PROJECT_KEY}] {SISTEMA}: {OBJETIVO_ESTRATÉGICO}
```

| Campo | Descripción | Ejemplo |
|---|---|---|
| `PROJECT_KEY` | Key del proyecto Jira | `DAT` |
| `SISTEMA` | Componente o dominio afectado | `ETL`, `API`, `Auth`, `Frontend` |
| `OBJETIVO_ESTRATÉGICO` | Meta de negocio en infinitivo | `Migrar pipeline a arquitectura incremental` |

**Ejemplo completo:**
> `[DAT] ETL: Migrar pipeline a arquitectura incremental`

---

### TASK

```
[{PROJECT_KEY}] {SISTEMA} | {ENTREGABLE_CONCRETO}
```

| Campo | Descripción | Ejemplo |
|---|---|---|
| `PROJECT_KEY` | Key del proyecto | `DAT` |
| `SISTEMA` | Componente afectado (mismo que la épica padre) | `ETL` |
| `ENTREGABLE_CONCRETO` | Acción + resultado en infinitivo | `Implementar carga incremental desde PostgreSQL` |

**Ejemplo completo:**
> `[DAT] ETL | Implementar carga incremental desde PostgreSQL`

**Ticket padre requerido:** Épica

---

### SPIKE

```
[{PROJECT_KEY}] SPIKE | {PREGUNTA_CLAVE_A_RESPONDER}
```

| Campo | Descripción | Ejemplo |
|---|---|---|
| `PROJECT_KEY` | Key del proyecto | `DAT` |
| `PREGUNTA_CLAVE_A_RESPONDER` | Pregunta concreta que debe quedar respondida al cerrar el ticket | `¿Cuál es la mejor estrategia de particionamiento para BigQuery vs Redshift?` |

**Ejemplo completo:**
> `[DAT] SPIKE | ¿Cuál es la mejor estrategia de particionamiento para BigQuery?`

**Regla:** Un Spike tiene timebox fijo (máx. 2 días). Al cerrarlo, el output es una decisión documentada, no código. Puede o no tener rama Git según complejidad.

**Ticket padre requerido:** Opcional (puede ser hijo de una Épica o estar suelto)

---

### BUG

```
[{PROJECT_KEY}] BUG | {COMPONENTE}: {SÍNTOMA_OBSERVABLE}
```

| Campo | Descripción | Ejemplo |
|---|---|---|
| `PROJECT_KEY` | Key del proyecto | `DAT` |
| `COMPONENTE` | Módulo, servicio o capa donde ocurre | `ETL`, `API-Gateway`, `Dashboard` |
| `SÍNTOMA_OBSERVABLE` | Qué se ve mal — no la causa | `Registros duplicados en carga nocturna` |

**Ejemplo completo:**
> `[DAT] BUG | ETL: Registros duplicados en carga nocturna`

**Regla:** El síntoma describe el comportamiento visto, no la causa técnica. La causa va en la descripción.

**Ticket padre requerido:** Opcional. Asociar a la épica correspondiente si el bug pertenece a una funcionalidad en desarrollo.

---

### SUB-TASK

```
[{PROJECT_KEY}] {TASK_ID} > {ACCIÓN_ESPECÍFICA}
```

| Campo | Descripción | Ejemplo |
|---|---|---|
| `PROJECT_KEY` | Key del proyecto | `DAT` |
| `TASK_ID` | ID del ticket Task padre | `DAT-42` |
| `ACCIÓN_ESPECÍFICA` | Paso técnico concreto en infinitivo | `Configurar conexión PostgreSQL con SSL` |

**Ejemplo completo:**
> `[DAT] DAT-42 > Configurar conexión PostgreSQL con SSL`

**Ticket padre requerido:** Task (obligatorio — una sub-task sin task padre no existe)

---

## Paso 3 — Campos obligatorios por tipo

Completar SIEMPRE estos campos en la descripción del ticket:

### Todos los tipos

| Campo | Contenido |
|---|---|
| **Contexto** | Por qué existe este ticket. Una oración. |
| **Objetivo** | Qué debe estar hecho al cerrar el ticket. |
| **Criterios de Aceptación** | Lista verificable, en lenguaje no técnico. |
| **Riesgos / Dependencias** | Qué puede bloquearlo o afectarlo. |

### Campos adicionales por tipo

| Tipo | Campos extra |
|---|---|
| Épica | Alcance (qué entra y qué NO entra), lista de Tasks esperadas, start date, due date |
| Task | Rama Git asociada (una vez creada), lista de Sub-tasks si aplica, start date, due date, story points |
| Spike | Pregunta central, timebox en días, formato del output esperado (ADR, nota, comentario), start date, due date |
| Bug | Pasos para reproducir, comportamiento esperado vs. actual, entorno (dev/qa/prod), severidad, start date, due date |
| Sub-task | ID de la Task padre, entregable específico, start date, due date, story points |

---

## Paso 3.5 — Gate Ponytail: ¿este campo necesita existir?

Antes de llenar un campo opcional (Riesgos/Dependencias, Alcance, lista de Sub-tasks esperadas), preguntar:

> **¿Este campo aporta algo que el lector necesita, o es relleno?**

- Sin riesgos reales → `Ninguno identificado`, una línea. No inventar riesgos para no dejar la sección vacía.
- Sin dependencias → `Ninguna`. No listar dependencias hipotéticas "por si acaso".
- Alcance sin exclusiones relevantes → omitir la lista de "qué NO entra" si ya es obvio por el título.

Mismo principio de [[ponytail]] aplicado a texto: el campo más corto que sigue siendo correcto es el correcto.

---

## Paso 3.6 — Campos operacionales de Jira

Después de crear el ticket y llenar la descripción, preguntar por estos campos operacionales que van fuera de la descripción y se setean como fields de la API:

### Story points (`customfield_10016`)

| Tipo de ticket | Story points |
|---|---|
| Subtarea | 3 |
| Task | 1 |
| Spike | 5 |
| Bug | 2 |
| Épica | No asignar — se calcula por suma de tasks |

Si el proyecto usa una convención distinta, preguntar al usuario.

### Fechas (`customfield_10015` Start date, `duedate` Due date)

Preguntar SIEMPRE al usuario las fechas, por ticket. No asumir fechas.

```
¿Fechas para [TICKET-KEY] ([TIPO])?
  - Start date (customfield_10015):
  - Due date (duedate):
```

### Persona asignada (`assignee`)

Preguntar SIEMPRE al usuario. Primero buscar el perfil en Jira con `jira_get_user_profile` para obtener el display name, luego asignarlo como string (no como objeto):

```json
{ "assignee": "Julio Martinez" }
```

Si el proyecto es personal o el usuario no especifica, asignar al reporter del ticket.

### Team (`customfield_10001`)

Preguntar al usuario. Si no hay teams configurados en el proyecto (verificar con `jira_search` por `"Team[Team]" is not EMPTY`), omitir el campo sin preguntar — no llenar lo que no existe.

### Formato de actualización

Usar `jira_update_issue` con el `fields` JSON:

```json
{
  "customfield_10016": 3,
  "customfield_10015": "2026-06-15",
  "duedate": "2026-06-22",
  "assignee": "Julio Martinez"
}
```

**Regla:** si el usuario responde "vos definí" o no da una fecha concreta, re-preguntar. No inventar fechas. No asumir story points — usar la tabla de arriba como default pero confirmar.

---

## Paso 4 — Jerarquía y relaciones

```
Épica: [DAT] ETL: Migrar pipeline a arquitectura incremental
 ├── Spike: [DAT] SPIKE | ¿Particionamiento BigQuery vs Redshift?
 ├── Task:  [DAT] ETL | Implementar carga incremental desde PostgreSQL
 │    ├── Sub-task: [DAT] DAT-42 > Configurar conexión PostgreSQL con SSL
 │    ├── Sub-task: [DAT] DAT-42 > Diseñar esquema de tabla incremental
 │    └── Sub-task: [DAT] DAT-42 > Escribir pruebas de idempotencia
 ├── Task:  [DAT] ETL | Agregar transformaciones de normalización
 └── Bug:   [DAT] BUG | ETL: Registros duplicados en carga nocturna
```

**Reglas de relación:**
- Sub-task siempre tiene una Task como padre. Nunca va directo a una Épica.
- Bug puede ser hijo de una Épica o estar suelto (si es un bug de producción no relacionado a una épica activa).
- Spike puede ser hijo de una Épica o estar suelto (si es una investigación de arquitectura general).
- Una Task solo tiene una Épica como padre.

---

## Paso 5 — Casamiento con rama Git

Después de crear el ticket, preguntar:

> **"¿Este ticket necesita casarse con un branch de desarrollo?"**

| Tipo de ticket | Rama típica | Patrón |
|---|---|---|
| Épica | Siempre | `epic/{EPIC-KEY}-{slug}` |
| Task | Casi siempre | `feat/{TASK-KEY}-{slug}` |
| Spike | Opcional | `chore/{SPIKE-KEY}-{slug}` (si produce código de prueba) |
| Bug | Siempre que haya fix | `fix/{BUG-KEY}-{slug}` |
| Sub-task | Condicional (Subtask Gate) | `feat/{SUBTASK-KEY}-{slug}` |

Aplicar el skill `git-branch-strategy` para determinar si la Sub-task amerita rama propia.

---

## Paso 6 — Verificar nomenclatura antes de crear

Antes de confirmar la creación, hacer este checklist:

- [ ] ¿El tipo de ticket es correcto según el árbol de decisión?
- [ ] ¿El título sigue exactamente el patrón del tipo?
- [ ] ¿El `PROJECT_KEY` es correcto para este repositorio?
- [ ] ¿Los campos obligatorios están completos?
- [ ] ¿Las relaciones padre/hijo son correctas?
- [ ] ¿Se preguntó si necesita rama Git?
- [ ] ¿Se preguntaron fechas (start date, due date)?
- [ ] ¿Se preguntó el assignee?
- [ ] ¿Se asignaron story points según tipo de ticket?

Si algún campo falta, **detener y pedir el dato** — no crear el ticket incompleto.

---

## Paso 7 — Cierre y evidencia

Al mover un ticket a **Done**:

| Tipo | Evidencia requerida |
|---|---|
| Épica | Todas las Tasks hijas en Done; PR de epic→main mergeado |
| Task | `sdd-verify` ejecutado; PR mergeado a epic-branch; comentario en Jira con branch y PR |
| Spike | Documento de decisión adjunto (ADR o nota); timebox respetado |
| Bug | Pasos para reproducir ya no reproducen el problema; evidencia de fix (captura o test) |
| Sub-task | Squash merge a task-branch completado; rama borrada |

Usar el skill `jira-evidence-formatter` para formatear la evidencia en lenguaje no técnico antes de adjuntarla al ticket.

---

## Referencia rápida — Patrones de nomenclatura

| Tipo | Patrón | Ejemplo |
|---|---|---|
| Épica | `[{KEY}] {SISTEMA}: {OBJETIVO}` | `[DAT] ETL: Migrar pipeline a incremental` |
| Task | `[{KEY}] {SISTEMA} \| {ENTREGABLE}` | `[DAT] ETL \| Implementar carga incremental` |
| Spike | `[{KEY}] SPIKE \| {PREGUNTA}` | `[DAT] SPIKE \| ¿Particionamiento BigQuery?` |
| Bug | `[{KEY}] BUG \| {COMPONENTE}: {SÍNTOMA}` | `[DAT] BUG \| ETL: Registros duplicados` |
| Sub-task | `[{KEY}] {TASK_ID} > {ACCIÓN}` | `[DAT] DAT-42 > Configurar conexión SSL` |

---

---

## Paso 8 — Flujo de estados y transiciones (Jira Workflow)

### Mapa de estados — flujo activo (3 estados)

> **Nota:** el proyecto DAT no tiene acceso de Site Admin para editar workflows de Jira Cloud.
> Se usa el flujo simplificado con los 3 estados existentes. El PR es el objeto de revisión, no un estado Jira.

```
┌──────────┐   Iniciar   ┌──────────┐   PR mergeado   ┌───────┐
│ Por hacer│ ──────────► │ En curso │ ───────────────► │ Listo │
└──────────┘             └──────────┘                  └───────┘
                               ▲
                               │   Reabrir (bug post-merge)
                           ┌───────┐
                           │ Listo │
                           └───────┘
```

El ticket permanece en **En curso** durante todo el ciclo de PR: mientras está abierto, mientras está en revisión, y si es rechazado y corregido.

### Tabla de transiciones

| Transición | De → A | Quién la ejecuta | Requisito |
|---|---|---|---|
| Iniciar | Por hacer → En curso | Developer | Branch creado con naming correcto |
| Cerrar | En curso → Listo | Developer | PR aprobado y mergeado, CI verde |
| Reabrir | Listo → En curso | Cualquiera | Bug post-merge o corrección necesaria |

### Regla de reject-to-fix

El PR es el registro vivo del ciclo de revisión. El ticket en Jira no cambia de estado durante este proceso.

1. El reviewer rechaza el PR con comentarios concretos: qué falla, qué se espera.
2. El developer corrige y pushea al mismo branch. El PR se actualiza solo.
3. El reviewer re-revisa desde el mismo PR.
4. Cuando el PR se aprueba y mergea, el developer mueve el ticket a **Listo**.

No abrir un PR nuevo. No crear un ticket nuevo. El link al PR en el comentario del ticket es el rastro de auditoría.

### Propagación jerárquica — reglas de estado entre niveles

```
Sub-task "Listo"
  → Task se mueve a "In Review" cuando TODAS las Sub-tasks están en "In Review" o "Listo"
  → Task se mueve a "Listo" cuando TODAS las Sub-tasks están en "Listo"

Task "Listo"
  → Epic se mueve a "In Review" cuando TODAS las Tasks están en "In Review" o "Listo"
  → Epic se mueve a "Listo" cuando TODAS las Tasks están en "Listo"
```

Estas transiciones pueden ser **manuales** (equipo chico) o configurarse como **automatizaciones Jira** (ver abajo).

### Alineación con gates de git-branch-strategy

| Estado Jira | Gate activo | Qué valida |
|---|---|---|
| Sub-task **En curso** | — | Desarrollo en branch local |
| Sub-task **In Review** | DSG-01..07 (develop gate) | Lint, unit tests, 80% cobertura, 1 approval, semantic commits |
| Sub-task **Listo** | DSG pasado | Branch mergeado a `develop` |
| Task **In Review** | SMG-01..10 (staging gate) | Todo DSG + DQS 5 obligaciones + integración + smoke + regresión |
| Task **Listo** | SMG pasado | Mergeado a `main` |
| Epic **Listo** | — | Release taggeado, changelog actualizado |

Si la Task falla el staging gate (SMG): Task vuelve a "En curso", las Sub-tasks afectadas se reabren manualmente.

### Automatizaciones Jira recomendadas (configurar en Project Settings → Automation)

Estas tres reglas eliminan las transiciones manuales de nivel intermedio:

| Regla | Trigger | Condición | Acción |
|---|---|---|---|
| Sub-tasks done → Task In Review | Child issue transitioned to "Listo" | All siblings in "In Review" or "Listo" | Transition parent Task to "In Review" |
| All Sub-tasks Listo → Task Listo | Child issue transitioned to "Listo" | All siblings in "Listo" | Transition parent Task to "Listo" |
| All Tasks Listo → Epic Listo | Child issue transitioned to "Listo" | All siblings in "Listo" | Transition parent Epic to "Listo" |

**Ponytail check:** si el equipo es ≤2 personas y las transiciones manuales no generan fricción, omitir la automatización — no instalar lo que no duele.

---

## Label Helper — Asignación de etiquetas

### Paso L1 — Intentar leer labels existentes del proyecto (repo-agnóstico)

Si la API Jira está disponible (`JIRA_TOKEN` válido):

```python
# Consultar últimos 30 tickets para ver qué labels se usan
GET /rest/api/3/search/jql?jql=project={PROJECT_KEY} ORDER BY created DESC&maxResults=30&fields=labels
```

Extraer todos los labels únicos y usarlos como sugerencias al crear nuevos tickets.
Si la API devuelve 401 o 0 resultados, usar la taxonomía estándar de abajo.

---

### Paso L2 — Taxonomía estándar (fallback siempre disponible)

#### Grupo 1 — Dominio (1 requerido)

| Label | Cuándo |
|---|---|
| `etl` | Pipeline, ingestión, transformaciones, carga |
| `api` | REST API, endpoints, autenticación de servicios |
| `analytics` | Reportes, exports, dashboards, agregados |
| `db` | Esquema, migraciones, queries SQL |
| `auth` | Autenticación, permisos, IAM, RLS |
| `frontend` | UI, Angular, componentes |
| `infra` | CI/CD, Docker, deployment, configuración |
| `docs` | Documentación pura, ADRs, README |
| `audit` | Auditoría, Data Quality Shield (DQS), process-integrity |

#### Grupo 2 — Tipo de trabajo (1 requerido)

| Label | Cuándo |
|---|---|
| `feature` | Nueva funcionalidad |
| `bugfix` | Corrección de defecto |
| `refactor` | Mejora estructural sin cambio de comportamiento |
| `spike` | Investigación o exploración técnica |
| `perf` | Mejora de rendimiento |
| `security` | Hardening, auditoría, vulnerabilidades |
| `test` | Cobertura de tests, corrección de suite |

#### Grupo 3 — Calidad y proceso (opcionales)

| Label | Cuándo |
|---|---|
| `shield-validated` | Data Quality Shield en verde |
| `shield-pending` | Shield no ejecutado aún |
| `tech-debt` | Deuda técnica |
| `quick-win` | Completable en <1 día |
| `blocker` | Bloquea a otro ticket o equipo |

**Regla mínima:** todo ticket necesita al menos 1 label de dominio + 1 de tipo.

---

### Paso L3 — Sugerir labels según contexto del ticket

Al asignar labels, hacer estas preguntas:

1. **¿Qué capa del sistema toca este ticket?** → label de Dominio
2. **¿Qué tipo de trabajo describe mejor esto?** → label de Tipo
3. **¿El Shield se ejecutó ya?** → `shield-validated` o `shield-pending`
4. **¿Bloquea algo?** → `blocker`
5. **¿Es urgente pero pequeño?** → `quick-win`

Presentar al usuario los labels sugeridos antes de crear el ticket:

```
Labels sugeridos para "[DAT] ETL | Implementar carga incremental":
  ✓ etl          (dominio: pipeline de datos)
  ✓ feature      (tipo: nueva funcionalidad)
  ✓ shield-pending (el Shield no se ha ejecutado aún)
¿Confirmas estos labels o quieres agregar/cambiar alguno?
```

---

### Paso L4 — Formato en jira_epic_tree.json (BUNKER_TOOLS)

Si el proyecto usa BUNKER_TOOLS (`~/Developer/BUNKER_TOOLS/jira_orchestrator.py`), generar el nodo con los labels incluidos:

```json
{
  "type": "task",
  "summary": "[DAT] ETL | Implementar carga incremental desde PostgreSQL",
  "labels": ["etl", "feature", "shield-pending"],
  "customfield_10016": 5,
  "description": "...",
  "children": []
}
```

Si no hay BUNKER_TOOLS, entregar los labels como lista para copiar en el campo `Labels` de la UI de Jira.

---

## Jerarquía visual de creación (orden obligatorio)

```
PASO 1 — ÉPICA (siempre primero)
    ↓
PASO 2 — TASK / SPIKE / BUG (hijos de la épica)
    ↓
PASO 3 — SUB-TASK (hijos de Task o Bug, solo si Subtask Gate)
```

**Nunca crear un hijo sin que su padre exista en Jira.**

---

## Anti-patterns

- Crear una Sub-task sin Task padre.
- Crear una Sub-task directamente bajo una Épica.
- Usar el nombre de una función, clase o variable como título de ticket.
- Crear un Bug con la causa técnica en el título (el título describe el síntoma).
- Crear una Task sin criterios de aceptación.
- Crear Sub-tasks para tareas triviales (<1 día) que caben en la Task.
- Tener un Spike sin timebox definido — se convierte en investigación infinita.
- Cerrar un ticket sin evidencia adjunta.
- Usar labels demasiado vagos como `importante` o `urgente` sin el par dominio+tipo.
- Crear tickets con 0 labels.
- Llenar un campo opcional con relleno genérico en vez de marcarlo `Ninguno` o `Ninguna` (gate Ponytail, Paso 3.5).
- Crear un ticket sin preguntar fechas (start date, due date) — no asumir, siempre preguntar.
- Crear un ticket sin preguntar assignee — aunque el proyecto sea personal.
- Asignar story points sin seguir la convención del proyecto (subtask=3, task=1 por defecto).
