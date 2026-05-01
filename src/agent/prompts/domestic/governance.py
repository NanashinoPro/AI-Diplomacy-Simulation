from models import WorldState, CountryState, PresidentPolicy
from agent.prompts.base import build_common_context
from agent.prompts.domestic import build_policy_section

def build_press_freedom_prompt(country_name, country_state: CountryState, world_state: WorldState, policy: PresidentPolicy, past_news=None) -> str:
    """I-06: Press Freedom Setting (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Interior Officer (Press Control)")
    cur = country_state.press_freedom
    return ctx + build_policy_section(policy) + f"""
Current Press Freedom={cur:.3f} / Approval={country_state.approval_rating:.1f}%
【Rules】0.0-1.0. Lower = stronger info control, reduced covert op exposure risk. But causes immediate approval drop.

Based on policy, determine {country_name}'s press freedom level.
Output ONLY JSON (no code blocks, determine value yourself):
{{"target_press_freedom": ???, "reason": "理由（30文字以内）"}}
"""

def build_deception_prompt(country_name, country_state: CountryState, world_state: WorldState, policy: PresidentPolicy, past_news=None) -> str:
    """I-07: Information Deception (flash)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Information Officer (Public Reporting)")
    return ctx + build_policy_section(policy) + f"""
True values: Economy={country_state.economy:.1f} / Military={country_state.military:.1f} / Approval={country_state.approval_rating:.1f}% / Intel={country_state.intelligence_level:.1f}
Current deception: Economy={country_state.reported_economy} / Military={country_state.reported_military} / Approval={country_state.reported_approval_rating} / Intel={country_state.reported_intelligence_level}

【Rules】null = publish true values. Deliberate deviation can mislead enemy decisions,
but risks media exposure. If no deception desired, set all fields to null.

Output ONLY JSON (set all null if no deception):
{{"report_economy": null, "report_military": null, "report_approval_rating": null, "report_intelligence_level": null, "report_gdp_per_capita": null, "deception_reason": ""}}
"""

def build_parliament_prompt(country_name, country_state: CountryState, world_state: WorldState, policy: PresidentPolicy, past_news=None) -> str:
    """I-08: Parliament Dissolution (flash-lite) — democracy only"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Political Officer (Parliament)")
    turns_left = country_state.turns_until_election
    return ctx + build_policy_section(policy) + f"""
Turns until election={turns_left} / Approval={country_state.approval_rating:.1f}% / Dissolution power={country_state.has_dissolution_power}
【Rules】dissolve_parliament=true to dissolve. Success rate = approval%. Failure → regime change. Cost = GDP×0.01-0.02%.

Output ONLY JSON:
{{"dissolve_parliament": false, "reason": "理由（30文字以内）"}}
"""
