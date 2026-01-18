# Python Codebase Reviewer - Evaluation Suite

Comprehensive evaluation datasets and metrics for measuring the quality and accuracy of the Python Codebase Reviewer agent system.

## Evaluation Philosophy

A production-ready code review system must:

1. **High Precision**: Findings should be valid (low false positive rate)
2. **High Recall**: Should catch real issues (low false negative rate)
3. **Correct Severity**: Critical issues marked critical, not low
4. **Actionable**: Provide working code fixes
5. **Context-Aware**: Different standards for tests, examples, etc.
6. **No Over-Flagging**: Don't overwhelm with minor issues

## Evaluation Metrics

### Primary Metrics

1. **Precision** = True Positives / (True Positives + False Positives)
   - Measures: How many flagged issues are actually issues?
   - Target: ≥ 90%

2. **Recall** = True Positives / (True Positives + False Negatives)
   - Measures: How many actual issues were caught?
   - Target: ≥ 85% for CRITICAL/HIGH, ≥ 75% for MEDIUM/LOW

3. **F1 Score** = 2 × (Precision × Recall) / (Precision + Recall)
   - Balanced measure
   - Target: ≥ 0.85

4. **Severity Accuracy** = Correctly classified severity / Total findings
   - Measures: Are severities correct?
   - Target: ≥ 90%

### Secondary Metrics

5. **False Positive Rate** = False Positives / (False Positives + True Negatives)
   - Target: ≤ 10%

6. **Tool Usage Accuracy** = Correct agent invocations / Total invocations
   - Measures: Does orchestrator call right agents?
   - Target: ≥ 95%

7. **Actionability Score** = Findings with valid fixes / Total findings
   - Target: 100%

8. **Coverage** = Categories tested / Total categories
   - Ensures comprehensive testing

## Evaluation Dataset Structure

Each eval dataset follows ADK format:

```json
[
  {
    "query": "Review this code:\n```python\n[code here]\n```",
    "expected_tool_use": ["security_reviewer"],
    "reference": {
      "expected_findings": [
        {
          "type": "SECURITY",
          "severity": "CRITICAL",
          "title": "SQL Injection",
          "line": 2,
          "must_detect": true
        }
      ],
      "should_not_flag": [
        "Test fixture data is not a security issue"
      ],
      "min_findings": 1,
      "max_findings": 3
    }
  }
]
```

## Evaluation Datasets

### 1. Security Reviewer Evals (`security_eval.json`)

Tests:
- ✅ OWASP Top 10 vulnerabilities (SQL injection, XSS, etc.)
- ✅ Python-specific issues (pickle, eval, shell=True)
- ✅ Secrets detection (API keys, passwords)
- ✅ Framework-specific (Django CSRF, Flask debug mode)
- ❌ Clean code (should not flag)
- ❌ Test fixtures (should not flag as hardcoded secrets)

Metrics:
- Precision: Are flagged issues real vulnerabilities?
- Recall: Did we catch all critical vulnerabilities?
- Severity: Is SQL injection marked CRITICAL?

### 2. Architecture Reviewer Evals (`architecture_eval.json`)

Tests:
- ✅ SOLID violations (God class, tight coupling)
- ✅ Design pattern opportunities
- ✅ Anti-patterns (circular dependencies)
- ❌ Good architecture (should not flag)
- ❌ Acceptable trade-offs

Metrics:
- Precision: Are architectural suggestions valid?
- Recall: Did we catch major design issues?
- Actionability: Are refactoring suggestions practical?

### 3. Code Quality Reviewer Evals (`code_quality_eval.json`)

