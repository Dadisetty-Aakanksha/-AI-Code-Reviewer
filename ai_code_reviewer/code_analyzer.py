"""
code_analyzer.py
Main pipeline: parse → static analysis → scoring → AI review.
"""

from ai_code_reviewer.code_parser import parse_code, get_code_metrics
from ai_code_reviewer.error_detector import detect_errors, summarize_issues
from ai_code_reviewer.ai_suggestor import get_ai_suggestions


def analyze_code(code: str, run_ai: bool = True) -> dict:
    result = {}

    # 1. Parse
    parse_result = parse_code(code)
    result["parse"] = {
        "success": parse_result["success"],
        "syntax_errors": parse_result["syntax_errors"],
        "context": parse_result["context"],
    }

    # 2. Metrics
    result["metrics"] = get_code_metrics(code)

    # 3. Static issues
    issues = []
    if parse_result["success"] and parse_result["tree"]:
        issues = detect_errors(code, parse_result["tree"])
    else:
        for err in parse_result["syntax_errors"]:
            issues.append({"severity": "error", "line": 0, "message": err})

    result["issues"] = issues
    result["issue_summary"] = summarize_issues(issues)

    # 4. Score
    score, grade = _calculate_score(issues, result["metrics"])
    result["quality_score"] = score
    result["grade"] = grade

    # 5. AI
    if run_ai:
        result["ai"] = get_ai_suggestions(code)
    else:
        result["ai"] = {"suggestions": [], "security_issues": [], "optimizations": [], "summary": "AI skipped."}

    return result


def _calculate_score(issues, metrics):
    score = 100
    summary = summarize_issues(issues)
    score -= summary["error"] * 15
    score -= summary["warning"] * 5
    score -= summary["info"] * 2
    if metrics["total_lines"] > 300:
        score -= 5
    score = max(0, min(100, score))

    if score >= 90:   grade = "A"
    elif score >= 75: grade = "B"
    elif score >= 60: grade = "C"
    elif score >= 40: grade = "D"
    else:             grade = "F"

    return score, grade
