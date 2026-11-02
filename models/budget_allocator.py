"""
Budget Allocator — Production Linear Programming Optimization Engine.
Recommends optimal budget allocations based on multi-dimensional sector vulnerability,
statutory finance commission floors, and absorptive capacity constraints using SciPy LP.
"""

import sys, os
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    DEFAULT_TOTAL_BUDGET, MIN_SECTOR_ALLOCATION_PCT,
    MAX_SECTOR_ALLOCATION_PCT, PRIORITY_BOOST_FACTOR,
)

try:
    from ml.src.budget_optimizer import LinearBudgetOptimizer
    _lp_optimizer = LinearBudgetOptimizer()
except Exception as e:
    print(f"[Budget Allocator] LP Optimizer module notice: {e}")
    _lp_optimizer = None


def compute_allocation(sector_scores: Dict[str, float], total_budget=None, top_n_priority=3,
                       min_pct=None, max_pct=None, boost_factor=None):
    """
    Compute constrained budget allocation.
    Uses SciPy Linear Programming optimizer if available, otherwise exact bounded distribution.
    """
    total_budget = total_budget or DEFAULT_TOTAL_BUDGET
    min_pct = min_pct or MIN_SECTOR_ALLOCATION_PCT
    max_pct = max_pct or MAX_SECTOR_ALLOCATION_PCT
    boost_factor = boost_factor or PRIORITY_BOOST_FACTOR
    n_sectors = len(sector_scores)

    sorted_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
    top_priority = [s[0] for s in sorted_sectors[:top_n_priority]]
    priority_sector = top_priority[0] if top_priority else None

    # Check if LP optimizer can be applied directly
    if _lp_optimizer is not None:
        try:
            # Map sectors into standard LP format
            lp_res = _lp_optimizer.optimize_budget(
                total_budget_lakhs=total_budget / 100000.0 if total_budget > 10000 else total_budget,
                sector_deficits=sector_scores,
                population=10000,
                priority_sector=priority_sector
            )
            explanations = lp_res.get("explanations", [])
            percentages = lp_res.get("percentages", {})

            # Convert back to original sector score naming
            allocations = []
            for rank, (sector, score) in enumerate(sorted_sectors, 1):
                pct = percentages.get(sector, min_pct)
                amount = (pct / 100.0) * total_budget
                allocations.append({
                    "sector": sector,
                    "vulnerability_score": score,
                    "allocation_pct": round(pct, 2),
                    "allocation_amount": round(amount, 2),
                    "is_priority": sector in top_priority,
                    "rank": rank,
                })

            return {
                "total_budget": total_budget,
                "allocations": allocations,
                "top_priority_sectors": top_priority,
                "explanations": explanations,
                "constraints": {"min_pct": min_pct, "max_pct": max_pct, "boost_factor": boost_factor}
            }
        except Exception as err:
            print(f"[Budget Allocator] LP optimization fallback triggered: {err}")

    # Fallback to analytical iterative constraint algorithm
    min_alloc = min_pct / 100.0
    max_alloc = max_pct / 100.0
    total_score = sum(sector_scores.values())
    if total_score == 0:
        raw_weights = {s: 1.0 / n_sectors for s in sector_scores}
    else:
        raw_weights = {s: v / total_score for s, v in sector_scores.items()}

    boosted = {}
    for sector, w in raw_weights.items():
        boosted[sector] = w * boost_factor if sector in top_priority else w
    total_b = sum(boosted.values())
    normalized = {s: w / total_b for s, w in boosted.items()}

    constrained = _apply_constraints(normalized, min_alloc, max_alloc)

    allocations = []
    for rank, (sector, _) in enumerate(sorted_sectors, 1):
        pct = constrained[sector] * 100
        amount = total_budget * constrained[sector]
        allocations.append({
            "sector": sector,
            "vulnerability_score": sector_scores[sector],
            "allocation_pct": round(pct, 2),
            "allocation_amount": round(amount, 2),
            "is_priority": sector in top_priority,
            "rank": rank,
        })

    return {
        "total_budget": total_budget,
        "allocations": allocations,
        "top_priority_sectors": top_priority,
        "constraints": {"min_pct": min_pct, "max_pct": max_pct, "boost_factor": boost_factor}
    }


def _apply_constraints(weights, min_alloc, max_alloc):
    constrained = dict(weights)
    for _ in range(50):
        changed = False
        deficit, surplus_s = 0, []
        for s, w in constrained.items():
            if w < min_alloc:
                deficit += min_alloc - w
                constrained[s] = min_alloc
                changed = True
            else:
                surplus_s.append(s)
        if deficit > 0 and surplus_s:
            st = sum(constrained[s] for s in surplus_s)
            if st > 0:
                for s in surplus_s:
                    constrained[s] = max(min_alloc, constrained[s] - deficit * (constrained[s] / st))
        excess, under_s = 0, []
        for s, w in constrained.items():
            if w > max_alloc:
                excess += w - max_alloc
                constrained[s] = max_alloc
                changed = True
            else:
                under_s.append(s)
        if excess > 0 and under_s:
            ut = sum(constrained[s] for s in under_s)
            if ut > 0:
                for s in under_s:
                    constrained[s] = min(max_alloc, constrained[s] + excess * (constrained[s] / ut))
        if not changed:
            break
    total = sum(constrained.values())
    if total > 0:
        constrained = {s: w / total for s, w in constrained.items()}
    return constrained


def format_allocation_table(result):
    lines = [f"\n{'='*70}", f"  Budget Allocation — Total: ₹{result['total_budget']:,.0f}", f"{'='*70}"]
    for a in result["allocations"]:
        p = "⭐" if a["is_priority"] else "  "
        lines.append(f"  {p} Rank {a['rank']}: {a['sector']:<25} | Score: {a['vulnerability_score']:.3f} | {a['allocation_pct']:>6.2f}% | ₹{a['allocation_amount']:>12,.2f}")
    lines.append(f"{'='*70}\n")
    return "\n".join(lines)
