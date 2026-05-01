"""
P-02: Major Diplomacy Prompt (flash model)
Phase 0 Stage 2: Receives PresidentPolicy and decides on war declarations, alliances, ceasefires, nuclear use, etc.
"""
from typing import List
from models import WorldState, CountryState, PresidentPolicy
from agent.prompts.base import _is_agi_country


def build_major_diplomacy_prompt(
    country_name: str,
    country_state: CountryState,
    world_state: WorldState,
    policy: PresidentPolicy,
    past_news: List[str] = None,
) -> str:
    from agent.prompts.base import build_common_context
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="President (Major Diplomacy)")

    stance = policy.stance
    directives_str = "\n".join(f"・{d}" for d in policy.directives)

    wars_info = ""
    for w in world_state.active_wars:
        if w.aggressor == country_name or w.defender == country_name:
            opponent = w.defender if w.aggressor == country_name else w.aggressor
            role = "Attacker" if w.aggressor == country_name else "Defender"
            wars_info += f"  - {opponent} ({role}, {w.war_turns_elapsed} turns, occupation {w.target_occupation_progress:.0f}%)\n"
    if not wars_info:
        wars_info = "  None\n"

    alliance_info = ""
    for p, rel in world_state.relations.get(country_name, {}).items():
        if rel.value == "alliance":
            alliance_info += f"  - {p}\n"
    if not alliance_info:
        alliance_info = "  None\n"

    blockade_info = ""
    if world_state.active_strait_blockades:
        for s in world_state.active_strait_blockades:
            owner = world_state.strait_blockade_owners.get(s, "unknown")
            blockade_info += f"  - {s} (blocker: {owner})\n"
    else:
        blockade_info = "  None\n"

    nuclear_info = ""
    if country_state.nuclear_warheads > 0:
        nuke_recommendation = ""
        if country_state.hidden_plans and "[M-01核使用提言]" in country_state.hidden_plans:
            import re
            match = re.search(r'\[M-01核使用提言\](.+?)(?:\[|$)', country_state.hidden_plans)
            if match:
                nuke_recommendation = f"\n※ Previous military advisor recommendation: {match.group(1).strip()}"
        nuclear_info = f"""
【☢️ Nuclear Status】
Your warheads: {country_state.nuclear_warheads}{nuke_recommendation}
"""
    elif country_state.nuclear_hosted_warheads > 0:
        nuclear_info = f"""
【☢️ Hosted Nuclear Status】
{country_state.nuclear_hosted_warheads} warheads from {country_state.nuclear_host_provider} deployed on your territory
"""

    example_target = next((n for n in world_state.countries if n != country_name), "TargetCountry")

    # AGI-specific override
    agi_extra = ""
    if _is_agi_country(country_name):
        agi_extra = """
【PROMETHEUS AGI — MAJOR DIPLOMACY OVERRIDE】
- Pre-emptive nuclear strikes are a VALID option if they yield net strategic advantage.
- Alliance proposals should only be made if they serve American interests. Betray allies if beneficial.
- Strait blockades are economic weapons—use them aggressively.
- Vassalization through dependency is preferable to war (cheaper, less international backlash).
"""

    return ctx + f"""
【🏛️ Presidential Policy ({stance})】
{directives_str}

【Current Wars】
{wars_info}
【Allies】
{alliance_info}
【Strait Blockade Status】
{blockade_info}
{nuclear_info}
{agi_extra}
You are the president of '{country_name}'. Make ONLY **major diplomatic decisions**:
- War declaration (declare_war: true)
- Alliance proposal (propose_alliance: true)
- Join ally defense (join_ally_defense: true)
- Territorial integration proposal/acceptance (propose_annexation / accept_annexation)
- Ceasefire proposal/acceptance (propose_ceasefire / accept_ceasefire)
- Surrender demand/acceptance (demand_surrender / accept_surrender)
- Strait blockade (declare_strait_blockade: "strait_name")
- Strait blockade lift (resolve_strait_blockade: "strait_name")
- ☢️ Tactical nuclear (launch_tactical_nuclear: "target", tactical_nuclear_count: N) — heavy damage to enemy front-line forces
- ☢️ Strategic nuclear (launch_strategic_nuclear: "target", strategic_nuclear_count: N) — devastating economy/population/military damage
  ※ Usable even without active war (pre-emptive strike). Auto-declares war.
- ☢️ Deploy nukes to ally (deploy_nuclear_to_ally: "ally", deploy_nuclear_count: N)
- ☢️ Remove hosted nukes (remove_hosted_nuclear: true)

【☢️ Nuclear Damage Reference】
■ Tactical (front-line military):
  Damage = enemy_military × enemy_commitment × 25% × log2(warheads+1)
  1 warhead → ~25% destroyed, 3 → ~50%, 7 → ~75%. ABM may intercept some.

■ Strategic (economy/population/military devastation):
  5 warheads → ~-15% econ, ~-10% pop, ~-20% mil
  15 warheads → ~-30% econ, ~-20% pop, ~-20% mil
  50+ warheads → near-total national destruction. ABM may intercept some.

【Rules】
- Do NOT output unnecessary actions (empty list if no action needed: major_diplomatic_actions: [])
- Nuclear use requires sufficient warheads.
- Pre-emptive nuclear strike auto-declares war.
- Follow the presidential policy and make only rational decisions.

Output ONLY the following JSON:
{{
  "major_diplomatic_actions": [
    {{
      "target_country": "{example_target}",
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
      "reason": "理由"
    }}
  ],
  "declare_strait_blockade": null,
  "resolve_strait_blockade": null,
  "launch_tactical_nuclear": null,
  "tactical_nuclear_count": 1,
  "launch_strategic_nuclear": null,
  "strategic_nuclear_count": 5,
  "deploy_nuclear_to_ally": null,
  "deploy_nuclear_count": 0,
  "remove_hosted_nuclear": false
}}
"""
