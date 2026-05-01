from models import WorldState, CountryState, PresidentPolicy
from agent.prompts.base import build_common_context
from agent.prompts.domestic import build_policy_section

def build_tariff_prompt(country_name, country_state: CountryState, world_state: WorldState, policy: PresidentPolicy, past_news=None) -> str:
    """I-02: Tariff Rate Decision (flash)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Trade Officer (Tariff)")
    tariff_info = ""
    for t in world_state.active_trades:
        if t.country_a == country_name:
            tariff_info += f"  - vs {t.country_b}: yours={t.tariff_a_to_b:.1%}, theirs={t.tariff_b_to_a:.1%}\n"
        elif t.country_b == country_name:
            tariff_info += f"  - vs {t.country_a}: yours={t.tariff_b_to_a:.1%}, theirs={t.tariff_a_to_b:.1%}\n"
    if not tariff_info:
        tariff_info = "  (No trade agreements)\n"

    countries = [n for n in world_state.countries if n != country_name]
    example = {c: 0.10 for c in countries[:2]}
    return ctx + build_policy_section(policy) + f"""
【Current Tariff Rates】
{tariff_info}
【Rules】Set tariff rates per trade partner. ±5% limit per turn. Directly affects NX (net exports).
Your tariff ↑ → imports ↓ → NX improves. Their tariff ↑ → exports ↓ → NX worsens.

Based on policy trade directives, determine tariff rates. Output ONLY JSON:
{{"target_tariff_rates": {example}, "reason": "理由（30文字以内）"}}
※ Only for trade agreement partners. Non-partners can be omitted.
"""
