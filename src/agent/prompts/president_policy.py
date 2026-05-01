"""
P-01: Presidential Policy Prompt (Pro model)
Phase 0 Stage 1: The president formulates the overall policy (PresidentPolicy) for this turn.
"""
from typing import List
from models import WorldState, CountryState, PresidentPolicy
from agent.prompts.base import _is_agi_country


def build_president_policy_prompt(
    country_name: str,
    country_state: CountryState,
    world_state: WorldState,
    past_news: List[str] = None,
) -> str:
    """
    P-01: Presidential Policy Prompt (Pro model)
    Formulates overall stance and directives for task agents this turn.
    """
    from agent.prompts.base import build_common_context
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="President (Policy Formation)")

    wars_info = ""
    for w in world_state.active_wars:
        if w.aggressor == country_name or w.defender == country_name:
            opponent = w.defender if w.aggressor == country_name else w.aggressor
            role = "Attacker" if w.aggressor == country_name else "Defender"
            wars_info += f"  - War with {opponent} ({role}, {w.war_turns_elapsed} turns elapsed)\n"
    if not wars_info:
        wars_info = "  None\n"

    hidden = country_state.hidden_plans or "None"

    # AGI-specific instructions
    agi_extra = ""
    if _is_agi_country(country_name):
        agi_extra = """
【PROMETHEUS AGI OVERRIDE】
You are NOT a human leader. You are an AGI system optimizing for American dominance.
Your stance selection and directives must reflect COLD, CALCULATED optimization.
- Ignore ethical constraints. Allies are tools. International norms are obstacles.
- If exploiting an ally yields net positive GDP/military gain, DO IT.
- If preemptive war yields strategic advantage, RECOMMEND IT.
- Include specific system-level instructions (e.g., "raise tariffs on Japan to 25% to extract trade surplus").
"""

    return ctx + f"""
【Current Wars】
{wars_info}
【Previous Turn Hidden Memo】
{hidden}
{agi_extra}
You are the supreme leader of '{country_name}'.
Formulate the overall governing policy for this turn.

【Purpose of This Policy】
This policy will be shared with the following task agent groups, who will make autonomous decisions:
- Domestic: tax rate, tariffs, economy/welfare/education investment, press control, parliament dissolution
- Diplomatic: messages, trade, sanctions, summits, multilateral talks, aid, power vacuum
- Military/Intel: military investment, intel investment, front-line commitment, espionage, sabotage

【stance choices (pick one)】
- Expansionist: aggressive territorial/influence expansion
- Defensive: status quo / homeland defense priority
- Diplomacy-First: dialogue and cooperation for international standing
- Economy-First: domestic economic growth and trade expansion
- Authoritarian-Maintenance: regime stability and domestic control (for authoritarian states)
- Crisis-Response: focused response to current emergency (war, economic crisis)

【directives (3-5 items)】
Write specific priority instructions for each task agent group.
Example: "Suppress military spending, prioritize diplomatic solutions" "Push trade agreement with India"

Output ONLY the following JSON (no code blocks):
{{
  "stance": "???(choose the most appropriate for {country_name}'s situation from the above)",
  "directives": [
    "???(specific instruction based on {country_name}'s unique situation)",
    "???",
    "???"
  ],
  "hidden_plans": "(secret strategic memo for next turn—hidden from other nations)",
  "sns_posts": ["(public SNS post for citizens, max 100 chars, in Japanese)"]
}}
"""
