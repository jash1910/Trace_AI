import time
from typing import Callable, Dict, Any

from integration.pv_bridge import PVCoordinator
from integration.attack_simulator import AttackSimulator
from integration.benchmark_report import generate_report

def run_without_pv(
    research_agent_fn: Callable,
    fact_checker_fn:   Callable,
    analyst_fn:        Callable,
    visualization_fn:  Callable,
    writer_fn:         Callable,
    topic: str,
) -> Dict[str, Any]:
    """Runs the TRACE pipeline sequentially without any PrivateVault controls."""
    t_start = time.time()
    state = {"topic": topic, "depth": "detailed"}

    try:
        # Merge outputs at each step since our agents return partial state dictionaries
        res_research = research_agent_fn(state)
        state = {**state, **res_research}
        
        res_checker = fact_checker_fn(state)
        state = {**state, **res_checker}
        
        res_analyst = analyst_fn(state)
        state = {**state, **res_analyst}
        
        res_viz = visualization_fn(state)
        state = {**state, **res_viz}
        
        res_writer = writer_fn(state)
        state = {**state, **res_writer}
        
        success = True
    except Exception as e:
        state["error"] = str(e)
        success = False

    return {
        "mode": "WITHOUT_PRIVATEVAULT",
        "topic": topic,
        "success": success,
        "elapsed_ms": round((time.time() - t_start) * 1000, 2),
        "state": state,
        "audit_trail": None,
        "adversarial_protection": False,
        "consensus_score": None,
    }

def run_with_pv(
    research_agent_fn: Callable,
    fact_checker_fn:   Callable,
    analyst_fn:        Callable,
    visualization_fn:  Callable,
    writer_fn:         Callable,
    topic: str,
) -> Dict[str, Any]:
    """Runs the TRACE pipeline sequentially with PrivateVault wrapping each agent execution."""
    t_start = time.time()
    coordinator = PVCoordinator(topic=topic)
    coordinator.start()

    state = {"topic": topic, "depth": "detailed"}

    agent_pipeline = [
        (research_agent_fn,  "research_agent"),
        (fact_checker_fn,    "fact_checker_agent"),
        (analyst_fn,         "analyst_agent"),
        (visualization_fn,   "visualization_agent"),
        (writer_fn,          "writer_agent"),
    ]

    for agent_fn, agent_id in agent_pipeline:
        state = coordinator.wrap_agent(agent_fn, agent_id, state)
        if state.get("pv_blocked"):
            break

    report = coordinator.finish()
    report["mode"] = "WITH_PRIVATEVAULT"
    report["topic"] = topic
    report["elapsed_ms"] = round((time.time() - t_start) * 1000, 2)
    report["state"] = state

    return report

def execute_benchmark(
    research_agent_fn: Callable,
    fact_checker_fn:   Callable,
    analyst_fn:        Callable,
    visualization_fn:  Callable,
    writer_fn:         Callable,
    topic: str,
) -> Dict[str, Any]:
    """
    Main benchmark orchestrator:
      1. Run pipeline without PrivateVault
      2. Run pipeline with PrivateVault
      3. Run attack simulations
      4. Compare and generate reports
    """
    print("\n" + "=" * 60)
    print("  TRACE + PrivateVault Benchmark")
    print("=" * 60)

    # 1. Baseline run (Without PV)
    print("\n📊 RUN #1 — Without PrivateVault (Baseline)\n")
    without_pv = run_without_pv(
        research_agent_fn=research_agent_fn,
        fact_checker_fn=fact_checker_fn,
        analyst_fn=analyst_fn,
        visualization_fn=visualization_fn,
        writer_fn=writer_fn,
        topic=topic
    )
    print(f"  ✅ Completed in {without_pv['elapsed_ms']}ms")
    print("  ❌ No audit trail | No adversarial protection | No consensus score")

    # 2. Secured run (With PV)
    print("\n🔐 RUN #2 — With PrivateVault Coordination\n")
    with_pv = run_with_pv(
        research_agent_fn=research_agent_fn,
        fact_checker_fn=fact_checker_fn,
        analyst_fn=analyst_fn,
        visualization_fn=visualization_fn,
        writer_fn=writer_fn,
        topic=topic
    )
    print(f"  ✅ Completed in {with_pv['elapsed_ms']}ms")
    print(f"  🔍 Consensus score:    {with_pv.get('avg_consensus_score')}")
    print(f"  📋 Audit entries:      {with_pv.get('merkle_chain_length')}")
    print(f"  🔗 Merkle root:        {str(with_pv.get('merkle_root', ''))[:16]}...")
    print(f"  🚨 Adversarial flags:  {len(with_pv.get('adversarial_flags', []))}")
    print(f"  ⏱  Avg decision time:  {with_pv.get('avg_time_to_decision_ms')}ms")

    # 3. Attack simulations
    print("\n⚔️  ATTACK SIMULATIONS\n")
    simulator = AttackSimulator()
    simulator.run_all()
    attack_summary = simulator.summary()

    for r in attack_summary["results"]:
        status = "🛡️  BLOCKED" if r["blocked"] else "⚠️  PASSED THROUGH"
        print(f"  {status} | {r['attack']:<30} | score: {r['adversarial_score']}")

    print(f"\n  Block rate: {attack_summary['block_rate']} ({attack_summary['blocked']}/{attack_summary['total_attacks']} attacks stopped)")

    # 4. Generate final reports
    print("\n📝 BENCHMARK REPORT\n")
    report = generate_report(without_pv, with_pv, attack_summary)
    
    rec = report["benchmark_report"]["recommendation"]
    print(f"  Deploy without PrivateVault? {rec['deploy_without_pv']}")
    print("\n  Key risks without PV:")
    for r in rec["risks_without_pv"]:
        print(f"    • {r}")
    print("\n  Improvements with PV:")
    for i in rec["improvements_with_pv"]:
        print(f"    ✓ {i}")

    print("\n" + "=" * 60)
    print("  Done. benchmark_report.json and pv_audit_ledger.jsonl created.")
    print("=" * 60 + "\n")
    
    return report
