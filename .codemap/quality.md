# PyQuality Index (PQI)

**Score: 77.5 / 100 — Good**

| Metric | Value |
|--------|------:|
| Files | 67 |
| Lines | 6,588 |

## Dimensions

| Dimension | Score | Confidence |
|-----------|------:|-----------:|
| Security | 100.0 | 50% |
| Elegance | 94.8 | 100% |
| Maintainability | 88.0 | 100% |
| Modularity | 79.5 | 100% |
| Reusability | 71.4 | 100% |
| Robustness | 70.4 | 100% |
| Testability | 48.4 | 100% |

## Sub-Scores

| Dimension | Sub-Score | Value |
|-----------|-----------|------:|
| Security | ast_unsafe_patterns | 100.0 |
| Security | ast_clean_file_ratio | 100.0 |
| Elegance | naming_conventions | 100.0 |
| Elegance | nesting_depth_p90 | 95.3 |
| Elegance | function_length_p90 | 90.0 |
| Maintainability | file_size_p90 | 94.0 |
| Maintainability | cohesion | 90.9 |
| Maintainability | function_length_p90 | 90.0 |
| Maintainability | doc_coverage | 79.3 |
| Modularity | circular_deps | 100.0 |
| Modularity | coupling_max_ce | 93.7 |
| Modularity | instability_balance | 68.9 |
| Modularity | size_gini | 45.8 |
| Reusability | coupling | 91.7 |
| Reusability | module_size | 88.4 |
| Reusability | api_surface_ratio | 36.5 |
| Robustness | return_type_coverage | 97.4 |
| Robustness | param_type_coverage | 74.9 |
| Robustness | exception_handling_quality | 42.9 |
| Testability | avg_nesting_depth | 89.3 |
| Testability | avg_function_length | 72.5 |
| Testability | test_code_ratio | 35.4 |
| Testability | test_file_ratio | 0.0 |

## Recommendations

### Testability

- Test-to-code ratio is 0.00 — aim for 0.8-1.2
- No test files found

### Robustness

- 3 bare/swallowed except clause(s) — catch specific exceptions
- 13 broad except(Exception) clause(s) — narrow the exception type

### Reusability

- API surface is 85% public — consider making more internals private

### Security

- Bandit error:

## Issues

| Severity | Count |
|----------|------:|
| HIGH | 5 |
| MEDIUM | 4 |
| LOW | 0 |
| **Total** | **9** |

### Robustness — 3 issues (3H / 0M / 0L)

#### swallowed-exception — 2 HIGH

| Sev | File | Line | Message | Tool |
|-----|------|-----:|---------|------|
| HIGH | modules/backend/core/logging.py | 133 | Exception swallowed (except: pass) — log or re-raise | ast |
| HIGH | modules/backend/events/publishers.py | 31 | Exception swallowed (except: pass) — log or re-raise | ast |

### Elegance — 3 issues (1H / 2M / 0L)

#### long-function — 3 (threshold: 60)

| Sev | File | Line | Entity | Value | Tool |
|-----|------|-----:|--------|------:|------|
| HIGH | modules/backend/core/logging.py | 138 | setup_logging | 104 | ast |
| MEDIUM | modules/backend/core/middleware.py | 49 | dispatch | 73 | ast |
| MEDIUM | modules/backend/core/pagination.py | 140 | create_paginated_response | 68 | ast |
