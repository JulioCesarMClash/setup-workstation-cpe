---
name: api-doc-gen
description: >
  Generate a concise API documentation report: usage mode, location, parameters, response schema, env vars, DB tables, and database.
  Saves result as an Obsidian note under 50-Projects/<project>/APIs/.
  Trigger: When user asks to document an API, generate API report, "documenta esta API", "genera reporte de API", "api-doc", or "documenta el módulo X".
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.1"
allowed-tools: Read, Edit, Write, Bash, mcp__obsidian-semantic__vault, mcp__obsidian-semantic__view, mcp__obsidian-semantic__edit, mcp__obsidian__write_file, mcp__obsidian__read_file, mcp__obsidian__list_directory, mcp__plugin_engram_engram__mem_save
---

## What This Skill Does

Reads source code files and produces a structured documentation note for each API endpoint. The note answers: _what does this endpoint do, how do you call it, what does it return, what data does it touch, and what does it need from the environment._

The note is saved in Obsidian so the whole team (devs, QA, product) can find it without opening the code.

---

## When to Use

**Technical users:**
- You point to a file or function: "documenta `src/routes/analytics.py`"
- You want a quick map of all routes in a router file
- Before opening a PR for a new endpoint

**Non-technical users (product, QA, stakeholders):**
- "Quiero saber qué hace el endpoint de exportación"
- "¿Qué datos toca el módulo de usuarios?"
- "Genera la documentación del módulo de analytics"

---

## Input Required

Ask the user for these if not provided:

| Input | What to ask | Required |
|-------|-------------|----------|
| `target` | "¿Qué archivo o endpoint quieres documentar?" (e.g. `src/routes/users.py` or `/api/export`) | Yes |
| `project` | "¿Cómo se llama el proyecto?" (e.g. `apn-pti26-data-core`) | Yes |
| `mode` | Single endpoint or full file/module? Default: single | No |
| `db_env_var` | Name of DB connection env var — auto-detect if missing | No |

---

## Quick Start — Example Invocation

**User says:** "documenta la API de analytics_exports en P01"

**You do:**
1. Ask: "¿Cuál es el archivo o ruta exacta?"
2. Read the file with the Read tool
3. Run local-router reasoning (Step 2 below)
4. Write the note to `50-Projects/apn-pti26-data-core/APIs/GET-analytics-export.md`
5. Confirm to user with the Obsidian path

---

## Execution Flow — Triple Hélice

### Step 1 — Scan (Claude tools)

Read the target file. If it imports services or repositories, read those too (one level deep).

Extract raw text for:
- Route decorators / method registrations
- Function signatures and return type hints
- `os.getenv`, `os.environ`, `process.env`, `config.*` calls
- SQL strings, ORM calls, table names
- Auth decorators / middleware references
- Response models, status codes, error raises

### Step 2 — Reason (Ollama / gemma4:31b)

```bash
~/local-router reason "Actúa como Arquitecto Senior. Analiza este código y extrae en JSON:
{
  endpoint: 'HTTP_METHOD /path',
  handler: 'function_name',
  location: 'file:line',
  description: 'qué hace este endpoint en una oración',
  auth: 'none|bearer|api_key|session|oauth2',
  params: {
    path: [{ name, type, description }],
    query: [{ name, type, required, default, description }],
    body: { schema_summary, required_fields: [] }
  },
  response: {
    success: { status_code, body_summary },
    errors: [{ status_code, condition }]
  },
  env_vars: [{ name, purpose }],
  database: { name, connection_var, tables: [{ name, operation }] },
  external_deps: [{ type: 'http|redis|s3|queue', target }],
  notes: 'edge cases o comportamiento no obvio — omit if none'
}
Código: [paste raw extract from Step 1]" --agent claude
```

### Step 3 — Write (Claude tools + Obsidian MCP)

> **MCP tool preference:** use `mcp__obsidian-semantic__*` (edit/view/vault) by default; fall back to `mcp__obsidian__*` (filesystem) only if obsidian-semantic is unavailable. See `core/obsidian-vault.md`.

1. Fill `assets/api-report-template.md` with the JSON output
2. Write to Obsidian: `50-Projects/<project>/APIs/<METHOD>-<path-slug>.md`
3. If `APIs/` folder does not exist, create it first (semantic `edit` creates parent folders; filesystem `create_directory` is deny-listed — use Bash `mkdir -p` in the vault as last resort)
4. Call `mem_save` with `type: architecture`, `project: <project>`
5. Report the Obsidian path back to the user

---

## Batch Mode

When user asks to document a full file, module, or router (not a single endpoint):

1. Read the target file
2. Identify ALL route registrations in the file (use Framework Detection Rules below)
3. Run Step 2 once per endpoint (or pass all routes together if the file is short)
4. Write one Obsidian note per endpoint
5. After all notes are written, create an index file: `50-Projects/<project>/APIs/INDEX.md`

