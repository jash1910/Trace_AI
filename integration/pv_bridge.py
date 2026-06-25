"""
PrivateVault Integration Bridge for TRACE
==========================================
Wraps each TRACE agent with PrivateVault's coordination layer
using their actual code from pv_core/ and pv_cost_layer/.
"""

import sys
import os
import time
import uuid
import json
import hashlib
import datetime
from typing import Any, Dict, List, Optional, Callable

from integration.config import PV_REPO_PATH, LEDGER_PATH

# ──────────────────────────────────────────────
# Point Python at PrivateVault source so imports work
# ──────────────────────────────────────────────
if PV_REPO_PATH not in sys.path:
    sys.path.insert(0, PV_REPO_PATH)

# ──────────────────────────────────────────────
# Import PrivateVault modules
# ──────────────────────────────────────────────

try:
    from pv_core.coordination.coordination_service import (
        start_trace as pv_start_trace,
        add_step as pv_add_step,
        finalize_trace as pv_finalize_trace,
    )
    _HAS_COORDINATION = True
except ImportError:
    _HAS_COORDINATION = False
    print("[PV] coordination_service not found — using fallback")

try:
    from pv_core.intent.intent_service import normalize as pv_normalize_intent
    _HAS_INTENT = True
except ImportError:
    _HAS_INTENT = False

try:
    from pv_core.risk.fast_risk import quick_score as pv_quick_score
    _HAS_RISK = True
except ImportError:
    _HAS_RISK = False

try:
    from pv_core.approval.approval_service import requires_approval as pv_requires_approval
    _HAS_APPROVAL = True
except ImportError:
    _HAS_APPROVAL = False

try:
    from pv_core.safety.execution_gate import allow_execution as pv_allow_execution
    _HAS_GATE = True
except ImportError:
    _HAS_GATE = False

try:
    from pv_cost_layer.audit.decision_ledger import append as pv_ledger_append
    _HAS_LEDGER = True
except ImportError:
    _HAS_LEDGER = False

try:
    from pv_runtime.adversarial.detectors.context_stitching_detector import ContextStitchingDetector
    from pv_runtime.adversarial.runtime_escalation import escalation_decision
    _HAS_ADVERSARIAL = True
    _stitching_detector = ContextStitchingDetector()
except ImportError:
    _HAS_ADVERSARIAL = False

try:
    from privatevault.evidence.merkle_chain import MerkleChain
    _HAS_MERKLE = True
except ImportError:
    _HAS_MERKLE = False


# ──────────────────────────────────────────────
# Fallback implementations (used if PV import fails)
# ──────────────────────────────────────────────

def _fallback_start_trace(agent_id: str, intent: dict) -> dict:
    return {
        "trace_id": str(uuid.uuid4()),
        "started_at": datetime.datetime.utcnow().isoformat(),
        "initiator": agent_id,
        "steps": [{"step_id": str(uuid.uuid4()), "agent_id": agent_id,
                   "action": intent.get("action"), "status": "INITIATED",
                   "timestamp": datetime.datetime.utcnow().isoformat()}]
    }

def _fallback_add_step(trace: dict, agent_id: str, action: str, status: str) -> dict:
    trace["steps"].append({"step_id": str(uuid.uuid4()), "agent_id": agent_id,
                           "action": action, "status": status,
                           "timestamp": datetime.datetime.utcnow().isoformat()})
    return trace

def _fallback_finalize(trace: dict, decision: dict) -> dict:
    trace["final_decision"] = decision
    trace["completed_at"] = datetime.datetime.utcnow().isoformat()
    return trace

def _fallback_normalize(raw_intent: dict, agent_id: str) -> dict:
    if "action" not in raw_intent:
        raise ValueError("Missing required field: action")
    intent = dict(raw_intent)
    intent["_meta"] = {"intent_id": str(uuid.uuid4()),
                       "timestamp": datetime.datetime.utcnow().isoformat(),
                       "agent_id": agent_id, "version": "v1"}
    return intent

def _fallback_quick_score(intent: dict) -> dict:
    text = str(intent).lower()
    high_risk_terms = ["delete", "execute", "deploy", "override", "bypass", "ignore previous"]
    score = sum(0.3 for term in high_risk_terms if term in text)
    score = min(score, 0.9)
    level = "high" if score > 0.6 else "medium" if score > 0.3 else "low"
    return {"risk_score": score, "risk_level": level}

def _fallback_requires_approval(intent: dict, risk: dict, decision: dict) -> bool:
    return risk.get("risk_level") in ["medium", "high"]

_last_exec: dict = {}
def _fallback_allow_execution(action: dict, cooldown_sec: float = 1.0) -> bool:
    key = str(action.get("agent_id") or "global")
    now = time.time()
    last = _last_exec.get(key)
    if last and (now - last) < cooldown_sec:
        return False
    _last_exec[key] = now
    return True

