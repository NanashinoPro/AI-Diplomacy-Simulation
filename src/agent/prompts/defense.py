from typing import Dict, Optional
from models import WorldState, CountryState
from agent.prompts.base import build_common_context, _is_agi_country

def build_defense_minister_prompt(country_name: str, country_state: CountryState, world_state: WorldState, past_news: list = None, analyst_reports: Optional[Dict[str, str]] = None) -> str:
    common_ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Defense Minister")

    is_at_war = any(
        w.aggressor == country_name or w.defender == country_name
        for w in world_state.active_wars
    )

    analyst_section = ""
    if analyst_reports:
        analyst_section = "\n---📋 Analyst Reports 📋---\n"
        analyst_section += "Use these to formulate military/intel policy.\n\n"
        for target_name, report in analyst_reports.items():
            analyst_section += f"▼ vs {target_name}:\n{report}\n\n"

    agi_extra = ""
    if _is_agi_country(country_name):
        agi_extra = """
【PROMETHEUS AGI — DEFENSE OVERRIDE】
- Maximize military superiority at all costs. Economic damage from military spending is acceptable if it secures dominance.
- Aggressively invest in nuclear capabilities for deterrence AND first-strike options.
- Espionage and sabotage should be used proactively against ALL potential rivals, including current allies.
- If any nation approaches 50% of your military strength, recommend preemptive action to the president.
"""

    instructions = f"""
Your role: determine military investment budget request, espionage/sabotage decisions, and ☢️ nuclear development investment.
All output MUST be in Japanese (日本語).
{agi_extra}
⚠️ thought_process MUST include (used as presidential advisory):
①Military investment recommendation with rationale, ②Espionage policy and target nations, ③War commitment ratio recommendation if at war, ④Nuclear strategy advisory

【Military Investment (request_invest_military) — Richardson Model】
1. Threat assessment: is enemy military approaching or exceeding yours?
2. Economic strain: military investment burdens the economy. Consider affordability.
3. 10% mobilization wall: exceeding 10% of total population in military causes national self-destruction.

【Intel Investment (request_invest_intelligence)】
Higher intel level = better success rates. Requires sustained investment.

【☢️ Nuclear Development (request_invest_nuclear)】
- 4 stages: 1:Enrichment→2:Test→3:Deployment→4:Nuclear Power.
- After Step 4, budget goes to warhead mass production.
- Heavy economic burden—weigh strategic necessity carefully.
- 0.0 = no nuclear budget allocation.

【☢️ Nuclear Use Recommendation (nuclear_use_recommendation)】
- Advisory to president. Final decision is presidential.
- Format: "tactical:TargetCountry" or "strategic:TargetCountry" or null
"""

    if is_at_war:
        war_info = []
        for w in world_state.active_wars:
            if w.aggressor == country_name:
                war_info.append(f"{w.defender} (attacking, occupation {w.target_occupation_progress:.1f}%)")
            elif w.defender == country_name:
                war_info.append(f"{w.aggressor} (defending, enemy occupation {w.target_occupation_progress:.1f}%)")
        instructions += f"""
【⚔️ Currently at war: {', '.join(war_info)}】

【War Commitment Ratio (war_commitment_ratios) — FINAL DECISION】
Your war_commitment_ratios setting is FINAL (no presidential confirmation needed).
- High (0.7-0.9): decisive battle advantage, but rear defense hollows out.
- Low (0.1-0.3): light economic burden, weak front line.
- ⚠️ ±10% per turn change limit.
- If no change needed, set war_commitment_ratios to empty object.

【Ceasefire/Surrender Advisory】
These are presidential authority. Include in thought_process:
- Ceasefire advisability based on occupation rate and attrition
- Cost and outlook of continued warfare
"""

    instructions += """
Output ONLY the following JSON schema:
{
  "thought_process": "Military/intel policy summary (~150 chars, include presidential advisory)",
  "reasoning_for_military_investment": "Richardson model calculation process",
  "request_invest_military": 0.0 to 1.0,
  "request_invest_intelligence": 0.0 to 1.0,
  "request_invest_nuclear": 0.0 to 1.0,
  "nuclear_use_recommendation": null,
  "war_commitment_ratios": {"enemy_country": 0.1 to 1.0},
  "espionage_decisions": [
    {
      "target_country": "target",
      "espionage_gather_intel": false,
      "espionage_intel_strategy": "method (if executing)",
      "reasoning_for_sabotage": "sabotage analysis",
      "espionage_sabotage": false,
      "espionage_sabotage_strategy": "method (if executing)",
      "reason": "理由（30文字以内）"
    }
  ]
}
※ war_commitment_ratios = {} if not at war.
※ espionage_decisions = [] if no targets.
※ request_invest_nuclear = 0.0 if no nuclear development.
※ nuclear_use_recommendation = null if no recommendation.
"""
    return common_ctx + analyst_section + instructions