**Index format:**
```markdown
# API Index — <project>
Generated: YYYY-MM-DD

| Method | Path | Handler | Auth | DB Tables |
|--------|------|---------|------|-----------|
| GET | /analytics/export | export_analytics | bearer | analytics_raw |
```

---

## Framework Detection Rules

| Framework | Route Patterns to Search |
|-----------|--------------------------|
| FastAPI | `@router.get(`, `@router.post(`, `@app.get(`, `@router.{method}(` |
| Flask | `@app.route(`, `@bp.route(`, `methods=[` |
| Express / Node | `router.get(`, `router.post(`, `app.get(`, `app.use(` |
| Django | `path(`, `re_path(`, `urlpatterns =` in `urls.py` |
| Gin (Go) | `r.GET(`, `r.POST(`, `group.GET(`, `v1.GET(` |
| NestJS | `@Get(`, `@Post(`, `@Controller(`, `@Patch(`, `@Delete(` |
| Spring Boot | `@GetMapping`, `@PostMapping`, `@RequestMapping` |

---

## DB / ORM Detection Rules

| Pattern | Indicates |
|---------|-----------|
| `session.query(Model)` / `db.query(` | SQLAlchemy ORM |
| `SELECT ... FROM table_name` | Raw SQL |
| `Model.objects.filter(` / `.get(` | Django ORM |
| `repository.find(` / `repo.fetch_` / `repo.get_` | Repository pattern |
| `db.collection(` / `.find({` / `.aggregate(` | MongoDB |
| `prisma.model.findMany` / `prisma.model.create` | Prisma (Node) |
| `db.Exec(` / `db.Query(` / `db.QueryRow(` | Go database/sql |
| `knex(` / `.select(` / `.where(` | Knex.js (Node) |

---

## Env Var Detection Rules

| Language | Patterns |
|----------|----------|
| Python | `os.getenv("VAR")`, `os.environ["VAR"]`, `settings.VAR`, `config.VAR` |
| Node / JS | `process.env.VAR`, `config.get("VAR")`, `env.VAR` |
| Go | `os.Getenv("VAR")`, `viper.GetString("VAR")` |
| Java | `System.getenv("VAR")`, `@Value("${VAR}")` |

---

## Response Schema Detection Rules

| Language / Framework | Patterns |
|---------------------|----------|
| FastAPI | Return type hint, `response_model=`, `JSONResponse(`, `raise HTTPException(` |
| Flask | `return jsonify(`, `return Response(`, `abort(` |
| Express | `res.json(`, `res.status(`, `res.send(` |
| Go Gin | `c.JSON(`, `c.AbortWithStatus(` |
| Django | `Response(`, `HttpResponse(`, `JsonResponse(` |

Extract: success status code + body shape, error status codes + conditions.

---

## Report Sections (all mandatory — mark `_none_` if empty)

1. **Header** — method + path + one-line description
2. **Location** — file, function name, line number, framework
3. **Usage** — full URL pattern, auth type, content-type
4. **Parameters** — path / query / request body (with types and required/optional)
5. **Response** — success status + body summary, error codes + conditions ← _new_
6. **Environment Variables** — name + inferred purpose
7. **Database** — DB name, connection var, tables + operation (SELECT/INSERT/UPDATE/DELETE)
8. **External Dependencies** — HTTP calls, Redis, S3, queues (mark _none_ if clean) ← _new_
9. **Notes** — edge cases or non-obvious behavior (omit section only if truly empty)

---

## Obsidian Output Rules

- Path: `50-Projects/<project>/APIs/<METHOD>-<path-slug>.md`
- Filename: kebab-case, uppercase method (e.g. `GET-users-id.md`, `POST-analytics-export.md`)
- Frontmatter fields: `type`, `project`, `method`, `path`, `handler`, `generated`
- Create `APIs/` folder if it doesn't exist
- After every write, save to Engram: `type: architecture`, project = project name
- Batch mode also writes `APIs/INDEX.md`

---

## Fallback Rules

| Situation | Action |
|-----------|--------|
| Can't find route decorator | Ask: "¿Cuál es el nombre de la función del endpoint?" |
| Can't detect DB tables | Write `tables: undetected — revisión manual requerida` |
| Can't detect env vars | Search `.env`, `config.py`, `settings.py`, `app.config` in project root |
| Framework not in table | Extract all function definitions + HTTP-related imports manually |
| Can't detect response schema | Write `response: undetected — revisar tipo de retorno manualmente` |
| obsidian-semantic unavailable | Fall back to `mcp__obsidian__*` (filesystem MCP) and say so explicitly |
| Both Obsidian MCPs unavailable | Write Markdown report to current working directory as `<slug>-api-doc.md` |

---

## Resources

- **Report template**: [`assets/api-report-template.md`](assets/api-report-template.md)
- **Obsidian vault path**: `BOVEDA MCP CLAUDE-OBSIDIAN/50-Projects/<project>/APIs/`
- **Governance note**: `000_SISTEMA_OPERATIVO/040_Estandar_API_Doc_Gen.md`
