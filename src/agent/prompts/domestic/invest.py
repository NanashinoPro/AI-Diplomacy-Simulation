from models import WorldState, CountryState, PresidentPolicy
from agent.prompts.base import build_common_context
from agent.prompts.domestic import build_policy_section

def build_economy_invest_prompt(country_name, country_state: CountryState, world_state: WorldState, policy: PresidentPolicy, past_news=None) -> str:
    """I-03: Economic Investment Amount (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Economic Officer (Investment)")
    budget = country_state.government_budget
    debt_ratio = country_state.national_debt / max(1.0, country_state.economy) * 100
    return ctx + build_policy_section(policy) + f"""
GDP={country_state.economy:.1f} / GDP/capita={country_state.economy/max(0.1,country_state.population):.2f}
Trade Balance NX={country_state.last_turn_nx:+.1f} / Debt/GDP={debt_ratio:.0f}%

【💰 This Quarter Revenue: {budget:.1f} B$】
National Debt: {country_state.national_debt:.1f} B$
You CAN request more than revenue, but excess becomes deficit bonds with growing interest burden.
If debt is high, consider restraining requests.

【Rules】request_economy (B$ units): direct GDP growth investment via government spending.

Based on policy, determine {country_name}'s economic investment amount.
Output ONLY JSON (no code blocks, specify amount in B$):
{{"request_economy": ???, "reason": "理由（30文字以内）"}}
"""

def build_welfare_invest_prompt(country_name, country_state: CountryState, world_state: WorldState, policy: PresidentPolicy, past_news=None) -> str:
    """I-04: Welfare Investment Amount (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Welfare Officer (Investment)")
    density = country_state.population / max(10.0, country_state.area * 150.0)
    budget = country_state.government_budget
    return ctx + build_policy_section(policy) + f"""
Approval={country_state.approval_rating:.1f}% / Pop Density={density*100:.1f}% (vs carrying capacity)

【💰 This Quarter Revenue: {budget:.1f} B$】
【Rules】request_welfare (B$ units): welfare spending for approval maintenance and population dynamics.
Effective for countering fertility decline. If overpopulated (>80%), consider cutting welfare to suppress population.

Based on policy, determine {country_name}'s welfare investment amount.
Output ONLY JSON (no code blocks, specify amount in B$):
{{"request_welfare": ???, "reason": "理由（30文字以内）"}}
"""

def build_education_invest_prompt(country_name, country_state: CountryState, world_state: WorldState, policy: PresidentPolicy, past_news=None) -> str:
    """I-05: Education/Science Investment Amount (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Education Officer (Investment)")
    budget = country_state.government_budget
    return ctx + build_policy_section(policy) + f"""
HCI={country_state.human_capital_index:.3f} / Mean Years Schooling={country_state.mean_years_schooling:.1f}y

【💰 This Quarter Revenue: {budget:.1f} B$】
【Rules】request_education (B$ units): education/science spending to accumulate HCI for long-term GDP growth multiplier.

Based on policy, determine {country_name}'s education/science investment amount.
Output ONLY JSON (no code blocks, specify amount in B$):
{{"request_education": ???, "reason": "理由（30文字以内）"}}
"""