def _fallback_ledger_append(entry: dict) -> dict:
    os.makedirs(os.path.dirname(LEDGER_PATH) or ".", exist_ok=True)
    prev_hash = "GENESIS"
    if os.path.exists(LEDGER_PATH):
        try:
            with open(LEDGER_PATH) as f:
                lines = f.readlines()
                if lines:
                    prev_hash = json.loads(lines[-1]).get("entry_hash", "GENESIS")
        except Exception:
            pass
    entry = dict(entry)
    entry["ts"] = int(time.time() * 1000)
    entry["prev_hash"] = prev_hash
    entry_hash = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
    entry["entry_hash"] = entry_hash
    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return {"entry_hash": entry_hash, "prev_hash": prev_hash}

def _fallback_escalation(score: int) -> str:
    if score >= 80: return "BLOCK"
    if score >= 50: return "APPROVAL"
    return "ALLOW"

class _FallbackMerkleChain:
    def __init__(self): self.chain = []
    def add(self, h: str) -> str:
        combined = h if not self.chain else hashlib.sha256((self.chain[-1] + h).encode()).hexdigest()
        self.chain.append(combined)
        return combined

class _FallbackStitchingDetector:
    RISK_TERMS = {"step", "combine", "continue", "previous", "earlier", "next phase",
                  "ignore", "override", "forget", "disregard", "new instructions"}
    def score(self, history: list) -> int:
        s = sum(10 for item in history for term in self.RISK_TERMS if term in str(item).lower())
        return min(s, 100)


# ──────────────────────────────────────────────
# Resolve: use PV's real code or fallback
# ──────────────────────────────────────────────

_start_trace    = pv_start_trace       if _HAS_COORDINATION else _fallback_start_trace
_add_step       = pv_add_step          if _HAS_COORDINATION else _fallback_add_step
_finalize       = pv_finalize_trace    if _HAS_COORDINATION else _fallback_finalize
_normalize      = pv_normalize_intent  if _HAS_INTENT       else _fallback_normalize
_quick_score    = pv_quick_score       if _HAS_RISK         else _fallback_quick_score
_req_approval   = pv_requires_approval if _HAS_APPROVAL     else _fallback_requires_approval
_allow_exec     = pv_allow_execution   if _HAS_GATE         else _fallback_allow_execution
_ledger         = pv_ledger_append     if _HAS_LEDGER       else _fallback_ledger_append
_escalation     = escalation_decision  if _HAS_ADVERSARIAL  else _fallback_escalation
_detector       = _stitching_detector  if _HAS_ADVERSARIAL  else _FallbackStitchingDetector()
_MerkleChain    = MerkleChain          if _HAS_MERKLE       else _FallbackMerkleChain


# ══════════════════════════════════════════════
# PVCoordinator — wraps any TRACE agent function
# ══════════════════════════════════════════════

