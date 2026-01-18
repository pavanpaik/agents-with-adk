# Evaluation Datasets

Comprehensive evaluation datasets for testing the Python Codebase Reviewer agents.

## Datasets Overview

| Dataset | Agent | Test Cases | Focus Areas |
|---------|-------|------------|-------------|
| `security_eval.json` | Security Reviewer | 16 | OWASP Top 10, Python security vulnerabilities |
| `architecture_eval.json` | Architecture Reviewer | 8 | SOLID principles, design patterns, anti-patterns |
| `code_quality_eval.json` | Code Quality Reviewer | 8 | PEP standards, Pythonic idioms, code smells |
| `performance_eval.json` | Performance Reviewer | 8 | Algorithm complexity, memory, database queries |
| `python_expert_eval.json` | Python Expert | 8 | Standard library, frameworks, modern Python |
| `orchestrator_eval.json` | Orchestrator | 7 | Multi-issue code, agent coordination |

## Test Coverage

### Security Reviewer (16 test cases)

**True Positives** (14 cases):
- SQL Injection (2 variations)
- Insecure Deserialization (pickle)
- Hardcoded Secrets (SECRET_KEY, AWS credentials)
- Command Injection
- SSRF
- Weak Password Hashing (MD5)
- Timing Attack vulnerability
- Mass Assignment
- CSRF Protection Disabled
- Unsafe YAML Loading
- XXE (XML External Entity)
- Path Traversal
- Weak Random Number Generation
- Multi-issue code (5 vulnerabilities)

**True Negatives** (2 cases):
- Secure code with parameterized queries
- Test fixtures (should NOT flag)

### Architecture Reviewer (8 test cases)

**SOLID Principle Tests**:
- Single Responsibility Principle (SRP)
- Open/Closed Principle (OCP)
- Liskov Substitution Principle (LSP)
- Interface Segregation Principle (ISP)
- Dependency Inversion Principle (DIP)

**Anti-Pattern Tests**:
- God Object
- Circular Dependency

**True Negatives**:
- Well-architected code

### Code Quality Reviewer (8 test cases)

**PEP Standards**:
- PEP 8 violations (naming, spacing)
- PEP 484 (missing type hints)
- PEP 257 (missing docstrings)

**Code Smells**:
- Long Method
- Magic Numbers
- Duplicated Code

**Pythonic Code**:
- Non-Pythonic patterns (should use comprehensions)

**True Negatives**:
- Clean, Pythonic code with type hints and docstrings

### Performance Reviewer (8 test cases)

**Algorithm Issues**:
- O(n²) where O(n) is possible
- String concatenation in loop

**Database**:
- N+1 query problem

**Memory**:
- Loading entire file into memory

**Data Structures**:
- Using list for membership testing (should use set)

**Caching**:
- Missing caching for expensive calculations

**Concurrency**:
- Sequential I/O operations (should use async/concurrency)

**True Negatives**:
- Efficient code with caching and optimal algorithms

### Python Expert (8 test cases)

**Standard Library**:
- Manual grouping instead of defaultdict
- Manual flattening instead of itertools.chain
- os.path instead of pathlib

**Framework Best Practices**:
- Django: Missing select_related

**Pythonic Idioms**:
- Manual resource management instead of context manager

**Async/Await**:
- Blocking call in async function
- Sequential await instead of gather

**Modern Python**:
- .format() instead of f-strings
- Manual __init__ instead of dataclass

**True Negatives**:
- Expert-level Python code

### Orchestrator (7 test cases)

**Multi-Issue Code**:
- Security + Quality issues
- Security + Architecture + Performance + Python issues
- Performance + Quality + Python issues
- Architecture + Quality issues

**Targeted Reviews**:
- Security-focused review
- Django view with N+1 queries

**True Negatives**:
- Clean, well-written code (should have minimal findings)

## Evaluation Metrics

Each evaluation measures:

1. **Precision**: Are flagged issues actually issues?
   - Target: ≥ 90%

2. **Recall**: Are all real issues caught?
   - Target: ≥ 85% for CRITICAL/HIGH, ≥ 75% for MEDIUM/LOW

3. **Severity Accuracy**: Are severities correct?
   - Target: ≥ 90%

4. **Tool Usage** (Orchestrator only): Are correct agents called?
   - Target: ≥ 95%

5. **False Positive Rate**: How many false alarms?
   - Target: ≤ 10%

## Running Evaluations

### Individual Agent

```bash
# Run security reviewer eval
pytest eval/test_eval.py::test_security_reviewer

# Run architecture reviewer eval
pytest eval/test_eval.py::test_architecture_reviewer

# Run all agent evals
pytest eval/test_eval.py
```

### All Evaluations

```bash
# Run comprehensive evaluation suite
python eval/run_all_evals.py
```

### Results

Results are saved to `eval/results/latest_eval_results.json`

## Adding New Test Cases

When adding new test cases:

1. **Identify the gap**: What issue type is not covered?
2. **Write the code**: Create a realistic code example
3. **Define expectations**: Specify what should be detected
4. **Add to dataset**: Insert into appropriate JSON file
5. **Run eval**: Verify the agent detects it
6. **Iterate**: Update prompts if necessary

### Example Test Case

```json
{
  "query": "Review this code:\n```python\n[code here]\n```",
  "expected_tool_use": [],
  "reference": {
    "must_detect": [
      {
        "type": "SECURITY",
        "severity": "CRITICAL",
        "issue": "SQL Injection",
        "line": 2
      }
    ],
    "must_provide_fix": true,
    "fix_should_include": ["parameterized query"]
  }
}
```

## Test Case Guidelines

### True Positive Tests

✅ **Do**:
- Use realistic code examples
- Cover common vulnerability patterns
- Include edge cases
- Vary code style and frameworks

❌ **Don't**:
- Use overly simplistic examples
- Mix too many issues in one test (except multi-issue tests)
- Use outdated code patterns

### True Negative Tests

✅ **Do**:
- Include well-written, secure code
- Test boundary cases (test fixtures, config files)
- Verify agents don't over-flag

❌ **Don't**:
- Forget to test true negatives
- Only test positive cases

### Severity Guidelines

- **CRITICAL**: Remote code execution, SQL injection, hardcoded secrets
- **HIGH**: XSS, CSRF, N+1 queries, major SOLID violations
- **MEDIUM**: Missing type hints, PEP violations, code smells
- **LOW**: Minor style issues, non-Pythonic patterns

## Continuous Improvement

1. **Track False Positives**: Log when agents incorrectly flag clean code
2. **Track False Negatives**: Log when agents miss real issues
3. **Add Edge Cases**: Continuously expand test coverage
4. **Update Prompts**: Improve prompts based on eval results
5. **Monitor Metrics**: Track precision/recall over time

---

A comprehensive eval suite is what separates a demo from a production system!
