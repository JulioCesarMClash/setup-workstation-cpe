---
name: gh-repo-bootstrap
description: >
  Bootstrap automático de un repositorio GitHub nuevo con estructura hexagonal Python,
  3 ramas permanentes (main/staging/develop), workflow quality-shield.yml y registro en Obsidian.
  Trigger: cuando el usuario pide crear un nuevo repo, inicializar un proyecto, o "bootstrap".
license: Apache-2.0
metadata:
  author: julio-martinez
  version: "1.1"
  tier: MID-HIGH
  model: claude-sonnet-4-6
  governance: 000_SISTEMA_OPERATIVO/060_Protocolo_Bootstrap_Repositorio.md
  changelog: >
    v1.1 (2026-07-03): Paso 3 apunta a quality-shield.standard.yml en AI-OS
    (fuente única) en vez del asset local desactualizado. Paso 6 reescrito con
    los 3 comandos completos de ruleset (antes solo develop, staging/main eran
    comentarios). Corregido tras auditoría de branch protection que encontró
    P01/P02/P03 sin merge gating real pese a tener quality-shield.yml.
---

# gh-repo-bootstrap — Bootstrap de Repositorio GitHub

> Gobernanza completa: `000_SISTEMA_OPERATIVO/060_Protocolo_Bootstrap_Repositorio.md`
> Estándar de ramas: `~/.skills/git-branch-strategy/SKILL.md`
> Plataforma deploy/CI: `000_SISTEMA_OPERATIVO/052_Estandar_Plataforma_Deploy_Jenkins_GitHub_Actions.md`

---

## When to Use

Activar **automáticamente** cuando el usuario diga cualquiera de:
- "crear un nuevo repo", "nuevo repositorio", "inicializar proyecto"
- "bootstrap", "scaffold repo", "setup del proyecto"
- "crea el repo en GitHub", "inicializa el git"

**No usar** si el repo ya existe y solo se quiere añadir un archivo o rama.

---

## Inputs requeridos

Preguntar al usuario antes de ejecutar si no están en el contexto:

| Input | Descripción | Ejemplo |
|-------|-------------|---------|
| `repo_name` | Nombre del repositorio | `apn-pti26-new-service` |
| `org` | Organización o usuario GitHub | `AprendeFCS` |
| `visibility` | `public` o `private` | `private` |
| `description` | Descripción corta del repo | `"Pipeline de ingestión X"` |
| `jira_key` | Key del proyecto Jira (opcional) | `DAT` |

---

## Pasos de ejecución (orden estricto)

### Paso 1 — Crear repositorio en GitHub
```bash
gh repo create {org}/{repo_name} \
  --{visibility} \
  --description "{description}" \
  --clone
cd {repo_name}
```

### Paso 2 — Bootstrap estructura mínima
```bash
mkdir -p src tests .github/workflows
touch src/.gitkeep tests/__init__.py
```

Crear los siguientes archivos:
- `.gitignore` → copiar desde `~/.skills/git-branch-strategy/assets/gitignore-python-hexagonal.txt`
- `.env.example` → plantilla mínima con variables del proyecto
- `requirements.txt` → mínimo: `pytest ruff pytest-cov`
- `README.md` → título + descripción + sección de ramas

### Paso 3 — Añadir quality-shield.yml
Fuente única canónica — nunca copiar de otro lado (ver `paths.yaml:github_quality_shield_template`):
```bash
cp ~/Developer/AI-OS/github/templates/quality-shield.standard.yml .github/workflows/quality-shield.yml
```

Este paso instala el estándar de **CI**. No asumir ni crear deploy en GitHub Actions como default si el repo será `deployable`.

### Paso 4 — Commit inicial en main
```bash
git add .
git commit -m "feat(init): bootstrap {repo_name} — estructura hexagonal + quality-shield"
git push -u origin main
```

### Paso 5 — Crear y pushear staging y develop
```bash
git checkout -b staging && git push -u origin staging
git checkout -b develop && git push -u origin develop
git checkout main
```

### Paso 6 — Configurar branch protection (requiere admin)

Mecanismo: **rulesets** (`gh api repos/{org}/{repo}/rulesets`), NO la API clásica de
`branches/{branch}/protection` — la clásica no soporta la política real que usamos
(3 rulesets independientes por rama, cada uno exigiendo su propio check). Ejecutar
solo si el token tiene permisos de admin. Los 3 checks exigidos deben coincidir
EXACTO con los `name:` de los jobs `develop-required` / `staging-required` /
`main-required` en `quality-shield.standard.yml` — ver `github/branch-gates-policy.md`.

`required_approving_review_count: 0` es el default real usado hoy en los 3 repos
activos (proyecto solo-dev — nadie puede aprobar su propio PR igual). Subir a 1+
si el equipo crece.