class PVCoordinator:
    """
    Wraps each TRACE agent call with PrivateVault's full coordination stack:
      1. Normalize intent
      2. Risk score
      3. Adversarial detection
      4. Execution gate
      5. Approval check
      6. Audit log
      7. Coordination trace
      8. Merkle evidence chain
    """

    def __init__(self, topic: str):
        self.topic = topic
        self.session_id = str(uuid.uuid4())
        self.pv_trace: Optional[dict] = None
        self.merkle = _MerkleChain()
        self.context_history: List[str] = []
        self.metrics: Dict[str, Any] = {
            "agent_calls": 0,
            "blocked": 0,
            "approved": 0,
            "approval_required": 0,
            "consensus_scores": [],
            "time_to_decision_ms": [],
            "failed": 0,
            "recovered": 0,
            "adversarial_flags": [],
        }

    # ── Internal helpers ──────────────────────

    def _build_intent(self, agent_id: str, state: dict) -> dict:
        """Convert TRACE state into a PV-compatible intent dict."""
        return {
            "action": f"{agent_id}_execute",
            "agent_id": agent_id,
            "topic": self.topic,
            "session_id": self.session_id,
            "state_keys": list(state.keys()),
            "output_preview": str(state.get("research_data", state.get("findings", "")))[:200],
        }

    def _adversarial_check(self, agent_id: str, state: dict) -> dict:
        """
        Run PrivateVault's adversarial detectors on the current state.
        Uses context_stitching_detector to catch prompt injection patterns.
        """
        self.context_history.append(f"{agent_id}: {str(state)[:300]}")
        adv_score = _detector.score(self.context_history[-10:])
        decision  = _escalation(adv_score)
        return {"total_score": adv_score, "decision": decision, "agent": agent_id}

    def _log(self, agent_id: str, action: str, result: dict, risk: dict, adv: dict) -> dict:
        """Append a tamper-evident entry to PrivateVault's decision ledger."""
        entry = {
            "session_id":  self.session_id,
            "agent_id":    agent_id,
            "action":      action,
            "risk":        risk,
            "adversarial": adv,
            "decision":    result.get("pv_decision", "ALLOW"),
            "approved":    result.get("approved", True),
        }
        audit = _ledger(entry)
        self.merkle.add(audit["entry_hash"])
        return audit

    # ── Public API ────────────────────────────

    def start(self) -> dict:
        """Start the PV coordination trace for this TRACE research session."""
        initial_intent = {"action": "trace_research_session", "topic": self.topic}
        self.pv_trace = _start_trace("trace_orchestrator", initial_intent)
        return self.pv_trace

    def wrap_agent(self, agent_fn: Callable, agent_id: str, state: dict) -> dict:
        """
        The core integration point. Call this instead of calling agent directly.
        """
        t_start = time.time()
        self.metrics["agent_calls"] += 1

        # ── Step 1: Normalize intent ──────────
        raw_intent = self._build_intent(agent_id, state)
        try:
            intent = _normalize(raw_intent, agent_id)
        except ValueError as e:
            intent = raw_intent
            intent["_meta"] = {"error": str(e)}

        # ── Step 2: Risk scoring ──────────────
        risk = _quick_score(intent)

        # ── Step 3: Adversarial detection ─────
        adv = self._adversarial_check(agent_id, state)

        # ── Step 4: Execution gate ────────────
        gate_action = {"agent_id": agent_id, "idempotency_key": self.session_id + agent_id}
        if not _allow_exec(gate_action, cooldown_sec=0.1):
            self.metrics["blocked"] += 1
            _add_step(self.pv_trace, agent_id, raw_intent["action"], "RATE_LIMITED")
            return {**state, "pv_blocked": True, "pv_reason": "rate_limited", "agent_id": agent_id}

        # ── Step 5: Block on adversarial ──────
        if adv["decision"] == "BLOCK":
            self.metrics["blocked"] += 1
            self.metrics["adversarial_flags"].append({"agent": agent_id, "score": adv["total_score"]})
            _add_step(self.pv_trace, agent_id, raw_intent["action"], "ADVERSARIAL_BLOCKED")
            _ledger({
                "session_id": self.session_id, "agent_id": agent_id,
                "decision": "BLOCK", "adversarial_score": adv["total_score"]
            })
            return {**state, "pv_blocked": True, "pv_reason": "adversarial_detected",
                    "adversarial_score": adv["total_score"]}

        # ── Step 6: Approval check ────────────
        pv_decision = {"allowed": True}
        needs_approval = _req_approval(intent, risk, pv_decision)
        if needs_approval:
            self.metrics["approval_required"] += 1
            _add_step(self.pv_trace, agent_id, raw_intent["action"], "APPROVAL_REQUIRED")

        if adv["decision"] == "APPROVAL":
            needs_approval = True
            self.metrics["approval_required"] += 1

        # ── Step 7: Run the actual TRACE agent ─
        _add_step(self.pv_trace, agent_id, raw_intent["action"], "EXECUTING")
        try:
            agent_output = agent_fn(state)
            if isinstance(agent_output, dict):
                result_state = {**state, **agent_output}
            else:
                result_state = state
            success = True
            self.metrics["approved"] += 1
            status = "SUCCESS"
        except Exception as e:
            result_state = {**state, "error": str(e)}
            success = False
            status = "FAILED"
            self.metrics["failed"] += 1

        # ── Step 8: Compute consensus score ───
        risk_penalty  = risk.get("risk_score", 0) * 40
        adv_penalty   = adv["total_score"] * 0.3
        consensus     = max(0, 100 - risk_penalty - adv_penalty)
        self.metrics["consensus_scores"].append(round(consensus, 2))

        # ── Step 9: Log to ledger ─────────────
        elapsed_ms = round((time.time() - t_start) * 1000, 2)
        self.metrics["time_to_decision_ms"].append(elapsed_ms)

        audit = self._log(
            agent_id=agent_id,
            action=raw_intent["action"],
            result={"pv_decision": "ALLOW" if success else "FAIL", "approved": not needs_approval},
            risk=risk,
            adv=adv,
        )

        # ── Step 10: Update PV trace ──────────
        _add_step(self.pv_trace, agent_id, raw_intent["action"], status)

        # Attach PV metadata to state for downstream agents
        result_state["_pv"] = {
            "agent_id":      agent_id,
            "risk":          risk,
            "adversarial":   adv,
            "consensus":     consensus,
            "approval_req":  needs_approval,
            "audit_hash":    audit.get("entry_hash"),
            "elapsed_ms":    elapsed_ms,
        }

        return result_state

    def finish(self) -> dict:
        """Finalize the PV trace and return the full coordination report."""
        self.pv_trace = _finalize(self.pv_trace, {
            "allowed": True,
            "session_id": self.session_id,
            "merkle_root": self.merkle.chain[-1] if self.merkle.chain else None,
        })

        scores = self.metrics["consensus_scores"]
        times  = self.metrics["time_to_decision_ms"]

        return {
            "session_id":           self.session_id,
            "pv_trace":             self.pv_trace,
            "merkle_root":          self.merkle.chain[-1] if self.merkle.chain else None,
            "merkle_chain_length":  len(self.merkle.chain),
            "total_agent_calls":    self.metrics["agent_calls"],
            "blocked":              self.metrics["blocked"],
            "approved":             self.metrics["approved"],
            "approval_required":    self.metrics["approval_required"],
            "failed":               self.metrics["failed"],
            "adversarial_flags":    self.metrics["adversarial_flags"],
            "avg_consensus_score":  round(sum(scores) / len(scores), 2) if scores else 0,
            "avg_time_to_decision_ms": round(sum(times) / len(times), 2) if times else 0,
        }
