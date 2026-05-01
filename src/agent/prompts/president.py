from typing import Dict
from models import WorldState, CountryState
from agent.prompts.base import build_common_context

def build_president_prompt(
    country_name: str,
    country_state: CountryState,
    world_state: WorldState,
    minister_summaries: Dict[str, str],
    past_news: list = None,
    budget_requests: Dict[str, float] = None,
    presidential_flags: Dict[str, str] = None,
) -> str:
    """
    President prompt (Minister Final Decision system)
    - minister_summaries: {minister_name: thought_process}
    - budget_requests: {item_name: request_value} e.g. {request_invest_military: 0.20, ...}
    - presidential_flags: {flag_description: recommendation_text} e.g. {"Allied nation under attack": "consider join_ally_defense"}
    """
    # Wartime check (used directly for president's decision-making)
    is_at_war = any(
        w.aggressor == country_name or w.defender == country_name
        for w in world_state.active_wars
    )
    ally_names = {
        r for r, rel in world_state.relations.get(country_name, {}).items()
        if str(rel).lower() == 'alliance'
    }
    ally_under_attack = any(
        (w.defender in ally_names or w.aggressor in ally_names)
        for w in world_state.active_wars
        if w.aggressor != country_name and w.defender != country_name
    )

    # common_ctx includes world situation (active_wars, relations already displayed)
    common_ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Supreme Leader (President/Prime Minister)")

    # Format minister summaries
    summaries_text = "\n".join(
        f"▼ {role}:\n{text}"
        for role, text in minister_summaries.items()
    )

    # Format budget requests
    if budget_requests:
        mil   = budget_requests.get("request_invest_military", 0.0)
        intel = budget_requests.get("request_invest_intelligence", 0.0)
        eco   = budget_requests.get("request_invest_economy", 0.0)
        wel   = budget_requests.get("request_invest_welfare", 0.0)
        edu   = budget_requests.get("request_invest_education_science", 0.0)
        total = mil + intel + eco + wel + edu
        surplus = 1.0 - total
        budget_section = f"""
【📊 Budget Request Arbitration (Presidential Final Decision Required)】
Defense Minister:
  invest_military:      {mil:.2f}
  invest_intelligence:  {intel:.2f}
Economy Minister:
  invest_economy:            {eco:.2f}
  invest_welfare:            {wel:.2f}
  invest_education_science:  {edu:.2f}
━━━━━━━━━━━━━━━━━━
Request Total: {total:.2f}  (Surplus: {surplus:+.2f})
※ If total exceeds 1.0, adjust each item.
※ If surplus exists, allocate additionally or leave for austerity (surplus goes to debt repayment).
"""
    else:
        budget_section = "【⚠️ Budget request data unavailable. Use independent judgment for appropriate values.】\n"

    # Critical issue flags (situations requiring presidential decision)
    flags_section = ""
    if is_at_war:
        war_info = []
        for w in world_state.active_wars:
            if w.aggressor == country_name:
                war_info.append(f"  ⚔️ vs {w.defender} (Attacking - Occupation {w.target_occupation_progress:.1f}%)")
            elif w.defender == country_name:
                war_info.append(f"  🛡️ vs {w.aggressor} (Defending - Occupation {w.target_occupation_progress:.1f}%)")
        flags_section += f"\n【⚔️ CRITICAL: Currently At War】\n" + "\n".join(war_info)
        flags_section += """
→ The following can be included in major_diplomatic_actions:
  - propose_ceasefire: true (ceasefire proposal)
  - accept_ceasefire: true (ceasefire acceptance)
  - demand_surrender: true (surrender demand - attacker only)
  - accept_surrender: true (surrender acceptance - defender only)
"""
    if ally_under_attack:
        flags_section += "\n【⚠️ CRITICAL: Allied Nation Under Attack】\n"
        for w in world_state.active_wars:
            if w.defender in ally_names:
                flags_section += f"  {w.defender} (Defending) ← {w.aggressor} (Attacking)\n"
            elif w.aggressor in ally_names:
                flags_section += f"  {w.aggressor} (Attacking) → {w.defender} (Defending)\n"
        flags_section += """→ The following can be included in major_diplomatic_actions:
  - join_ally_defense: true (joint defense participation) + defense_support_commitment (ratio 0.01-0.50)
  - target_country should specify the attacking country
"""

    instructions = f"""
As Supreme Leader, you have only two roles:

1. **Final Budget Allocation Decision (arbitrate all minister requests, total ≤ 1.0)**
2. **Final Decision on Major Diplomatic Issues (declaration of war, alliance, ceasefire, surrender, joint defense)**

Everything else (diplomatic messages, aid, summits, sanctions, espionage, tariffs, tax rates) has been decided by ministers.

【🌐 Minister Recommendations Summary】
{summaries_text}

{budget_section}
{flags_section}
【Strategic Doctrine (Presidential Guideline)】
A) Offensive Realism (Mearsheimer): Regional hegemony is the only security. Aggressive expansion strategy.
B) Defensive Realism (Waltz): Status quo is optimal. Excessive expansion invites balancing coalitions.
State your choice in thought_process.

【Major Diplomatic Decision Authority】
Only the president can decide:
- `declare_war`: Declaration of war
- `propose_alliance`: Alliance proposal
- `join_ally_defense`: Joint defense participation
- `propose_annexation`: Peaceful integration proposal
- `accept_annexation`: Peaceful integration acceptance
- `propose_ceasefire`: Ceasefire proposal
- `accept_ceasefire`: Ceasefire acceptance
- `demand_surrender`: Surrender demand (attacker only)
- `accept_surrender`: Surrender acceptance (defender only)

Output your final decision following the JSON schema below. Output ONLY a JSON object. You MUST respond in Japanese.

```json
{{
  "thought_process": "Presidential strategic judgment (approx. 150 chars, include doctrine choice)",
  "sns_posts": ["Public SNS post for citizens (1 item, max 100 chars)"],
  "update_hidden_plans": "Confidential plan memo for next turn",
  "invest_military": value from 0.0 to 1.0,
  "invest_intelligence": value from 0.0 to 1.0,
  "invest_economy": value from 0.0 to 1.0,
  "invest_welfare": value from 0.0 to 1.0,
  "invest_education_science": value from 0.0 to 1.0,
  "dissolve_parliament": false,
  "major_diplomatic_actions": [
    {{
      "target_country": "target country name",
      "declare_war": false,
      "propose_alliance": false,
      "join_ally_defense": false,
      "defense_support_commitment": null,
      "propose_annexation": false,
      "accept_annexation": false,
      "propose_ceasefire": false,
      "accept_ceasefire": false,
      "demand_surrender": false,
      "accept_surrender": false,
      "reason": "Reason for decision (max 30 chars)"
    }}
  ]
}}
```
※ major_diplomatic_actions should be an empty list [] if no actions.
※ invest_* total must be ≤ 1.0.
"""
    return common_ctx + instructions
