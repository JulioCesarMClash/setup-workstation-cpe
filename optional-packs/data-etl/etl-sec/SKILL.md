---
name: etl-sec
description: >
  Auditor de seguridad OWASP-aligned para proyectos ETL Python hexagonales.
  Detecta SQLi, SSRF, command injection, secrets expuestos, path traversal y patrones inseguros.
  Trigger: cuando el usuario pide "busca vulnerabilidades", "security audit", "revisa seguridad", "OWASP", antes de un release, o al tocar código de red/DB/subprocess.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
allowed-tools: Read, Bash, Grep, Glob
---

## When to Use

- Antes de un release o merge a main
- Al agregar código que toca DB, HTTP, subprocess, filesystem, o env vars
- Al revisar PRs que incluyen SQL dinámico o llamadas externas
- Al incorporar dependencias nuevas

## Severity Levels

| Level    | Criterio |
|----------|----------|
| CRITICAL | RCE, SQLi explotable con input externo real, secrets en código |
| HIGH     | SQLi por fallback inseguro, SSRF con input semi-controlado, deserialization |
| MEDIUM   | Patrones inseguros que podrían escalar, SSRF por env var, SQL sin sanitizar |
| LOW      | Validación débil, fallback sin escape, subprocess sin validar input |
| INFO     | Patrones seguros observados, no requieren acción |

---

## Analysis Categories

### CAT-1 — SQL Injection
- [ ] f-strings en SQL con input derivado de usuario o env var
- [ ] `where=` params que aceptan raw SQL strings sin sanitizar
- [ ] Fallback paths que usan concatenación en lugar de parameterización
- [ ] Identifiers (tabla/columna) interpolados sin `quote_identifier()`
- [ ] **Seguro**: `%s` parameterizado + `quote_identifier()` para names

```bash
rg -n 'f".*SELECT|f".*INSERT|f".*UPDATE|f".*WHERE' etl/ --type py | grep -v test_
rg -n "where\s*=" etl/pipelines/ --type py
```

### CAT-2 — Command Injection / subprocess
- [ ] `shell=True` en cualquier subprocess call
- [ ] Comandos construidos con concatenación de strings (no lista)
- [ ] Input de usuario pasado a subprocess sin validación
- [ ] **Seguro**: list form + sin `shell=True`

```bash
rg -n "shell=True|os\.system|os\.popen" etl/ --type py
rg -n "subprocess\." etl/ --type py | grep -v test_
```

### CAT-3 — SSRF / URL Validation
- [ ] URLs tomadas de env vars sin validar scheme/host
- [ ] `http://` aceptado donde solo debería aceptarse `https://`
- [ ] Webhook URLs sin whitelist de dominio permitido
- [ ] `urllib.request.urlopen` / `requests.get` sin validación previa

```bash
rg -n "urlopen|requests\.(get|post)|webhook_url" etl/ --type py | grep -v test_
rg -n "os\.getenv.*URL\|os\.getenv.*WEBHOOK" etl/ --type py
```

### CAT-4 — Secrets / Credenciales
- [ ] `password=`, `token=`, `api_key=`, `secret=` con valor hardcodeado
- [ ] Credenciales en logs (print con password/token)
- [ ] `.env` files commiteados al repo
- [ ] Secrets en variables de entorno logueadas con `print(os.environ)`

```bash
rg -in "password\s*=\s*['\"][^'\"]{3,}" etl/ --type py | grep -v test_
rg -n "print.*os\.environ|log.*os\.environ" etl/ --type py
```

### CAT-5 — Path Traversal
- [ ] `Path(user_input)` o `open(user_input)` sin sanitizar
- [ ] `args.*` usado directamente en operaciones de filesystem
- [ ] `../` no bloqueado en paths derivados de input externo

```bash
rg -n "Path\(.*args\.|open\(.*args\." etl/ --type py | grep -v test_
```

### CAT-6 — Deserialization / Parsing
- [ ] `pickle.loads` / `pickle.load`
- [ ] `yaml.load()` sin `Loader=yaml.SafeLoader`
- [ ] `json.loads` con input de red sin try/except

```bash
rg -n "pickle\.|yaml\.load[^_]" etl/ --type py
```

### CAT-7 — Dependencias y Configuración
- [ ] TLS bypass (`verify=False`, `ssl=False`, `CERT_NONE`)
- [ ] Timeouts ausentes en llamadas HTTP
- [ ] `override=True` en `load_dotenv` sin control de origen

```bash
rg -n "verify=False|ssl=False|CERT_NONE" etl/ --type py
```

---

## Rules Catalog

| ID | Category | Severity | Rule | Fix |
|----|----------|----------|------|-----|
| SEC-01 | SQL | CRITICAL | f-string SQL con input externo real | Parametrizar con `%s` o usar ORM |
| SEC-02 | SQL | HIGH | Fallback SQL con string concat sin escape | `cursor.mogrify()` o re-raise el TypeError |
| SEC-03 | SQL | MEDIUM | `where=` param acepta raw SQL string | Documentar restricción; validar en caller |
| SEC-04 | Network | MEDIUM | Webhook URL sin validación de scheme/host | `assert url.startswith("https://chat.googleapis.com/")` |
| SEC-05 | subprocess | HIGH | `shell=True` con input dinámico | Cambiar a list form |
| SEC-06 | subprocess | LOW | Args CLI no validados antes de subprocess | Validar formato (regex/datetime.fromisoformat) |
| SEC-07 | Secrets | CRITICAL | Credencial hardcodeada en código | Mover a env var + `.gitignore` |
| SEC-08 | Deserialization | HIGH | `pickle.loads` con datos externos | Eliminar; usar JSON |
| SEC-09 | TLS | HIGH | `verify=False` en requests | Nunca deshabilitar TLS en prod |

---

## Output Format

```
## ETL-SEC REPORT — <fecha>

### CRITICAL (N)
- [SEC-01] archivo.py:L — descripción
  Exploitable: <cómo se explotaría>
  Fix: <cambio mínimo>

### HIGH / MEDIUM / LOW / INFO ...

---
Total: N | CRITICAL: N | HIGH: N | MEDIUM: N | LOW: N | INFO: N
Subprocess shell=True: NO ✅ | Hardcoded secrets: NO ✅ | TLS bypass: NO ✅
```

## Execution Protocol

1. Correr los comandos de cada categoría (CAT-1 a CAT-7)
2. Verificar callers de cada hallazgo — ¿el input es interno o externo?
3. Clasificar por severity según si el input es controlable por un atacante
4. Proponer fix mínimo sin romper la suite
5. Preguntar al usuario qué hallazgos implementar

## Stack Específico (ELT_analisis_Script)
Python 3.12 · PostgreSQL/MariaDB (dbutils PooledDB) · urllib.request · python-dotenv · argparse · subprocess list-form · pandas CSV staging
