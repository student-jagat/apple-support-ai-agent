import json
import sys
import os
sys.path.insert(0, os.path.abspath("."))
from src.agent import AppleSupportAgent
from src.data_loader import load_golden_set

agent = AppleSupportAgent()
golden = load_golden_set()

missed = []
unneeded = []

for g in golden:
    resp = agent.process(g["text"], g.get("thread_context", []))
    if g["true_escalate"] and not resp.should_escalate:
        missed.append({
            "id": g["id"],
            "stratum": g.get("stratum", ""),
            "text": g["text"],
            "true_reason": g.get("escalation_reason", ""),
            "pred_intent": resp.predicted_intent,
            "conf": resp.intent_confidence,
            "agent_reason": resp.escalation_reason
        })
    elif not g["true_escalate"] and resp.should_escalate:
        unneeded.append({
            "id": g["id"],
            "stratum": g.get("stratum", ""),
            "text": g["text"],
            "agent_trigger": resp.escalation_trigger,
            "agent_reason": resp.escalation_reason
        })

print(f"Total golden: {len(golden)}")
print(f"True escalate count: {sum(1 for g in golden if g['true_escalate'])}")
print(f"Missed (False Negatives): {len(missed)}")
print(f"Unneeded (False Positives): {len(unneeded)}")
print("\nSample Missed Escalations:")
for m in missed[:8]:
    print(f"[{m['id']}] ({m['stratum']}) Pred: {m['pred_intent']} ({m['conf']:.2f})")
    print(f"  Text: {m['text']}")
    print(f"  Ground truth reason: {m['true_reason']}")
    print(f"  Agent decided: {m['agent_reason']}")
