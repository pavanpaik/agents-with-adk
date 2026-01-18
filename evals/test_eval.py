"""
Unit tests for Python Codebase Reviewer evaluations.

Run with: pytest eval/test_eval.py
"""
import pathlib
from google.adk.evaluation.agent_evaluator import AgentEvaluator


def test_security_reviewer():
    """Test security reviewer against eval dataset."""
    AgentEvaluator.evaluate(
        agent_module="python_codebase_reviewer.sub_agents.security_reviewer",
        eval_dataset_file_path_or_dir=str(
            pathlib.Path(__file__).parent / "eval_data/security_eval.json"
        ),
        num_runs=2,
    )


def test_architecture_reviewer():
    """Test architecture reviewer against eval dataset."""
    AgentEvaluator.evaluate(
        agent_module="python_codebase_reviewer.sub_agents.architecture_reviewer",
        eval_dataset_file_path_or_dir=str(
            pathlib.Path(__file__).parent / "eval_data/architecture_eval.json"
        ),
        num_runs=2,
    )


def test_code_quality_reviewer():
    """Test code quality reviewer against eval dataset."""
    AgentEvaluator.evaluate(
        agent_module="python_codebase_reviewer.sub_agents.code_quality_reviewer",
        eval_dataset_file_path_or_dir=str(
            pathlib.Path(__file__).parent / "eval_data/code_quality_eval.json"
        ),
        num_runs=2,
    )


def test_performance_reviewer():
    """Test performance reviewer against eval dataset."""
    AgentEvaluator.evaluate(
        agent_module="python_codebase_reviewer.sub_agents.performance_reviewer",
        eval_dataset_file_path_or_dir=str(
            pathlib.Path(__file__).parent / "eval_data/performance_eval.json"
        ),
        num_runs=2,
    )


def test_python_expert():
    """Test Python expert against eval dataset."""
    AgentEvaluator.evaluate(
        agent_module="python_codebase_reviewer.sub_agents.python_expert",
        eval_dataset_file_path_or_dir=str(
            pathlib.Path(__file__).parent / "eval_data/python_expert_eval.json"
        ),
        num_runs=2,
    )


def test_orchestrator():
    """Test orchestrator (end-to-end) against eval dataset."""
    AgentEvaluator.evaluate(
        agent_module="python_codebase_reviewer",
        eval_dataset_file_path_or_dir=str(
            pathlib.Path(__file__).parent / "eval_data/orchestrator_eval.json"
        ),
        num_runs=2,
    )


if __name__ == "__main__":
    """Run all tests when executed directly."""
    print("Running Security Reviewer eval...")
    test_security_reviewer()

    print("\nRunning Architecture Reviewer eval...")
    test_architecture_reviewer()

    print("\nRunning Code Quality Reviewer eval...")
    test_code_quality_reviewer()

    print("\nRunning Performance Reviewer eval...")
    test_performance_reviewer()

    print("\nRunning Python Expert eval...")
    test_python_expert()

    print("\nRunning Orchestrator (end-to-end) eval...")
    test_orchestrator()

    print("\n✅ All evaluations completed!")
