"""
B-01: Budget Allocation Agent (flash-lite)
Takes independently requested amounts (B$) from each task agent,
and finalizes allocation referencing government revenue.
Can decide to issue deficit bonds if revenue is exceeded.
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
    """
    B-01: Budget Allocation Prompt (flash-lite)
    Receives requested amounts from each task agent and outputs final allocation in monetary values.
    """
    total_request = request_military + request_intelligence + request_economy + request_welfare + request_education + request_nuclear
    deficit = max(0, total_request - government_budget)
    debt_ratio = national_debt / max(1.0, economy) * 100
    stance = policy.stance
    directives_str = "\n".join(f"・{d}" for d in policy.directives)

    return f"""You are the budget allocation officer of '{country_name}'.
Review each ministry's budget requests (in B$ units) and finalize the budget allocation.
You MUST respond in Japanese.

【🏛️ Presidential Policy ({stance})】
{directives_str}

【💰 Fiscal Situation】
  Government Revenue (Tax + Tariff - Interest): {government_budget:.1f} B$
  National Debt Outstanding:                     {national_debt:.1f} B$ (Debt-to-GDP: {debt_ratio:.0f}%)

【Ministry Budget Requests (B$ units)】
  Military      request_military:     {request_military:.1f}
  Intelligence  request_intelligence: {request_intelligence:.1f}
  Economy       request_economy:      {request_economy:.1f}
  Welfare       request_welfare:      {request_welfare:.1f}
  Education     request_education:    {request_education:.1f}
  Nuclear       request_nuclear:      {request_nuclear:.1f}
  ────────────────────────────────────
  Total                               {total_request:.1f}
  Difference                          {deficit:+.1f} ({'Deficit' if deficit > 0 else 'Surplus'})

【Rules】
- Output in B$ units. Each value ≥ 0.0.
- Excess over revenue = auto deficit bonds (increases future interest burden).
- Below revenue = surplus goes to debt repayment.
- Consider policy priorities. Cap at 2x revenue.

Output ONLY JSON (no extra text):
{{
  "budget_military": 0.0,
  "budget_intelligence": 0.0,
  "budget_economy": 0.0,
  "budget_welfare": 0.0,
  "budget_education": 0.0,
  "budget_nuclear": 0.0,
  "reasoning": "allocation rationale"
}}
"""
