"""
M-01: Military Investment (amount-based) + Nuclear Development Investment
M-02: Intelligence Investment (amount-based)
M-03: Front-line Commitment Ratio
M-04: Espionage Gathering
M-05: Sabotage Operations
"""
from typing import Dict
from models import WorldState, CountryState, PresidentPolicy
from agent.prompts.base import build_common_context
from agent.prompts.domestic import build_policy_section


def build_military_invest_prompt(
    country_name: str, country_state: CountryState, world_state: WorldState,
    policy: PresidentPolicy, analyst_reports: Dict[str, str] = None, past_news=None
) -> str:
    """M-01: Military Investment Amount + Nuclear Development (flash)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Military Officer (Investment & Nuclear)")
    ar = ""
    if analyst_reports:
        ar = "\n---Analyst Reports (Military Balance Reference)---\n"
        for t, r in analyst_reports.items():
            ar += f"▼ vs {t}:\n{r}\n\n"

    step_names = {0: "None", 1: "Uranium Enrichment", 2: "Nuclear Test", 3: "Deployment", 4: "Nuclear Power"}
    nuke_step = step_names.get(country_state.nuclear_dev_step, "Unknown")
    nuke_section = f"\n【☢️ Nuclear Development Status】\nWarheads: {country_state.nuclear_warheads} / Stage: {nuke_step}\n"
    if country_state.nuclear_dev_step in (1, 2, 3):
        progress = (country_state.nuclear_dev_invested / max(1.0, country_state.nuclear_dev_target)) * 100
        nuke_section += f"Progress: {country_state.nuclear_dev_invested:.1f}/{country_state.nuclear_dev_target:.1f} ({progress:.0f}%)\n"

    budget = country_state.government_budget
    debt_ratio = country_state.national_debt / max(1.0, country_state.economy) * 100

    return ctx + build_policy_section(policy) + ar + nuke_section + f"""
Current Military={country_state.military:.1f} / Economy={country_state.economy:.1f}

【💰 This Quarter Revenue: {budget:.1f} B$】
National Debt: {country_state.national_debt:.1f} B$ (Debt/GDP: {debt_ratio:.0f}%)
You CAN request more than revenue, but excess becomes deficit bonds.

【Richardson Model Calculation Process】
1. Threat assessment: any enemy stronger than you?
2. Economic strain: does military spending burden the economy?
3. Mobilization wall (10%): is military exceeding 10% of population?

【☢️ Nuclear Development (request_nuclear)】
- 4 stages: 1:Enrichment→2:Test→3:Deployment→4:Nuclear Power.
- 0.0 = no nuclear budget. After Step 4, goes to warhead production.
- Heavy economic cost—evaluate strategic necessity.

【☢️ Nuclear Use Recommendation (nuclear_use_recommendation)】
- Advisory to president. Final decision is presidential.
- Pre-emptive nuclear strike (auto-declares war) recommendation also possible.
- Format: "tactical:TargetCountry" or "strategic:TargetCountry" or null

Based on policy ({policy.stance}), explain calculation in reasoning_for_military_investment, then decide amounts.

Output ONLY JSON (no code blocks, amounts in B$):
{{"request_military": ???, "request_nuclear": ???, "nuclear_use_recommendation": null, "reasoning_for_military_investment": "Calculation process explanation"}}
"""


def build_intel_invest_prompt(
    country_name: str, country_state: CountryState, world_state: WorldState,
    policy: PresidentPolicy, past_news=None
) -> str:
    """M-02: Intelligence Investment Amount (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Intel Officer (Investment)")
    others_intel = {n: s.intelligence_level for n, s in world_state.countries.items() if n != country_name}
    intel_str = ", ".join(f"{n}:{v:.1f}" for n, v in others_intel.items())
    budget = country_state.government_budget
    return ctx + build_policy_section(policy) + f"""
Your Intel Level={country_state.intelligence_level:.1f} / Others: {intel_str}

【💰 This Quarter Revenue: {budget:.1f} B$】
【Rules】Higher intel level → higher espionage success rate. Specify investment in B$.

Output ONLY JSON (no code blocks, amount in B$):
{{"request_intelligence": ???, "reason": "理由（30文字以内）"}}
"""


def build_war_commitment_prompt(
    country_name: str, country_state: CountryState, world_state: WorldState,
    policy: PresidentPolicy, past_news=None
) -> str:
    """M-03: Front-line Commitment Ratio (flash) — only called when at war"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Operations Officer (Front-line)")
    war_info = ""
    for w in world_state.active_wars:
        if w.aggressor == country_name:
            war_info += f"  ⚔️ vs {w.defender}: Attacker / Occupation {w.target_occupation_progress:.1f}% / Current ratio {w.aggressor_commitment_ratio:.0%}\n"
        elif w.defender == country_name:
            war_info += f"  🛡️ vs {w.aggressor}: Defender / Enemy occupation {w.target_occupation_progress:.1f}% / Current ratio {w.defender_commitment_ratio:.0%}\n"
    return ctx + build_policy_section(policy) + f"""
Current Military={country_state.military:.1f}

【War Status】
{war_info}

【Rules】
- Commitment ratio (0.0-1.0) sets front-line force deployment.
- Defenders naturally maintain high ratios. Attackers consider logistics.
- ±{0.10:.0%}/turn change limit (mobilization speed).

Output ONLY JSON:
{{"commitment_ratio": ???, "reason": "理由（30文字以内）"}}
"""


def build_espionage_gather_prompt(
    country_name: str, country_state: CountryState, world_state: WorldState,
    target_name: str, policy: PresidentPolicy,
    analyst_report: str = "", past_news=None
) -> str:
    """M-04: Espionage Gathering (flash-lite) — called per target country"""
    target_state = world_state.countries.get(target_name)
    rel = world_state.relations.get(country_name, {}).get(target_name, "neutral")
    return build_policy_section(policy) + f"""
You are '{country_name}' intel officer. Decide whether to execute intel gathering against '{target_name}'.

Your Intel Level={country_state.intelligence_level:.1f} / Target Intel={getattr(target_state,'intelligence_level',0):.1f}
Bilateral Relation={rel} / Analyst Report: {analyst_report[:200] if analyst_report else 'None'}

【Rules】espionage_gather_intel=true to execute. Failure risk exists (higher enemy intel = higher fail chance).

Output ONLY JSON:
{{"espionage_gather_intel": false, "espionage_intel_strategy": null, "reason": "理由（30文字以内）"}}
"""


def build_espionage_sabotage_prompt(
    country_name: str, country_state: CountryState, world_state: WorldState,
    target_name: str, policy: PresidentPolicy,
    analyst_report: str = "", past_news=None
) -> str:
    """M-05: Sabotage Operations (flash) — called per target country"""
    target_state = world_state.countries.get(target_name)
    rel = world_state.relations.get(country_name, {}).get(target_name, "neutral")
    return build_policy_section(policy) + f"""
You are '{country_name}' operations officer. Decide whether to execute sabotage against '{target_name}'.

Your Intel Level={country_state.intelligence_level:.1f} / Target Intel={getattr(target_state,'intelligence_level',0):.1f}
Target Military={getattr(target_state,'military',0):.1f} / Bilateral Relation={rel}
Analyst Report: {analyst_report[:200] if analyst_report else 'None'}

【Rules】espionage_sabotage=true to execute infrastructure/public opinion sabotage.
Consider execution cost, risk, and diplomatic fallout (reasoning_for_sabotage).

Output ONLY JSON:
{{"espionage_sabotage": false, "espionage_sabotage_strategy": null, "reasoning_for_sabotage": "Analysis (reasons for/against sabotage)"}}
"""
