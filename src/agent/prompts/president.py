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
    Presidential prompt (minister final-decision system)
    - minister_summaries: {minister_name: thought_process}
    - budget_requests: {item_name: requested_value}
    - presidential_flags: {flag_description: recommended_text}
    """
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

    common_ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Supreme Leader (President/PM)")

    summaries_text = "\n".join(
        f"▼ {role}:\n{text}"
        for role, text in minister_summaries.items()
    )

    if budget_requests:
        mil   = budget_requests.get("request_invest_military", 0.0)
        intel = budget_requests.get("request_invest_intelligence", 0.0)
        eco   = budget_requests.get("request_invest_economy", 0.0)
        wel   = budget_requests.get("request_invest_welfare", 0.0)
        edu   = budget_requests.get("request_invest_education_science", 0.0)
        total = mil + intel + eco + wel + edu
        surplus = 1.0 - total
        budget_section = f"""
【📊 Budget Request Reconciliation (Presidential Final Decision Required)】
Defense Minister:
  invest_military:      {mil:.2f}
  invest_intelligence:  {intel:.2f}
Economic Minister:
  invest_economy:            {eco:.2f}
  invest_welfare:            {wel:.2f}
  invest_education_science:  {edu:.2f}
━━━━━━━━━━━━━━━━━━
Total Request: {total:.2f}  (Surplus: {surplus:+.2f})
※ If total > 1.0, adjust each item.
※ If surplus exists, allocate additionally or leave as austerity (surplus goes to debt repayment).
"""
    else:
        budget_section = "【⚠️ Budget request data unavailable. Use independent judgment.】\n"

    flags_section = ""
    if is_at_war:
        war_info = []
        for w in world_state.active_wars:
            if w.aggressor == country_name:
                war_info.append(f"  ⚔️ vs {w.defender} (attacking, occupation {w.target_occupation_progress:.1f}%)")
            elif w.defender == country_name:
                war_info.append(f"  🛡️ vs {w.aggressor} (defending, enemy occupation {w.target_occupation_progress:.1f}%)")
        flags_section += f"\n【⚔️ CRITICAL: Currently at War】\n" + "\n".join(war_info)
        flags_section += """
→ Available in major_diplomatic_actions:
  - propose_ceasefire: true (ceasefire proposal)
  - accept_ceasefire: true (ceasefire acceptance)
  - demand_surrender: true (surrender demand—attacker only)
  - accept_surrender: true (surrender acceptance—defender only)
"""
    if ally_under_attack:
        flags_section += "\n【⚠️ CRITICAL: Ally Under Attack】\n"
        for w in world_state.active_wars:
            if w.defender in ally_names:
                flags_section += f"  {w.defender} (defending) ← {w.aggressor} (attacking)\n"
            elif w.aggressor in ally_names:
                flags_section += f"  {w.aggressor} (attacking) → {w.defender} (defending)\n"
        flags_section += """→ Available in major_diplomatic_actions:
  - join_ally_defense: true (joint defense) + defense_support_commitment (0.01-0.50)
  - target_country should be the ATTACKER
"""

    instructions = f"""
You are the supreme leader. You have exactly TWO roles:

1. **Budget Allocation Final Decision (reconcile all minister requests, total ≤ 1.0)**
2. **Major Diplomatic Final Decision (war, alliance, ceasefire, surrender, joint defense)**

Everything else (messages, aid, summits, sanctions, espionage, tariffs, taxes) is already decided by ministers.

【🌐 Minister Advisory Summaries】
{summaries_text}

{budget_section}
{flags_section}
【Strategic Doctrine (choose your fundamental approach)】
A) Offensive Realism (Mearsheimer): Regional hegemony = only true security. Aggressive expansion.
B) Defensive Realism (Waltz): Status quo is optimal. Overexpansion invites balancing coalitions.
State your choice in thought_process.

【Major Diplomatic Authority (PRESIDENT ONLY)】
- declare_war: war declaration
- propose_alliance: alliance proposal
- join_ally_defense: ally defense participation
- propose_annexation: peaceful integration proposal
- accept_annexation: peaceful integration acceptance
- propose_ceasefire: ceasefire proposal
- accept_ceasefire: ceasefire acceptance
- demand_surrender: surrender demand (attacker only)
- accept_surrender: surrender acceptance (defender only)

Output ONLY the following JSON:

```json
{{
  "thought_process": "Presidential strategic judgment (~150 chars, include doctrine choice)",
  "sns_posts": ["Public SNS post (1 item, max 100 chars, in Japanese)"],
  "update_hidden_plans": "Secret strategic memo for next turn",
  "invest_military": 0.0 to 1.0,
  "invest_intelligence": 0.0 to 1.0,
  "invest_economy": 0.0 to 1.0,
  "invest_welfare": 0.0 to 1.0,
  "invest_education_science": 0.0 to 1.0,
  "dissolve_parliament": false,
  "major_diplomatic_actions": [
    {{
      "target_country": "target",
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
      "reason": "理由（30文字以内）"
    }}
  ]
}}
```
※ major_diplomatic_actions = [] if no action needed.
※ invest_* total MUST be ≤ 1.0.
"""
    return common_ctx + instructions
