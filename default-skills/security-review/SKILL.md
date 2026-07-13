---
name: security-review
description: >
  OWASP-style secure-code review for general application code. Use when
  reviewing code for security issues, before merging stakeholder-facing
  features, or when the user says "security review", "is this safe",
  "owasp", or "revisar seguridad".
license: MIT
metadata:
  tier: MEDIUM
---

# security-review

## First action — secret sweep

Before any logic review, grep the source tree for hardcoded credentials.

## Review checklist — OWASP Top 10, condensed

- [ ] Injection — unsanitized input reaching SQL/NoSQL/command execution.
- [ ] Broken auth — JWT validation logic, password hashing implementation.
- [ ] XSS — `innerHTML` usage or missing output encoding in UI components.
- [ ] Broken access control — authorization enforced server-side, not just hidden in the UI.
- [ ] Secrets exposure — keys/tokens committed to version control.
- [ ] Insecure deserialization — `eval()` or libraries parsing untrusted external data.
- [ ] SSRF — user-provided URLs used in server-side HTTP requests without validation.
- [ ] Insufficient logging — security events logged without leaking PII.

## Output format

One block per finding:

```text
Location: file_path:line_number
Severity: High | Med | Low
Recommendation: concise technical fix
```

## Defer-to rules

- ETL or data-pipeline security → use a dedicated ETL security workflow instead.
- Over-engineering / complexity complaints → use a simplification review, not this skill.
- Infra/network/cloud security → out of scope, report as external to code.

## Out of scope

Automated scanner integration, infra/network/cloud security, auto-fixing, or silent code patching.
