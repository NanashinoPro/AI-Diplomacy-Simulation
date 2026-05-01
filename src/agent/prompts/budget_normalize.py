"""
B-01: Budget Allocation Agent (flash-lite)
Each task agent's independent budget requests (B$) are reconciled against government revenue.
"""
from models import PresidentPolicy


def build_budget_normalize_prompt(
    country_name: str,
    policy: PresidentPolicy,
    request_military: float,
    request_intelligence: float,
    request_economy: float,
    request_welfare: float,
    request_education: float,
    request_nuclear: float,
    government_budget: float,
    national_debt: float,
    economy: float,
) -> str:
    total_request = request_military + request_intelligence + request_economy + request_welfare + request_education + request_nuclear
    deficit = max(0, total_request - government_budget)
    debt_ratio = national_debt / max(1.0, economy) * 100
    stance = policy.stance
    directives_str = "\n".join(f"・{d}" for d in policy.directives)

    return f"""You are the budget allocation officer of '{country_name}'.
Review each ministry's budget request (B$ units) and finalize the allocation.

【🏛️ Presidential Policy ({stance})】
{directives_str}

【💰 Fiscal Status】
  Government Revenue (tax + tariff - interest): {government_budget:.1f} B$
  National Debt:                                 {national_debt:.1f} B$ (Debt/GDP: {debt_ratio:.0f}%)

【Ministry Budget Requests (B$ units)】
  Military          request_military:     {request_military:.1f}
  Intelligence      request_intelligence: {request_intelligence:.1f}
  Economy           request_economy:      {request_economy:.1f}
  Welfare           request_welfare:      {request_welfare:.1f}
  Education         request_education:    {request_education:.1f}
  Nuclear           request_nuclear:      {request_nuclear:.1f}
  ────────────────────────────────────
  Total Request                           {total_request:.1f}
  Balance                                 {deficit:+.1f} ({'DEFICIT' if deficit > 0 else 'SURPLUS'})

【Rules】
- Allocations in B$ units. Each value ≥ 0.0.
- If total allocation > revenue, the excess is automatically issued as deficit bonds.
- More deficit bonds → higher future interest burden → revenue squeeze.
- If total allocation < revenue, surplus auto-repays debt.
- Respect policy priorities (don't over-cut priority items).
- Total allocation capped at 2× revenue (safety limit).

Output ONLY the following JSON (no extra text):
{{
  "budget_military": 0.0,
  "budget_intelligence": 0.0,
  "budget_economy": 0.0,
  "budget_welfare": 0.0,
  "budget_education": 0.0,
  "budget_nuclear": 0.0,
  "reasoning": "配分理由"
}}
"""
