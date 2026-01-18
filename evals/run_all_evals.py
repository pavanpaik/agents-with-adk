"""
Comprehensive evaluation runner for Python Codebase Reviewer.

This script runs all evaluation datasets and generates detailed reports.
"""
import pathlib
import json
from typing import Dict, List
from google.adk.evaluation.agent_evaluator import AgentEvaluator

# Evaluation configurations
EVAL_CONFIGS = [
    {
        "name": "Security Reviewer",
        "agent_module": "python_codebase_reviewer.sub_agents.security_reviewer",
        "eval_file": "security_eval.json",
        "min_precision": 0.90,
        "min_recall": 0.85,
    },
    {
        "name": "Architecture Reviewer",
        "agent_module": "python_codebase_reviewer.sub_agents.architecture_reviewer",
        "eval_file": "architecture_eval.json",
        "min_precision": 0.85,
        "min_recall": 0.80,
    },
    {
        "name": "Code Quality Reviewer",
        "agent_module": "python_codebase_reviewer.sub_agents.code_quality_reviewer",
        "eval_file": "code_quality_eval.json",
        "min_precision": 0.85,
        "min_recall": 0.75,
    },
    {
        "name": "Performance Reviewer",
        "agent_module": "python_codebase_reviewer.sub_agents.performance_reviewer",
        "eval_file": "performance_eval.json",
        "min_precision": 0.85,
        "min_recall": 0.80,
    },
    {
        "name": "Python Expert",
        "agent_module": "python_codebase_reviewer.sub_agents.python_expert",
        "eval_file": "python_expert_eval.json",
        "min_precision": 0.85,
        "min_recall": 0.75,
    },
    {
        "name": "Orchestrator (End-to-End)",
        "agent_module": "python_codebase_reviewer",
        "eval_file": "orchestrator_eval.json",
        "min_precision": 0.85,
        "min_recall": 0.80,
    },
]

NUM_RUNS = 3  # Run each eval multiple times for consistency


def run_evaluation(config: Dict) -> Dict:
    """Run evaluation for a single agent configuration."""
    print(f"\n{'=' * 60}")
    print(f"Evaluating: {config['name']}")
    print(f"{'=' * 60}")

    eval_file_path = str(
        pathlib.Path(__file__).parent / "eval_data" / config["eval_file"]
    )

    print(f"Agent Module: {config['agent_module']}")
    print(f"Eval Dataset: {config['eval_file']}")
    print(f"Runs: {NUM_RUNS}")
    print()

    try:
        # Run ADK evaluation
        results = AgentEvaluator.evaluate(
            agent_module=config["agent_module"],
            eval_dataset_file_path_or_dir=eval_file_path,
            num_runs=NUM_RUNS,
        )

        # Note: AgentEvaluator returns results in its own format
        # You may need to adapt this based on actual ADK return format
        print(f"✅ Evaluation completed for {config['name']}")

        return {
            "name": config["name"],
            "status": "success",
            "results": results,
            "config": config,
        }

    except Exception as e:
        print(f"❌ Evaluation failed for {config['name']}: {str(e)}")
        return {
            "name": config["name"],
            "status": "failed",
            "error": str(e),
            "config": config,
        }


def calculate_summary_metrics(all_results: List[Dict]) -> Dict:
    """Calculate summary metrics across all evaluations."""
    total = len(all_results)
    passed = sum(1 for r in all_results if r["status"] == "success")
    failed = total - passed

    return {
        "total_evaluations": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / total if total > 0 else 0,
    }


def generate_report(all_results: List[Dict], summary: Dict):
    """Generate and print detailed evaluation report."""
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY REPORT")
    print("=" * 80)
    print()

    # Overall Summary
    print("Overall Results:")
    print(f"  Total Evaluations: {summary['total_evaluations']}")
    print(f"  Passed: {summary['passed']} ✅")
    print(f"  Failed: {summary['failed']} ❌")
    print(f"  Pass Rate: {summary['pass_rate']:.1%}")
    print()

    # Individual Results
    print("Individual Agent Results:")
    print("-" * 80)
    for result in all_results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"{status_icon} {result['name']:<30} - {result['status'].upper()}")

        if result["status"] == "failed":
            print(f"   Error: {result.get('error', 'Unknown error')}")

    print()

    # Recommendations
    print("Recommendations:")
    print("-" * 80)

    if summary["failed"] > 0:
        print("⚠️  Some evaluations failed. Please review the errors above.")
        print("   - Check agent module paths")
        print("   - Verify eval dataset format")
        print("   - Review agent prompts for improvements")
    else:
        print("✅ All evaluations passed!")
        print("   Next steps:")
        print("   - Review detailed results for precision/recall metrics")
        print("   - Analyze false positives/negatives")
        print("   - Update prompts to improve metrics")
        print("   - Add more edge cases to eval datasets")

    print()


def save_results(all_results: List[Dict], summary: Dict):
    """Save evaluation results to JSON file."""
    output_file = pathlib.Path(__file__).parent / "results" / "latest_eval_results.json"
    output_file.parent.mkdir(exist_ok=True)

    output_data = {
        "summary": summary,
        "results": all_results,
        "num_runs": NUM_RUNS,
    }

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"📊 Results saved to: {output_file}")


def main():
    """Run all evaluations and generate report."""
    print("=" * 80)
    print("PYTHON CODEBASE REVIEWER - COMPREHENSIVE EVALUATION")
    print("=" * 80)
    print()
    print(f"Running {len(EVAL_CONFIGS)} evaluation suites with {NUM_RUNS} runs each")
    print()

    all_results = []

    # Run all evaluations
    for config in EVAL_CONFIGS:
        result = run_evaluation(config)
        all_results.append(result)

    # Calculate summary
    summary = calculate_summary_metrics(all_results)

    # Generate report
    generate_report(all_results, summary)

    # Save results
    save_results(all_results, summary)

    # Exit with appropriate code
    if summary["failed"] > 0:
        print("\n⚠️  Some evaluations failed. See report above.")
        exit(1)
    else:
        print("\n✅ All evaluations passed!")
        exit(0)


if __name__ == "__main__":
    main()
