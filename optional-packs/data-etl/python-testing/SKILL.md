---
name: python-testing
description: >
  Author and run pytest tests for Python code (ETL scripts, local_router.py,
  export utilities). Use when writing or extending pytest tests, adding
  coverage to Python code, setting up fixtures/parametrize, or when the user
  says "write tests", "pytest", "test this Python". For ETL/data tests, defer
  to DQS obligations which override Ponytail in test code.
license: MIT
metadata:
  tier: MID-HIGH
---

# python-testing

## Core layout

- Files: `test_*.py`.
- Structure: Arrange-Act-Assert. One assertion concern per test — don't bundle unrelated checks.

```python
def test_export_user_count():
    # Arrange
    data = setup_mock_users(count=10)
    exporter = UserExporter()
    # Act
    result = exporter.execute(data)
    # Assert
    assert len(result) == 10
```

## Parametrize and fixtures

```python
@pytest.mark.parametrize("input_val, expected", [(None, 0), ("", 0), ("valid", 1)])
def test_parser_edge_cases(input_val, expected):
    assert parse_logic(input_val) == expected

@pytest.fixture
def temp_file(tmp_path):
    return tmp_path / "test_output.csv"
```

Use `monkeypatch` for env vars and `tmp_path` for filesystem isolation — relevant for export scripts that write files to disk.

## DQS — mandatory for ETL/data code

When the code under test is ETL or data-pipeline related, **DQS obligations override Ponytail/YAGNI**. Cosmetic tests (`len() > 0`, `is not None`) are prohibited. Required test cases:

1. **Cardinalidad Exacta por Grano Dimensional** — assert exact row counts per population, never just `len() > 0`.
2. **Reconciliación Dimensional Exacta** — sum of sub-totals by any dimension must equal the global total exactly.
3. **Control de Fan-Out Dimensional** — cross-joined dimensions must not multiply totals; `sum(sub-dimension) > sum(total)` is the fan-out signal.
4. **Idempotencia Real Destructiva** — run the pipeline twice on the same cutoff; assert only one run survives and both totals are identical.
5. **Erradicación de Filas Huérfanas** — after any replace/upsert, assert zero rows remain from a previous `run_id` via direct query, never inferred from totals alone.

Full doc: `000_SISTEMA_OPERATIVO/000_Gobernanza_Data_Quality_Shield.md`.

## Run and read failures

- Run: `pytest -v`
- If a DQS assertion fails, the pipeline is structurally broken — fix the code, never loosen the assertion to match bad data.

## Ponytail note

Don't test stdlib functions or trivial getters/setters. Test behavior and boundaries — that's where bugs live.

## Out of scope

Coverage tooling / CI gates, frameworks other than pytest (no unittest, no nose), mocking beyond stdlib `unittest.mock` + pytest's `monkeypatch`, property-based testing (hypothesis).
