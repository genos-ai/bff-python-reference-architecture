# Rules

Machine-readable compliance rules in JSONL format, used by automated quality tools.

## Current Rules

| File | Scope |
|------|-------|
| `001_module_boundaries.jsonl` | Module isolation and dependency rules |
| `002_code_patterns.jsonl` | Required and prohibited code patterns |
| `003_configuration.jsonl` | Configuration management rules |
| `004_datetime_policy.jsonl` | Date/time handling rules |
| `005_data_layer.jsonl` | Data access layer rules |

## Naming Convention

```
00N_rule_category.jsonl
```

## Adding Rules

Each JSONL file contains one rule per line. Rules are consumed by `scripts/` tooling for automated compliance checks.
