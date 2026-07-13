---
type: api-doc
project: {{PROJECT}}
method: {{METHOD}}
path: {{PATH}}
handler: {{HANDLER}}
generated: {{DATE}}
tags: [api, {{PROJECT}}]
---

# `{{METHOD}} {{PATH}}`

> {{ONE_LINE_DESCRIPTION}}

---

## Location

| Field | Value |
|-------|-------|
| File | `{{FILE_PATH}}` |
| Function | `{{HANDLER}}` |
| Line | `{{LINE_NUMBER}}` |
| Framework | {{FRAMEWORK}} |

---

## Usage

```
{{METHOD}} {{FULL_PATH_PATTERN}}
Content-Type: {{CONTENT_TYPE}}
Auth: {{AUTH_TYPE}}
```

---

## Parameters

### Path Params
{{#if PATH_PARAMS}}
| Name | Type | Description |
|------|------|-------------|
{{EACH PATH_PARAM}}| `{{name}}` | `{{type}}` | {{description}} |
{{/EACH}}
{{else}}
_none_
{{/if}}

### Query Params
{{#if QUERY_PARAMS}}
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
{{EACH QUERY_PARAM}}| `{{name}}` | `{{type}}` | {{required}} | `{{default}}` | {{description}} |
{{/EACH}}
{{else}}
_none_
{{/if}}

### Request Body
{{#if BODY_SCHEMA}}
```json
{{BODY_SCHEMA_JSON}}
```
{{else}}
_none_
{{/if}}

---

## Response

### Success
| Status | Body |
|--------|------|
| `{{SUCCESS_STATUS}}` | {{SUCCESS_BODY_SUMMARY}} |

### Errors
{{#if ERROR_CODES}}
| Status | Condition |
|--------|-----------|
{{EACH ERROR}}| `{{code}}` | {{condition}} |
{{/EACH}}
{{else}}
_none documented_
{{/if}}

---

## Environment Variables

{{#if ENV_VARS}}
| Variable | Inferred Purpose |
|----------|-----------------|
{{EACH ENV_VAR}}| `{{name}}` | {{purpose}} |
{{/EACH}}
{{else}}
_none_
{{/if}}

---

## Database

| Field | Value |
|-------|-------|
| Database | `{{DB_NAME}}` |
| Connection var | `{{DB_CONNECTION_VAR}}` |

### Tables Accessed

{{#if TABLES}}
| Table | Operation | Notes |
|-------|-----------|-------|
{{EACH TABLE}}| `{{name}}` | `{{operation}}` | {{notes}} |
{{/EACH}}
{{else}}
_none detected_
{{/if}}

---

## External Dependencies

{{#if EXTERNAL_DEPS}}
| Type | Target | Notes |
|------|--------|-------|
{{EACH DEP}}| `{{type}}` | `{{target}}` | {{notes}} |
{{/EACH}}
{{else}}
_none_
{{/if}}

---

## Notes

{{#if NOTES}}
{{NOTES}}
{{else}}
_none_
{{/if}}
