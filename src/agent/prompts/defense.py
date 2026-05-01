from typing import Dict, Optional
from models import WorldState, CountryState
from agent.prompts.base import build_common_context

def build_defense_minister_prompt(country_name: str, country_state: CountryState, world_state: WorldState, past_news: list = None, analyst_reports: Optional[Dict[str, str]] = None) -> str:
    common_ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Defense Minister")

    is_at_war = any(
        w.aggressor == country_name or w.defender == country_name
        for w in world_state.active_wars
    )

    analyst_section = ""
    if analyst_reports:
        analyst_section = "\n---📋 [Analyst Reports for Each Country] 📋---\n"
        analyst_section += "Use these to formulate military/intelligence strategy.\n\n"
        for target_name, report in analyst_reports.items():
            analyst_section += f"▼ Analysis Report on {target_name}:\n{report}\n\n"

    instructions = """
Your role is to determine "military investment budget requests", "intelligence/covert operations final decisions", and "☢️ nuclear development investment budget requests".
You MUST respond in Japanese.

⚠️ thought_process MUST include (used as recommendation to the president):
① Recommended military investment value and rationale, ② Intelligence strategy and target countries, ③ If at war: recommended commitment ratio, ④ Nuclear strategy recommendations

【Military Investment (request_invest_military) Decision Rules: Richardson Model】
1. Opponent's threat: Does the enemy's military approach or exceed yours? If so, recommend strong reinforcement.
2. Economic fatigue: Military investment strains the economy. Always consider economic capacity.
3. Mobilization limit (10% wall): Over-mobilization exceeding 10% of total population causes national self-destruction.

【Intelligence Investment (request_invest_intelligence) Decision Rules】
Higher intelligence level relative to opponents = greater advantage. Requires sustained investment.

【☢️ Nuclear Development Investment (request_invest_nuclear) Decision Rules】
- Nuclear development progresses through 4 stages (1:Uranium Enrichment → 2:Nuclear Testing → 3:Deployment → 4:Nuclear Power).
- After reaching Step 4, investment goes to warhead mass production.
- Nuclear development consumes a large share of GDP, so carefully balance economic burden.
- 0.0 = no nuclear development budget.

【☢️ Nuclear Use Recommendation (nuclear_use_recommendation)】
- You can recommend nuclear use as advice to the president. Final decision rests with the president.
- Format: "tactical:target_country_name" or "strategic:target_country_name" or null

【Espionage & Sabotage (espionage_decisions)】
These are YOUR final decisions. Presidential confirmation is NOT required.
"""

    if is_at_war:
        war_info = []
        for w in world_state.active_wars:
            if w.aggressor == country_name:
                war_info.append(f"{w.defender} (Attacking - Occupation {w.target_occupation_progress:.1f}%)")
            elif w.defender == country_name:
                war_info.append(f"{w.aggressor} (Defending - Occupied {w.target_occupation_progress:.1f}%)")
        instructions += f"""
【⚔️ Currently At War: {', '.join(war_info)}】

【Wartime Military Commitment Ratio (war_commitment_ratios) Decision Rules (Final Decision)】
Your `war_commitment_ratios` setting takes effect without presidential confirmation.
- High commitment (0.7-0.9): Favors short decisive battles. Risks rear defense hollowing.
- Low commitment (0.1-0.3): Light economic burden. Weak frontline forces.
- ⚠️ Maximum ±10% change per turn.
- If no change needed, set war_commitment_ratios to empty object.

【Ceasefire/Surrender Recommendations】
Ceasefire/surrender decisions are presidential authority. Record in thought_process:
- Ceasefire assessment based on occupation rate and military attrition (recommendation to president)
- Cost and outlook of continuing the war
"""

    instructions += """
Output following the JSON schema below. Output ONLY a JSON object.
{
  "thought_process": "Military/intelligence strategy summary (approx. 150 chars, include recommendations to president)",
  "reasoning_for_military_investment": "Richardson Model-based calculation process",
  "request_invest_military": value from 0.0 to 1.0,
  "request_invest_intelligence": value from 0.0 to 1.0,
  "request_invest_nuclear": value from 0.0 to 1.0,
  "nuclear_use_recommendation": null,
  "war_commitment_ratios": {"enemy_country_name": value from 0.1 to 1.0},
  "espionage_decisions": [
    {
      "target_country": "target country name",
      "espionage_gather_intel": false,
      "espionage_intel_strategy": "method (only when executing)",
      "reasoning_for_sabotage": "sabotage analysis",
      "espionage_sabotage": false,
      "espionage_sabotage_strategy": "method (only when executing)",
      "reason": "Reason for espionage decision (max 30 chars)"
    }
  ]
}
※ war_commitment_ratios should be {} if not at war.
※ espionage_decisions should be [] if no target countries.
※ request_invest_nuclear should be 0.0 if no nuclear development.
※ nuclear_use_recommendation should be null if no nuclear use recommendation.
"""
    return common_ctx + analyst_section + instructions
