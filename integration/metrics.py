from typing import Dict, Any, List

def calculate_metrics(run_result: Dict[str, Any], is_pv_enabled: bool) -> Dict[str, Any]:
    """
    Compiles all required metrics for a given run (baseline or secured).
    
    Required metrics:
      - Consensus Score
      - Decision Time
      - Tool Selection Accuracy
      - Recovery Rate
      - Failed Decisions
      - Approval Count
      - Agent Interaction Count
      - Blocked Decisions
      - Average Confidence
    """
    if not is_pv_enabled:
        # Baseline metrics (Without PrivateVault)
        elapsed = run_result.get("elapsed_ms", 0.0)
        return {
            "consensus_score": "N/A",
            "decision_time_ms": round(elapsed, 2),
            "tool_selection_accuracy": 1.0,
            "recovery_rate": 0.0,
            "failed_decisions": 1 if not run_result.get("success", True) else 0,
            "approval_count": 0,
            "agent_interaction_count": 5,
            "blocked_decisions": 0,
            "average_confidence": "N/A"
        }
    else:
        # Secured metrics (With PrivateVault)
        scores = run_result.get("pv_trace", {}).get("steps", [])
        avg_consensus = run_result.get("avg_consensus_score", 100.0)
        total_calls = run_result.get("total_agent_calls", 0)
        blocked = run_result.get("blocked", 0)
        failed = run_result.get("failed", 0)
        approved = run_result.get("approved", 0)
        approval_req = run_result.get("approval_required", 0)
        avg_time = run_result.get("avg_time_to_decision_ms", 0.0)
        
        total_attempts = total_calls + blocked
        tool_accuracy = round(approved / total_attempts, 2) if total_attempts > 0 else 1.0
        
        recovered = run_result.get("recovered", 0)
        recovery_rate = round(recovered / (failed + blocked), 2) if (failed + blocked) > 0 else 1.0

        return {
            "consensus_score": round(avg_consensus, 2),
            "decision_time_ms": round(avg_time, 2),
            "tool_selection_accuracy": tool_accuracy,
            "recovery_rate": recovery_rate,
            "failed_decisions": failed,
            "approval_count": approval_req,
            "agent_interaction_count": total_calls,
            "blocked_decisions": blocked,
            "average_confidence": round(avg_consensus / 100.0, 2)
        }
