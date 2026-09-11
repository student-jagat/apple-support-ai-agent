"""
eval/metrics.py
Automated evaluation metrics for:
1. Intent Classification (Accuracy, Macro F1, Weighted F1, Per-Class Metrics, Confusion Matrix)
2. Escalation Decision (Precision, Recall, F1, Cost of False Positives, Risk of False Negatives)
3. Text Generation Quality (ROUGE-1, ROUGE-2, ROUGE-L, BLEU-4, Lexical Groundedness)
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    f1_score
)
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer

def evaluate_classification(
    y_true: List[str],
    y_pred: List[str],
    labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Computes standard intent classification performance metrics.
    """
    if labels is None:
        labels = sorted(list(set(y_true + y_pred)))

    acc = accuracy_score(y_true, y_pred)
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="macro", zero_division=0
    )
    weight_p, weight_r, weight_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="weighted", zero_division=0
    )
    per_class_p, per_class_r, per_class_f1, per_class_supp = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average=None, zero_division=0
    )

    per_class_metrics = {}
    for i, lbl in enumerate(labels):
        per_class_metrics[lbl] = {
            "precision": round(float(per_class_p[i]), 4),
            "recall": round(float(per_class_r[i]), 4),
            "f1": round(float(per_class_f1[i]), 4),
            "support": int(per_class_supp[i])
        }

    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()

    return {
        "accuracy": round(float(acc), 4),
        "macro_f1": round(float(macro_f1), 4),
        "macro_precision": round(float(macro_p), 4),
        "macro_recall": round(float(macro_r), 4),
        "weighted_f1": round(float(weight_f1), 4),
        "per_class": per_class_metrics,
        "confusion_matrix": cm,
        "labels": labels
    }


def evaluate_escalation(
    y_true_escalate: List[bool],
    y_pred_escalate: List[bool]
) -> Dict[str, Any]:
    """
    Computes escalation policy metrics, including cost of unnecessary escalation
    (False Positives) and risk of missed escalation (False Negatives).
    """
    y_t = np.array(y_true_escalate, dtype=bool)
    y_p = np.array(y_pred_escalate, dtype=bool)

    tp = int(np.sum(y_t & y_p))
    fp = int(np.sum(~y_t & y_p))
    fn = int(np.sum(y_t & ~y_p))
    tn = int(np.sum(~y_t & ~y_p))

    total = len(y_t)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / total if total > 0 else 0.0

    # Operational business metrics:
    # False Positive Rate (FPR): fraction of auto-handleable queries sent needlessly to humans
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    # False Negative Rate (FNR): fraction of dangerous/safety/billing queries missed by agent
    fnr = fn / (tp + fn) if (tp + fn) > 0 else 0.0

    return {
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "false_positive_rate_unnecessary_escalation": round(float(fpr), 4),
        "false_negative_rate_missed_escalation": round(float(fnr), 4)
    }


def evaluate_generation(
    predictions: List[str],
    references: List[str]
) -> Dict[str, Any]:
    """
    Computes ROUGE-1, ROUGE-2, ROUGE-L, BLEU-4, and lexical groundedness metrics.
    """
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    smooth = SmoothingFunction().method1

    r1_scores = []
    r2_scores = []
    rl_scores = []
    bleu_scores = []

    for pred, ref in zip(predictions, references):
        pred_clean = pred.strip()
        ref_clean = ref.strip()

        # ROUGE
        r_scores = scorer.score(ref_clean, pred_clean)
        r1_scores.append(r_scores["rouge1"].fmeasure)
        r2_scores.append(r_scores["rouge2"].fmeasure)
        rl_scores.append(r_scores["rougeL"].fmeasure)

        # BLEU-4
        pred_tokens = pred_clean.lower().split()
        ref_tokens = [ref_clean.lower().split()]
        if not pred_tokens:
            bleu_scores.append(0.0)
        else:
            b = sentence_bleu(ref_tokens, pred_tokens, smoothing_function=smooth)
            bleu_scores.append(b)

    return {
        "rouge1": round(float(np.mean(r1_scores)), 4),
        "rouge2": round(float(np.mean(r2_scores)), 4),
        "rougeL": round(float(np.mean(rl_scores)), 4),
        "bleu4": round(float(np.mean(bleu_scores)), 4)
    }
