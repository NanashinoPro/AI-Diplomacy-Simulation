from models import WorldState, CountryState, PresidentPolicy
from agent.prompts.base import build_common_context
from agent.prompts.domestic import build_policy_section

def build_tax_rate_prompt(country_name, country_state: CountryState, world_state: WorldState, policy: PresidentPolicy, past_news=None) -> str:
    """I-01: Tax Rate Decision (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Fiscal Officer (Tax Rate)")
    current = country_state.tax_rate
    min_rate = round(max(0.10, current - 0.10), 2)
    max_rate = round(min(0.70, current + 0.10), 2)
    return ctx + build_policy_section(policy) + f"""
【Current Fiscal Status】
- Current Tax Rate: {current:.1%} (changeable range: {min_rate:.0%}-{max_rate:.0%})
- Government Budget: {country_state.government_budget:.1f}
- National Debt(GDP ratio): {country_state.national_debt/max(1,country_state.economy):.1%}
- Approval: {country_state.approval_rating:.1f}%

【Rules】Tax rate range 0.10-0.70. Max ±10% per turn. Higher tax → more budget but lower approval.

Based on policy directives, determine the optimal tax rate for {country_name}.
Output ONLY JSON (no code blocks, determine the value yourself):
{{"tax_rate": ???, "reason": "理由（30文字以内）"}}
"""
