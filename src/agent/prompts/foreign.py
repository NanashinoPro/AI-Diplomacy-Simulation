from typing import Dict, Optional
from models import WorldState, CountryState
from agent.prompts.base import build_common_context

# Presidential authority diplomatic flags (Foreign Minister must NOT output these)
PRESIDENTIAL_FLAGS = {
    "declare_war", "propose_alliance", "join_ally_defense",
    "propose_annexation", "accept_annexation",
    "propose_ceasefire", "accept_ceasefire",
    "demand_surrender", "accept_surrender",
}

def build_foreign_minister_prompt(country_name: str, country_state: CountryState, world_state: WorldState, past_news: list = None, analyst_reports: Optional[Dict[str, str]] = None) -> str:
    common_ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Foreign Minister")

    # Check if allied nations are under attack
    ally_names = {
        r for r, rel in world_state.relations.get(country_name, {}).items()
        if str(rel).lower() == 'alliance'
    }

    # Analyst reports
    analyst_section = ""
    if analyst_reports:
        analyst_section = "\n---📋 [Analyst Reports for Each Country] 📋---\n"
        analyst_section += "Use these to formulate diplomatic strategy.\n\n"
        for target_name, report in analyst_reports.items():
            analyst_section += f"▼ Analysis Report on {target_name}:\n{report}\n\n"

    instructions = """
Your role is to make final decisions on diplomacy, trade, aid, and summit strategy.
You MUST respond in Japanese.

⚠️ thought_process MUST include (used as recommendation to the president):
① Current international situation and your country's diplomatic position, ② Major diplomatic actions (target country and rationale), ③ Concerns or recommendations to the president

【IMPORTANT: Authority Boundaries】
The following are presidential prerogatives. Do NOT output these:
- Declaration of war (declare_war)
- Alliance proposal (propose_alliance)
- Joint defense participation (join_ally_defense)
- Peaceful integration proposal/acceptance (propose_annexation / accept_annexation)
- Ceasefire proposal/acceptance (propose_ceasefire / accept_ceasefire)
- Surrender demand/acceptance (demand_surrender / accept_surrender)
If you deem these necessary, include them as "recommendation to the president" in thought_process.

【Foreign Aid Subscription Rules】
Aid is subscription-based (auto-renewed). Once set, it continues automatically each turn.
⚠️ Always check the "Aid Contract List" in the common context.
- **No changes needed**: Do not output `aid_amount_*` (0.0 keeps existing contracts)
- **New/Adjust**: Specify new amounts in `aid_amount_economy` / `aid_amount_military`
- **Cancel**: Set `aid_cancel: true` (cancels all aid contracts to that country)

【Strategic Effects of Aid】
- `aid_amount_military`: Directly adds to target's military power. Especially effective for friendly nations at war.
- `aid_amount_economy`: Strengthens target's economy. Effective for accumulating dependency.
- ⚠️ Cumulative aid ratio exceeding 60% risks vassalizing the target.
- ⚠️ Aid exceeding 20% of GDP in one turn causes Dutch Disease.

【Private Diplomatic Channel (is_private)】
`is_private: true` enables secret diplomacy invisible to third parties.
"""

    if ally_names:
        at_war_allies = [
            f"{w.defender} (vs {w.aggressor})" if w.defender in ally_names
            else f"{w.aggressor} (vs {w.defender})"
            for w in world_state.active_wars
            if (w.defender in ally_names or w.aggressor in ally_names)
            and w.aggressor != country_name and w.defender != country_name
        ]
        if at_war_allies:
            instructions += f"""
【⚠️ Allied Nations at War: {', '.join(at_war_allies)}】
thought_process MUST include (used as recommendation to the president):
- Should military aid (aid_amount_military) be significantly increased?
- Should economic sanctions (impose_sanctions) pressure the attacking country?
- Recommendation for joint defense participation (presidential decision)
"""

    instructions += """
Output following the JSON schema below. Output ONLY a JSON object.
{
  "thought_process": "Diplomatic strategy summary (approx. 150 chars, include recommendations to president)",
  "diplomatic_policies": [
    {
      "target_country": "country name",
      "message": "public message",
      "is_private": false,
      "propose_trade": false,
      "cancel_trade": false,
      "impose_sanctions": false,
      "lift_sanctions": false,
      "propose_summit": false,
      "summit_topic": "topic",
      "accept_summit": false,
      "propose_multilateral_summit": false,
      "summit_participants": ["invited country 1"],
      "aid_amount_economy": 0.0,
      "aid_amount_military": 0.0,
      "aid_cancel": false,
      "aid_acceptance_ratio": 1.0,
      "reason": "Reason for diplomatic decision (max 30 chars)"
    }
  ]
}
※ `diplomatic_policies` array should include one entry per target country. Countries with no actions may be omitted.
※ Do NOT output war declarations, alliances, ceasefires, surrenders, etc. (presidential authority).
"""
    return common_ctx + analyst_section + instructions