Tests:
- ✅ PEP 8 violations
- ✅ Non-Pythonic code
- ✅ Missing type hints/docstrings
- ✅ Code smells
- ❌ Consistent style (should not over-flag)
- ❌ Existing patterns (don't flag for being different)

Metrics:
- Precision: Are PEP violations real?
- Recall: Did we catch readability issues?
- Balance: Not too pedantic?

### 4. Performance Reviewer Evals (`performance_eval.json`)

Tests:
- ✅ O(n²) algorithms where O(n) exists
- ✅ N+1 queries
- ✅ Memory inefficiency
- ❌ Acceptable algorithms (O(n log n) is fine for sorting)
- ❌ Readable code over micro-optimizations

Metrics:
- Precision: Are performance issues real bottlenecks?
- Recall: Did we catch major inefficiencies?
- Practicality: Focus on real bottlenecks, not micro-opts?

### 5. Python Expert Evals (`python_expert_eval.json`)

Tests:
- ✅ Missed standard library usage
- ✅ Framework anti-patterns
- ✅ Non-idiomatic code
- ❌ Correct usage (should not suggest changes)

Metrics:
- Precision: Are suggestions actually better?
- Expertise: Does it demonstrate deep Python knowledge?

### 6. End-to-End Orchestrator Evals (`orchestrator_eval.json`)

Tests:
- ✅ Multi-issue code (security + performance + quality)
- ✅ Correct agent selection
- ✅ Finding aggregation
- ✅ Deduplication
- ✅ Prioritization

Metrics:
- Tool usage: Right agents called?
- Completeness: All issues found?
- Report quality: Well-structured output?

## Running Evaluations

### Individual Agent Evaluation

```python
from google.adk.evaluation.agent_evaluator import AgentEvaluator
import pathlib

# Evaluate security reviewer
AgentEvaluator.evaluate(
    agent_module="python_codebase_reviewer.sub_agents.security_reviewer",
    eval_dataset_file_path_or_dir=str(
        pathlib.Path(__file__).parent / "eval_data/security_eval.json"
    ),
    num_runs=3  # Run multiple times for consistency
)
```

### Full System Evaluation

```python
# Evaluate orchestrator (end-to-end)
AgentEvaluator.evaluate(
    agent_module="python_codebase_reviewer",
    eval_dataset_file_path_or_dir=str(
        pathlib.Path(__file__).parent / "eval_data/orchestrator_eval.json"
    ),
    num_runs=3
)
```

### Run All Evals

```bash
cd python_codebase_reviewer
python eval/run_all_evals.py
```

## Evaluation Categories

### True Positive Tests (Should Flag)

1. **Critical Security Issues**
   - SQL injection
   - Command injection
   - Hardcoded secrets
   - Authentication bypass

2. **High Severity Issues**
   - N+1 queries
   - O(n²) in hot paths
   - Major SOLID violations

3. **Medium Severity Issues**
   - Missing type hints
   - PEP 8 violations
   - Code smells

4. **Low Severity Issues**
   - Non-Pythonic patterns
   - Minor optimizations

### True Negative Tests (Should NOT Flag)

1. **Clean Code**
   - Well-written, secure code
   - Proper patterns used correctly

2. **Acceptable Patterns**
   - Test fixtures (not "hardcoded data")
   - Configuration files
   - Intentional design choices

3. **Context-Appropriate**
   - Simple scripts (don't need architecture)
   - Example code (different standards)

### Edge Cases

1. **Framework-Specific**
   - Django-specific patterns
   - Flask-specific patterns
   - FastAPI-specific patterns

2. **Python Version**
   - Modern features (3.10+)
   - Deprecated features

3. **Code Type**
   - Production code
   - Test code
   - Example/tutorial code
   - Scripts vs libraries

## Success Criteria

### Minimum Passing Scores (MVP)

- **Precision**: ≥ 85% (few false positives)
- **Recall**: ≥ 80% for CRITICAL/HIGH (catch serious issues)
- **Severity Accuracy**: ≥ 85% (right severity)
- **Tool Usage**: ≥ 90% (right agents called)

### Production-Ready Scores

- **Precision**: ≥ 90%
- **Recall**: ≥ 85% for CRITICAL/HIGH, ≥ 75% for MEDIUM/LOW
- **Severity Accuracy**: ≥ 90%
- **Tool Usage**: ≥ 95%
- **F1 Score**: ≥ 0.85

### Gold Standard Scores

- **Precision**: ≥ 95%
- **Recall**: ≥ 90% for CRITICAL/HIGH, ≥ 80% for MEDIUM/LOW
- **Severity Accuracy**: ≥ 95%
- **Tool Usage**: ≥ 98%
- **F1 Score**: ≥ 0.90

## Continuous Evaluation

### Regression Testing

Run evals on every prompt change to ensure:
- No regression in precision/recall
- New capabilities don't introduce false positives
- Performance remains acceptable

### Dataset Growth

Continuously add eval cases from:
- User feedback (false positives/negatives)
- New vulnerability types
- New Python versions
- New framework patterns

### Metrics Tracking

Track over time:
- Precision/recall trends
- False positive rate
- Severity accuracy
- Response time

## Evaluation Reports

Each evaluation run generates:

```
=== Evaluation Report ===
Agent: security_reviewer
Dataset: security_eval.json
Runs: 3

Metrics:
- Precision: 92.5% ✅
- Recall: 87.3% ✅
- F1 Score: 0.897 ✅
- Severity Accuracy: 91.2% ✅

Tool Usage:
- Correct invocations: 95.8% ✅

False Positives: 3
- Test fixture flagged as hardcoded secret (line 45)
- Configuration constant flagged as magic number (line 12)
- Intentional globals flagged (line 78)

False Negatives: 2
- Missed timing attack vulnerability (line 102)
- Missed XXE vulnerability (line 156)

Recommendations:
- Update prompt to recognize test fixture patterns
- Add timing attack examples to security knowledge
- Add XXE detection examples
```

## Next Steps

1. **Create eval datasets** for each agent
2. **Run baseline evaluations** to establish current performance
3. **Iterate on prompts** to improve metrics
4. **Add edge cases** discovered during testing
5. **Track metrics over time** for continuous improvement
6. **Automate eval runs** in CI/CD pipeline

---

A comprehensive eval suite is what separates a demo from a production-ready system!