Reemplazar `{org}`/`{repo_name}` y correr los 3 bloques (uno por rama — el `name`
del ruleset y el `context` del check cambian, todo lo demás es idéntico):

```bash
# develop
gh api repos/{org}/{repo_name}/rulesets --method POST --input - <<'EOF'
{
  "name": "Develop branch gate",
  "target": "branch",
  "enforcement": "active",
  "conditions": {"ref_name": {"include": ["refs/heads/develop"], "exclude": []}},
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "pull_request", "parameters": {
      "required_approving_review_count": 0, "dismiss_stale_reviews_on_push": false,
      "required_reviewers": [], "require_code_owner_review": false,
      "require_last_push_approval": false, "required_review_thread_resolution": false,
      "allowed_merge_methods": ["merge", "squash", "rebase"]
    }},
    {"type": "required_status_checks", "parameters": {
      "strict_required_status_checks_policy": true, "do_not_enforce_on_create": false,
      "required_status_checks": [{"context": "Develop gate — required"}]
    }}
  ]
}
EOF

# staging
gh api repos/{org}/{repo_name}/rulesets --method POST --input - <<'EOF'
{
  "name": "Staging branch gate",
  "target": "branch",
  "enforcement": "active",
  "conditions": {"ref_name": {"include": ["refs/heads/staging"], "exclude": []}},
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "pull_request", "parameters": {
      "required_approving_review_count": 0, "dismiss_stale_reviews_on_push": false,
      "required_reviewers": [], "require_code_owner_review": false,
      "require_last_push_approval": false, "required_review_thread_resolution": false,
      "allowed_merge_methods": ["merge", "squash", "rebase"]
    }},
    {"type": "required_status_checks", "parameters": {
      "strict_required_status_checks_policy": true, "do_not_enforce_on_create": false,
      "required_status_checks": [{"context": "Staging gate — required"}]
    }}
  ]
}
EOF

# main
gh api repos/{org}/{repo_name}/rulesets --method POST --input - <<'EOF'
{
  "name": "Main branch gate",
  "target": "branch",
  "enforcement": "active",
  "conditions": {"ref_name": {"include": ["refs/heads/main"], "exclude": []}},
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "pull_request", "parameters": {
      "required_approving_review_count": 0, "dismiss_stale_reviews_on_push": false,
      "required_reviewers": [], "require_code_owner_review": false,
      "require_last_push_approval": false, "required_review_thread_resolution": false,
      "allowed_merge_methods": ["merge", "squash", "rebase"]
    }},
    {"type": "required_status_checks", "parameters": {
      "strict_required_status_checks_policy": true, "do_not_enforce_on_create": false,
      "required_status_checks": [{"context": "Main gate — required"}]
    }}
  ]
}
EOF
```

**Antes de correr esto en un repo real**: abrir un PR de prueba primero y confirmar
con `gh pr checks` que el check aparece con el nombre EXACTO esperado. Un nombre
mal alineado deja el PR bloqueado para siempre en "expected — waiting for status"
(pasó en la auditoría del 2026-07-03 — ver `060_Protocolo_Bootstrap_Repositorio.md`).

Si falla por permisos → registrar como pendiente en la nota Obsidian del repo.

### Paso 7 — Registrar en Obsidian
Crear nota en: `50-Projects/{repo_name}/Index.md` con:
- Nombre del repo, URL GitHub, organización
- Ramas creadas, fecha de bootstrap
- Jira key asociado (si aplica)
- Estado de branch protection

---

## Output esperado

Al terminar reportar:

```
✅ Repo creado: https://github.com/{org}/{repo_name}
✅ Ramas: main, staging, develop pusheadas
✅ quality-shield.yml instalado
✅/⚠️  Branch protection: configurada / pendiente (sin permisos admin)
✅ Nota Obsidian creada: 50-Projects/{repo_name}/Index.md
```

---

## Constraints

- **Nunca** hacer push directo a `main` después del bootstrap — solo PRs.
- **Nunca** commitear `.env` con valores reales — solo `.env.example`.
- Si el repo ya existe en GitHub, **no** ejecutar `gh repo create`; ir directo al Paso 3.
- Si el usuario no provee `jira_key`, omitir referencias Jira en el README.
- Branch protection requiere token con scope `admin:repo` — advertir si falta.
- Si el repo será `deployable`, registrar que el deploy debe centralizarse en Jenkins; no instalar GitHub Actions deploy como default sin excepción documentada.

---

## Checklist de verificación final

- [ ] `gh repo view {org}/{repo_name}` responde sin error
- [ ] `git branch -a` muestra `main`, `staging`, `develop` en remotes
- [ ] `.github/workflows/quality-shield.yml` existe y coincide con `quality-shield.standard.yml` (9 jobs, triggers en develop+staging+main)
- [ ] Nota Obsidian creada en `50-Projects/{repo_name}/`
- [ ] Branch protection activa (o pendiente documentada)
