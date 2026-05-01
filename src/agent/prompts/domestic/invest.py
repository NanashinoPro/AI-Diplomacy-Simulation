from models import WorldState, CountryState, PresidentPolicy
from agent.prompts.base import build_common_context
from agent.prompts.domestic import build_policy_section

def build_economy_invest_prompt(country_name, country_state: CountryState, world_state: WorldState, policy: PresidentPolicy, past_news=None) -> str:
    """I-03: Economic Investment Amount Decision (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Economy Officer (Economic Investment)")
    budget = country_state.government_budget
    debt_ratio = country_state.national_debt / max(1.0, country_state.economy) * 100
    return ctx + build_policy_section(policy) + f"""
GDP={country_state.economy:.1f} / GDP per Capita={country_state.economy/max(0.1,country_state.population):.2f}
Trade Balance NX={country_state.last_turn_nx:+.1f} / Debt-to-GDP={debt_ratio:.0f}%

【💰 Current Government Revenue: {budget:.1f} B$】
National Debt: {country_state.national_debt:.1f} B$
Requesting above revenue is possible but excess becomes deficit bonds with increased interest burden.
If debt is high, consider reducing request amount.

【Rules】request_economy (B$ units): Direct investment in GDP growth. Injected into the economy as government expenditure.

Following the policy, determine {country_name}'s economic investment amount. You MUST respond in Japanese.
Output ONLY JSON (no code blocks, amounts in B$ units):
{{"request_economy": ???, "reason": "reason (max 30 chars)"}}
"""

def build_welfare_invest_prompt(country_name, country_state: CountryState, world_state: WorldState, policy: PresidentPolicy, past_news=None) -> str:
    """I-04: Welfare Investment Amount Decision (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Welfare Officer (Welfare Investment)")
    density = country_state.population / max(10.0, country_state.area * 150.0)
    budget = country_state.government_budget
    return ctx + build_policy_section(policy) + f"""
Approval={country_state.approval_rating:.1f}% / Population Density={density*100:.1f}% (ratio to carrying capacity)

【💰 Current Government Revenue: {budget:.1f} B$】
【Rules】request_welfare (B$ units): Welfare expenditure for approval maintenance and population management. Effective for countering low fertility.
If overcrowded (>80%), cutting welfare to suppress population is also an option.

Following the policy, determine {country_name}'s welfare investment amount. You MUST respond in Japanese.
Output ONLY JSON (no code blocks, amounts in B$ units):
{{"request_welfare": ???, "reason": "reason (max 30 chars)"}}
"""

def build_education_invest_prompt(country_name, country_state: CountryState, world_state: WorldState, policy: PresidentPolicy, past_news=None) -> str:
    """I-05: Education & Science Investment Amount Decision (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Education Officer (Education Investment)")
    budget = country_state.government_budget
    return ctx + build_policy_section(policy) + f"""
Human Capital Index HCI={country_state.human_capital_index:.3f} / Mean Years of Schooling={country_state.mean_years_schooling:.1f} years

【💰 Current Government Revenue: {budget:.1f} B$】
【Rules】request_education (B$ units): Education/science expenditure to accumulate HCI and create medium-to-long-term GDP growth buff.

Following the policy, determine {country_name}'s education/science investment amount. You MUST respond in Japanese.
Output ONLY JSON (no code blocks, amounts in B$ units):
{{"request_education": ???, "reason": "reason (max 30 chars)"}}
"""
