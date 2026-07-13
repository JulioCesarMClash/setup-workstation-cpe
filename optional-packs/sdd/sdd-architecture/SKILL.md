---
name: sdd-architecture
description: >
  Architecture selector for SDD cycles. Asks the user to choose an architecture
  pattern (Hexagonal, Clean Architecture, Screaming) and then enforces that
  pattern's layer structure, naming conventions, and dependency rules throughout
  the full SDD cycle (design → tasks → apply → verify).
  Trigger: /architecture, "aplicar arquitectura", "elegir arquitectura", "clean architecture", "hexagonal", "sdd con arquitectura"
metadata:
  version: "1.0"
  global: true
  tier: MID-HIGH
  model: opus
---

## When to Use

- Before or during `sdd-design` when the implementation requires an explicit architecture decision
- When the user says `/architecture`, "elegir arquitectura", "aplicar clean architecture", "hexagonal", or similar
- When starting a new module, service, or project from scratch inside an SDD cycle

## Step 1 — Architecture Selection

**ALWAYS ask first. Never assume.**

Present the three options and wait for the user's choice:

```
Which architecture pattern do you want to apply?

1. Hexagonal (Ports & Adapters)
2. Clean Architecture (Uncle Bob)
3. Screaming Architecture (Feature-first)
```

Do not continue until the user answers.

---

## Option 1 — Hexagonal Architecture (Ports & Adapters)

### Core Principle
The domain is the center. External systems (DB, HTTP, queues) are adapters that plug into ports (interfaces). The domain never imports from adapters.

### Canonical Layer Structure

```
src/
  domain/           # Pure business logic. Zero external imports.
    entities/
    value_objects/
    exceptions/
  application/      # Use cases. Orchestrates domain. Imports ports only.
    use_cases/
    services/
  ports/            # Interfaces (abstract classes / protocols). No implementations.
    inbound/        # What the outside world calls into the app
    outbound/       # What the app calls out to (DB, APIs, queues)
  adapters/
    inbound/        # HTTP controllers, CLI handlers, event consumers
    outbound/       # DB repositories, HTTP clients, queue publishers
  infrastructure/   # Framework wiring, DI container, config
```

### Dependency Rule
```
adapters → ports ← application → domain
```
- `domain` imports nothing outside stdlib
- `application` imports `domain` + `ports` only
- `adapters` implement `ports`; they may import `application` and `domain`
- `infrastructure` wires everything together

### Naming Conventions
- Ports: `{Entity}Repository`, `{Entity}Service`, `{Action}Port`
- Inbound adapters: `{Entity}Controller`, `{Entity}Consumer`
- Outbound adapters: `{Entity}RepositoryImpl`, `{Api}Client`
- Use cases: `{Verb}{Entity}UseCase` (e.g., `CreateOrderUseCase`)

### SDD Design Checklist (enforce in sdd-design)
- [ ] No domain entity imports from adapters or infrastructure
- [ ] Every outbound dependency is behind a port (interface)
- [ ] Use cases receive ports via constructor injection (DI)
- [ ] Tests mock ports, never concrete adapters

---

## Option 2 — Clean Architecture (Uncle Bob)

### Core Principle
Four concentric rings. Dependency rule: source code dependencies point INWARD only. The outer rings know about inner rings; inner rings know nothing about outer rings.

### Canonical Ring Structure

```
src/
  entities/          # Ring 1 — Enterprise business rules. Pure domain objects.
    {Entity}.py/.ts
  use_cases/         # Ring 2 — Application business rules. Orchestrates entities.
    {Verb}{Entity}Interactor.py/.ts
  interface_adapters/ # Ring 3 — Converts data between use cases and external format.
    controllers/
    presenters/
    gateways/        # DB gateway interfaces + implementations
  frameworks_drivers/ # Ring 4 — DB, UI, web frameworks, external APIs.
    db/
    web/
    external/
```

### Dependency Rule
```
frameworks_drivers → interface_adapters → use_cases → entities
```
NEVER the reverse. An entity must not import anything from ring 3 or 4.

### Naming Conventions
- Entities: plain nouns (`Order`, `User`, `Invoice`)
- Use Cases / Interactors: `{Verb}{Entity}Interactor` or `{Verb}{Entity}UseCase`
- Gateways: `{Entity}Gateway` (interface in ring 3, implementation in ring 4)
- Controllers: `{Entity}Controller`
- Presenters: `{Entity}Presenter`

### Data Crossing Boundaries
Data that crosses a ring boundary must be converted to a simple DTO/struct.
Never pass an entity object from ring 1 directly into ring 4.

### SDD Design Checklist (enforce in sdd-design)
- [ ] Entities have no imports from use_cases, interface_adapters, or frameworks_drivers
- [ ] Use cases depend only on entities and gateway interfaces (not implementations)
- [ ] Controllers call use case input ports; presenters implement output ports
- [ ] DB implementations live in ring 4 and implement ring 3 gateway interfaces
- [ ] DTOs defined at each boundary crossing

---

## Option 3 — Screaming Architecture (Feature-first)

### Core Principle
The top-level structure screams what the system does, not what framework it uses. Features are the primary organizing unit; layers are secondary and live inside each feature.

### Canonical Directory Structure

```
src/
  {feature_a}/           # e.g., orders/, billing/, users/
    domain/
    use_cases/
    api/                 # HTTP routes / controllers for this feature
    repository/          # DB access for this feature
    dto/
    tests/
  {feature_b}/
    ...
  shared/                # Cross-feature utilities only (no business logic)
    auth/
    events/
    config/
  main.py / app.ts       # Bootstrap only
```

### Dependency Rule
- Features must NOT import from each other's internals
- Cross-feature communication via shared events or a dedicated public API surface
- `shared/` can be imported by any feature; features cannot import from `shared/`'s internals (only the public exports)

### Naming Conventions
- Feature dirs: plural nouns (`orders/`, `users/`, `billing/`)
- Within a feature: follow clean or hexagonal conventions internally
- Cross-feature events: `{Feature}{Action}Event` (e.g., `OrderPlacedEvent`)

### SDD Design Checklist (enforce in sdd-design)
- [ ] No feature directly imports from another feature's internal modules
- [ ] Cross-feature data flows through events or a declared public interface
- [ ] `shared/` contains zero business logic
- [ ] Each feature is independently testable without other features loaded

---

## Step 2 — SDD Integration

Once the architecture is chosen, inject the following into the SDD phases:

### In sdd-design
- Declare the chosen architecture explicitly in the design doc
- Map each component being built to its layer
- Flag any proposed dependency that violates the chosen rule

### In sdd-tasks
- Group tasks by layer (not by feature) when using Hexagonal or Clean
- Group tasks by feature when using Screaming
- Add a "Layer compliance" task to verify boundaries before marking apply done

### In sdd-apply
- Enforce the layer structure when creating files — no shortcuts
- Reject any import that crosses a boundary in the wrong direction
- Flag violations immediately rather than deferring to verify

### In sdd-verify
- Run the architecture checklist for the chosen option (listed above)
- Verify at least one test exercises each layer boundary
- Confirm the top-level directory structure matches the chosen pattern

---

## What NOT to do

- Do not mix patterns (e.g., hexagonal naming inside a screaming structure) without explicit user approval
- Do not let the framework's default structure override the chosen architecture
- Do not generate code before the architecture is chosen and confirmed
- Do not create `utils/` or `helpers/` at the root level — it's always a smell; put it in `shared/` (Screaming) or `infrastructure/` (Hexagonal/Clean)
