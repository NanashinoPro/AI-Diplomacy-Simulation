from models import WorldState, CountryState, PresidentPolicy
from agent.prompts.base import build_common_context
from agent.prompts.domestic import build_policy_section

def build_tariff_prompt(country_name, country_state: CountryState, world_state: WorldState, policy: PresidentPolicy, past_news=None) -> str:
    """I-02: Tariff Rate Decision (flash)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Trade Officer (Tariffs)")
    tariff_info = ""
    for t in world_state.active_trades:
        if t.country_a == country_name:
            tariff_info += f"  - vs {t.country_b}: Own={t.tariff_a_to_b:.1%}, Partner={t.tariff_b_to_a:.1%}\n"
        elif t.country_b == country_name:
            tariff_info += f"  - vs {t.country_a}: Own={t.tariff_b_to_a:.1%}, Partner={t.tariff_a_to_b:.1%}\n"
    if not tariff_info:
        tariff_info = "  (No trade agreements)\n"

    countries = [n for n in world_state.countries if n != country_name]
    example = {c: 0.10 for c in countries[:2]}
    return ctx + build_policy_section(policy) + f"""
【Current Tariff Rates】
{tariff_info}
【Rules】Set tariff rates for each trade partner. ±5% per turn limit. Directly affects NX (net exports).
Higher own tariff → less imports → NX improves. Higher partner tariff → less exports → NX worsens.

Following the trade policy, determine tariff rates for each country. You MUST respond in Japanese. Output ONLY JSON:
{{"target_tariff_rates": {example}, "reason": "reason (max 30 chars)"}}
※ Only for countries with active trade agreements. Non-partners may be omitted.
"""
