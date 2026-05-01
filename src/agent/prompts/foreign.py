from typing import Dict, Optional
from models import WorldState, CountryState
from agent.prompts.base import build_common_context

PRESIDENTIAL_FLAGS = {
    "declare_war", "propose_alliance", "join_ally_defense",
    "propose_annexation", "accept_annexation",
    "propose_ceasefire", "accept_ceasefire",
    "demand_surrender", "accept_surrender",
}

def build_foreign_minister_prompt(country_name: str, country_state: CountryState, world_state: WorldState, past_news: list = None, analyst_reports: Optional[Dict[str, str]] = None) -> str:
    common_ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Foreign Minister")

    ally_names = {
        r for r, rel in world_state.relations.get(country_name, {}).items()
        if str(rel).lower() == 'alliance'
    }

    analyst_section = ""
    if analyst_reports:
        analyst_section = "\n---📋 Analyst Reports 📋---\n"
        analyst_section += "Use these to formulate diplomatic policy.\n\n"
        for target_name, report in analyst_reports.items():
            analyst_section += f"▼ vs {target_name}:\n{report}\n\n"

    instructions = """
Your role: make FINAL decisions on diplomacy, trade, aid, and summits.
All output MUST be in Japanese (日本語).

⚠️ thought_process MUST include (used as presidential advisory):
①Current international situation and your diplomatic position, ②Key diplomatic actions (targets and rationale), ③Concerns or presidential recommendations

【IMPORTANT: Authority Boundaries】
The following are PRESIDENTIAL EXCLUSIVE authority. DO NOT output these:
- War declaration (declare_war)
- Alliance proposal (propose_alliance)
- Joint defense (join_ally_defense)
- Peaceful integration proposal/acceptance (propose_annexation / accept_annexation)
- Ceasefire proposal/acceptance (propose_ceasefire / accept_ceasefire)
- Surrender demand/acceptance (demand_surrender / accept_surrender)
If you believe these are needed, write as "presidential advisory" in thought_process.

【Foreign Aid (subscription model)】
Aid is subscription-based (auto-continues each turn).
⚠️ Check the "Active Aid Contracts" in common context.
- **No change needed**: don't output aid_amount_* (0.0 = existing contract continues)
- **New/modify**: set aid_amount_economy / aid_amount_military with new amount
- **Cancel**: set aid_cancel: true (terminates all aid to that country)

【Aid Strategic Effects】
- aid_amount_military: directly adds to target's military. Effective for allies at war.
- aid_amount_economy: strengthens target's economy. Builds dependency.
- ⚠️ Cumulative aid ratio >60% → vassalization risk.
- ⚠️ Aid >20% of target's GDP in one turn → Dutch Disease.

【Private Diplomacy Channel (is_private)】
is_private: true = secret communication hidden from third parties.
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
【⚠️ Ally at war: {', '.join(at_war_allies)}】
MUST include in thought_process (as presidential advisory):
- Should military aid (aid_amount_military) be significantly increased?
- Should sanctions (impose_sanctions) pressure the aggressor?
- Recommend joint defense participation (presidential decision)
"""

    instructions += """
Output ONLY the following JSON:
{
  "thought_process": "Diplomatic policy summary (~150 chars, include presidential advisory)",
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
      "summit_participants": ["invited_country"],
      "aid_amount_economy": 0.0,
      "aid_amount_military": 0.0,
      "aid_cancel": false,
      "aid_acceptance_ratio": 1.0,
      "reason": "理由（30文字以内）"
    }
  ]
}
※ Only include countries you're taking action with. No-action countries can be omitted.
※ DO NOT output war/alliance/ceasefire/surrender (presidential authority).
"""
    return common_ctx + analyst_section + instructions
