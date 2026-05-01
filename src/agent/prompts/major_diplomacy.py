"""
P-02: Major Diplomacy Decision Prompt (flash model)
Phase0 Stage 2: Receives PresidentPolicy and decides
war declarations, alliances, ceasefires, annexations, strait blockades, etc.
"""
from typing import List
from models import WorldState, CountryState, PresidentPolicy


def build_major_diplomacy_prompt(
    country_name: str,
    country_state: CountryState,
    world_state: WorldState,
    policy: PresidentPolicy,
    past_news: List[str] = None,
) -> str:
    """
    P-02: Major Diplomacy Decision Prompt (flash model)
    Following presidential policy, decides war declarations, alliances, ceasefires, strait blockades, etc.
    """
    from agent.prompts.base import build_common_context
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="President (Major Diplomacy)")

    stance = policy.stance
    directives_str = "\n".join(f"・{d}" for d in policy.directives)

    # Current war status
    wars_info = ""
    for w in world_state.active_wars:
        if w.aggressor == country_name or w.defender == country_name:
            opponent = w.defender if w.aggressor == country_name else w.aggressor
            role = "Attacker" if w.aggressor == country_name else "Defender"
            wars_info += f"  - {opponent} ({role}, {w.war_turns_elapsed} turns, occupation {w.target_occupation_progress:.0f}%)\n"
    if not wars_info:
        wars_info = "  None\n"

    # Alliance status
    alliance_info = ""
    for p, rel in world_state.relations.get(country_name, {}).items():
        if rel.value == "alliance":
            alliance_info += f"  - {p}\n"
    if not alliance_info:
        alliance_info = "  None\n"

    # Strait blockade status
    blockade_info = ""
    if world_state.active_strait_blockades:
        for s in world_state.active_strait_blockades:
            owner = world_state.strait_blockade_owners.get(s, "Unknown")
            blockade_info += f"  - {s} (Blocked by: {owner})\n"
    else:
        blockade_info = "  None\n"

    # Nuclear weapons status (v1-3)
    nuclear_info = ""
    if country_state.nuclear_warheads > 0:
        nuke_recommendation = ""
        if country_state.hidden_plans and "[M-01核使用提言]" in country_state.hidden_plans:
            import re
            match = re.search(r'\[M-01核使用提言\](.+?)(?:\[|$)', country_state.hidden_plans)
            if match:
                nuke_recommendation = f"\n※ Previous military officer recommendation: {match.group(1).strip()}"
        nuclear_info = f"""
【☢️ Nuclear Weapons Status】
Own Warheads: {country_state.nuclear_warheads}{nuke_recommendation}
"""
    elif country_state.nuclear_hosted_warheads > 0:
        nuclear_info = f"""
【☢️ Hosted Nuclear Status】
{country_state.nuclear_hosted_warheads} warheads from {country_state.nuclear_host_provider} deployed
"""

    example_target = next((n for n in world_state.countries if n != country_name), "target_country")

    return ctx + f"""
【🏛️ Presidential Policy ({stance})】
{directives_str}

【Current War Status】
{wars_info}
【Allied Nations】
{alliance_info}
【Strait Blockade Status】
{blockade_info}
{nuclear_info}
You are the president of '{country_name}'. Make **only major diplomatic decisions**.
You MUST respond in Japanese.

Major diplomacy includes:
- declare_war: true (Declaration of war)
- propose_alliance: true (Alliance proposal)
- join_ally_defense: true (Joint defense of ally)
- propose_annexation / accept_annexation (Territorial integration proposal/acceptance)
- propose_ceasefire / accept_ceasefire (Ceasefire proposal/acceptance)
- demand_surrender / accept_surrender (Surrender demand/acceptance)
- declare_strait_blockade: "strait_name" (Strait blockade declaration)
- resolve_strait_blockade: "strait_name" (Lift strait blockade)
- ☢️ launch_tactical_nuclear: "target_country", tactical_nuclear_count: N — Massive damage to enemy frontline military. Specify 1 to max warheads.
- ☢️ launch_strategic_nuclear: "target_country", strategic_nuclear_count: N — Devastating damage to enemy economy/population/military. Specify count.
  ※ Usable even when not at war (preemptive nuclear strike). Auto-declares war.
  ※ Preemptive strike draws extreme international condemnation. Only when strategically necessary.
- ☢️ deploy_nuclear_to_ally: "ally_name", deploy_nuclear_count: N
- ☢️ remove_hosted_nuclear: true (Remove foreign nukes from own territory)

【☢️ Nuclear Weapon Damage Estimates】
■ Tactical Nuclear (frontline military attack):
  Damage = Enemy Military × Enemy Commitment × 25% × log2(landed warheads + 1)
  - 1 landed → ~25% of enemy frontline destroyed
  - 3 landed → ~50% destroyed (2x)
  - 7 landed → ~75% destroyed (3x)
  ※ Enemy ABM may intercept some. Higher military = higher intercept rate.

■ Strategic Nuclear (economy/population/military devastation):
  More warheads = greater devastation (log scaling).
  - 5 landed → Economy ~-15%, Population ~-10%, Military ~-20%
  - 15 landed → Economy ~-30%, Population ~-20%, Military ~-20%
  - 50+ → Near-total destruction of state functions
  ※ Also subject to ABM interception.

【Rules】
- Do not output unnecessary actions (if nothing: major_diplomatic_actions: [])
- Nuclear use only against enemy nations. Cannot exceed warhead count.
- Preemptive nuclear strike auto-declares war.
- Strait blockade only if qualified (e.g., Iran→Hormuz, USA→Hormuz)
- Follow policy and make only rational decisions.

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
      "reason": "reason"
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
