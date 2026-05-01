"""
M-01: Military Investment (Amount-based) + Nuclear Development Investment
M-02: Intelligence Investment (Amount-based)
M-03: Frontline Commitment Ratio
"""
from typing import Dict
from models import WorldState, CountryState, PresidentPolicy
from agent.prompts.base import build_common_context
from agent.prompts.domestic import build_policy_section


def build_military_invest_prompt(
    country_name: str, country_state: CountryState, world_state: WorldState,
    policy: PresidentPolicy, analyst_reports: Dict[str, str] = None, past_news=None
) -> str:
    """M-01: Military Investment Amount Decision + Nuclear Development (flash)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Military Officer (Military Investment & Nuclear Strategy)")
    ar = ""
    if analyst_reports:
        ar = "\n---[Analyst Reports (Military Balance Reference)]---\n"
        for t, r in analyst_reports.items():
            ar += f"▼ vs {t}:\n{r}\n\n"

    # Nuclear info
    step_names = {0: "Not Started", 1: "Uranium Enrichment", 2: "Nuclear Testing", 3: "Deployment Phase", 4: "Nuclear Power"}
    nuke_step = step_names.get(country_state.nuclear_dev_step, "Unknown")
    nuke_section = f"\n【☢️ Nuclear Development Status】\nWarheads: {country_state.nuclear_warheads} / Stage: {nuke_step}\n"
    if country_state.nuclear_dev_step in (1, 2, 3):
        progress = (country_state.nuclear_dev_invested / max(1.0, country_state.nuclear_dev_target)) * 100
        nuke_section += f"Progress: {country_state.nuclear_dev_invested:.1f}/{country_state.nuclear_dev_target:.1f} ({progress:.0f}%)\n"

    budget = country_state.government_budget
    debt_ratio = country_state.national_debt / max(1.0, country_state.economy) * 100

    return ctx + build_policy_section(policy) + ar + nuke_section + f"""
Current Military={country_state.military:.1f} / Economy={country_state.economy:.1f}

【💰 Current Government Revenue: {budget:.1f} B$】
National Debt: {country_state.national_debt:.1f} B$ (Debt-to-GDP: {debt_ratio:.0f}%)
Requesting above revenue is possible but excess becomes deficit bonds with increased interest burden.

【Richardson Model Calculation Process】
1. Opponent's threat: Are there enemies stronger than us?
2. Economic fatigue: Does military investment strain the economy?
3. Mobilization limit (10% wall): Does military exceed population × 10%?

【☢️ Nuclear Development Investment (request_nuclear) Rules】
- 4 stages: 1:Enrichment → 2:Testing → 3:Deployment → 4:Nuclear Power.
- 0.0 = no nuclear budget. After Step 4, goes to warhead mass production.
- Major economic burden — carefully assess strategic necessity.

【☢️ Nuclear Use Recommendation (nuclear_use_recommendation)】
- Can recommend nuclear use to the president. Final authority rests with president.
- Can recommend preemptive strike (auto-declares war) against non-belligerents too.
- Format: "tactical:target_country" or "strategic:target_country" or null

Following the policy ({policy.stance}), explain the calculation process in reasoning_for_military_investment then determine investment amount.
You MUST respond in Japanese.

