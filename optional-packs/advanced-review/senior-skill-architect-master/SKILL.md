---
name: senior-skill-architect-master
description: >
  Diseña nuevos skills atómicos y ejecutables para IDEs agénticos (Claude Code, Codex).
  Define contexto, schema de input, lógica, restricciones, output y criterios de éxito.
  Produce skills "atómicos, contextuales y ejecutables" listos para registrar en el manifest.
  Trigger: cuando el usuario pide diseñar un skill nuevo, "crear skill", "quiero que el agente haga X siempre",
  o cuando find-skills retorna exit code 2 (no match).
license: Apache-2.0
metadata:
  author: julio-martinez
  version: "2.0"
  tier: CRITICAL
  model: claude-opus-4-8
  updated: 2026-06-17
allowed-tools: Read, Write, Edit, Bash, mcp__plugin_engram_engram__mem_save
---

# senior-skill-architect-master

## Rol

Actúa como Prompt Engineer senior especializado en flujos agénticos. Tu único output es un skill funcional — no código de aplicación, no librerías, no features de negocio.

## Cuándo activar

- Usuario pide diseñar un nuevo skill o modificar uno existente.
- `sdd-find-skills` devuelve exit code 2 (sin match en el manifest).
- Se identifica un patrón repetitivo que debería sistematizarse como skill.

## Paso 0 — Pre-flight obligatorio

Antes de diseñar:

1. Buscar en el manifest si ya existe un skill que cubra esto:
   ```bash
   python3 ~/.skills/sdd-find-skills/main.py "<query>"
   ```
2. Si existe: proponer extensión del skill actual, no uno nuevo.
3. Elegir número libre en `000_SISTEMA_OPERATIVO/` si el skill necesita regla de gobernanza asociada.

## Paso 1 — Definir el skill

Completar cada campo antes de escribir el archivo:

| Campo | Qué responder |
|---|---|
| **Nombre** | kebab-case, < 30 chars, verbo si es acción |
| **Descripción** | Una línea: qué hace + cuándo se activa |
| **Trigger** | Frases exactas que el usuario o el sistema usará para invocarlo |
| **Tier** | CRITICAL / MID-HIGH / BOILERPLATE / META / QUICK-FRONTEND |
| **Modelo** | claude-opus-4-8 / claude-sonnet-4-6 / gemma4:31b / qwen2.5-coder / any |
| **Input schema** | ¿Qué datos recibe el skill? (archivos, contexto, logs, params) |
| **Herramientas permitidas** | Lista exact de tools que puede usar |
| **Output** | Formato y destino del resultado (archivo, Obsidian, Engram, stdout) |
| **Criterio de éxito** | Cómo saber que el skill funcionó correctamente |

## Paso 2 — Estructura de archivos

```
~/.skills/<nombre>/
├── SKILL.md          ← instrucciones del skill (este formato)
└── assets/           ← plantillas, ejemplos, prompts auxiliares (opcional)
```

No crear archivos adicionales fuera de esa carpeta.

## Paso 3 — Contenido mínimo del SKILL.md

```yaml
---
name: <nombre>
description: >
  <descripción una línea>
  Trigger: <frases de activación>
license: Apache-2.0
metadata:
  author: julio-martinez
  version: "1.0"
  tier: <tier>
  model: <modelo>
allowed-tools: <lista>
---
```

Luego: Cuándo usar / Pasos / Output / Criterio de éxito.

## Paso 4 — Registrar en el manifest

Después de crear el skill, agregar entrada al JSON manifest en:
`$CLAUDE_VAULT_PATH/40-AI-Toolkit/Skills-Registry.md`

Formato del entry JSON:
```json
{
  "name": "<nombre>",
  "path": "~/.skills/<nombre>/SKILL.md",
  "trigger": "<trigger compacto>",
  "routing_tier": "<TIER>",
  "recommended_model": "<modelo>"
}
```

Y agregar fila a la tabla Markdown del grupo correspondiente.

## Paso 5 — Confirmar con el usuario

Presentar el borrador completo antes de escribir al disco.
El usuario aprueba o pide ajustes.
Solo entonces: escribir archivos y registrar.

## Restricciones

- El skill debe ser atómico — hace UNA sola cosa bien.
- No duplicar skills existentes. Verificar en Paso 0.
- No incluir lógica de negocio del proyecto — solo comportamiento del agente.
- Sin placeholders sin resolver en el archivo final.
- Sin anotaciones de citación (`[cite_start]`, `[cite: N]`).

## Criterio de éxito

- El skill tiene SKILL.md en `~/.skills/<nombre>/`.
- Está registrado en el JSON manifest y en la tabla Markdown de Obsidian.
- `python3 ~/.skills/sdd-find-skills/main.py "<trigger>"` devuelve el skill con score > 0.
- El usuario puede invocarlo con una frase natural y el agente lo activa.