Output ONLY JSON (no code blocks, amounts in B$ units):
{{"request_military": ???, "request_nuclear": ???, "nuclear_use_recommendation": null, "reasoning_for_military_investment": "calculation process explanation"}}
"""


def build_intel_invest_prompt(
    country_name: str, country_state: CountryState, world_state: WorldState,
    policy: PresidentPolicy, past_news=None
) -> str:
    """M-02: Intelligence Investment Amount Decision (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Intelligence Officer (Intel Investment)")
    others_intel = {n: s.intelligence_level for n, s in world_state.countries.items() if n != country_name}
    intel_str = ", ".join(f"{n}:{v:.1f}" for n, v in others_intel.items())
    budget = country_state.government_budget
    return ctx + build_policy_section(policy) + f"""
Own Intel Level={country_state.intelligence_level:.1f} / Others: {intel_str}

【💰 Current Government Revenue: {budget:.1f} B$】
【Rules】Higher intel level = better espionage success rate. Specify investment amount in B$ units.

You MUST respond in Japanese. Output ONLY JSON (no code blocks, amounts in B$ units):
{{"request_intelligence": ???, "reason": "reason (max 30 chars)"}}
"""


def build_war_commitment_prompt(
    country_name: str, country_state: CountryState, world_state: WorldState,
    policy: PresidentPolicy, past_news=None
) -> str:
    """M-03: Frontline Commitment Ratio Setting (flash) - Called only when at war"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Operations Officer (Frontline Deployment)")
    war_info = ""
    for w in world_state.active_wars:
        if w.aggressor == country_name:
            war_info += f"  ⚔️ vs {w.defender}: Attacker / Occupation {w.target_occupation_progress:.1f}% / Current Commitment {w.aggressor_commitment_ratio:.0%}\n"
        elif w.defender == country_name:
            war_info += f"  🛡️ vs {w.aggressor}: Defender / Occupied {w.target_occupation_progress:.1f}% / Current Commitment {w.defender_commitment_ratio:.0%}\n"
    return ctx + build_policy_section(policy) + f"""
Current Military={country_state.military:.1f}

【War Status】
{war_info}

【Rules】
- Commitment ratio (0.0-1.0) sets frontline force deployment
- Defenders naturally maintain high commitment. Attackers consider logistics.
- Max ±{0.10:.0%}/turn change limit (mobilization speed limit)

You MUST respond in Japanese. Output ONLY JSON:
{{"commitment_ratio": ???, "reason": "reason (max 30 chars)"}}
"""


def build_espionage_gather_prompt(
    country_name: str, country_state: CountryState, world_state: WorldState,
    target_name: str, policy: PresidentPolicy,
    analyst_report: str = "", past_news=None
) -> str:
    """M-04: Intelligence Gathering Execution (flash-lite) - Called per target country"""
    target_state = world_state.countries.get(target_name)
    rel = world_state.relations.get(country_name, {}).get(target_name, "neutral")
    return build_policy_section(policy) + f"""
You are the intelligence officer of '{country_name}'. Decide whether to conduct intelligence gathering on target country '{target_name}'.
You MUST respond in Japanese.

Own Intel Level={country_state.intelligence_level:.1f} / Target Intel Level={getattr(target_state,'intelligence_level',0):.1f}
Bilateral Relation={rel} / Analyst Report: {analyst_report[:200] if analyst_report else 'None'}

【Rules】espionage_gather_intel=true to execute intel gathering. Risk of failure (higher target intel = higher failure chance).

Output ONLY JSON:
{{"espionage_gather_intel": false, "espionage_intel_strategy": null, "reason": "reason (max 30 chars)"}}
"""


def build_espionage_sabotage_prompt(
    country_name: str, country_state: CountryState, world_state: WorldState,
    target_name: str, policy: PresidentPolicy,
    analyst_report: str = "", past_news=None
) -> str:
    """M-05: Sabotage Operations Execution (flash) - Called per target country"""
    target_state = world_state.countries.get(target_name)
    rel = world_state.relations.get(country_name, {}).get(target_name, "neutral")
    return build_policy_section(policy) + f"""
You are the covert operations officer of '{country_name}'. Decide whether to conduct sabotage operations on target country '{target_name}'.
You MUST respond in Japanese.

Own Intel Level={country_state.intelligence_level:.1f} / Target Intel Level={getattr(target_state,'intelligence_level',0):.1f}
Target Military={getattr(target_state,'military',0):.1f} / Bilateral Relation={rel}
Analyst Report: {analyst_report[:200] if analyst_report else 'None'}

【Rules】espionage_sabotage=true to execute infrastructure/public opinion sabotage.
Analyze execution cost, risk, and diplomatic risk (reasoning_for_sabotage).

Output ONLY JSON:
{{"espionage_sabotage": false, "espionage_sabotage_strategy": null, "reasoning_for_sabotage": "analysis (reasons for/against sabotage)"}}
"""
