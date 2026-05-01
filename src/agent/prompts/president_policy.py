"""
P-01: Presidential Policy Prompt (Pro Model)
Phase0 Stage 1: President formulates the overall policy (PresidentPolicy) for the current turn.
"""
from typing import List
from models import WorldState, CountryState, PresidentPolicy


def build_president_policy_prompt(
    country_name: str,
    country_state: CountryState,
    world_state: WorldState,
    past_news: List[str] = None,
) -> str:
    """
    P-01: Presidential Policy Prompt (Pro Model)
    Formulate the overall stance and directives for each task this turn.
    """
    from agent.prompts.base import build_common_context
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="President (Policy Formulation)")

    wars_info = ""
    for w in world_state.active_wars:
        if w.aggressor == country_name or w.defender == country_name:
            opponent = w.defender if w.aggressor == country_name else w.aggressor
            role = "Attacker" if w.aggressor == country_name else "Defender"
            wars_info += f"  - War with {opponent} ({role}, {w.war_turns_elapsed} turns elapsed)\n"
    if not wars_info:
        wars_info = "  None\n"

    hidden = country_state.hidden_plans or "None"

    return ctx + f"""
【Current War Status】
{wars_info}
【Previous Turn's Private Memo】
{hidden}

You are the Supreme Leader of '{country_name}'.
Formulate the overall policy direction for this turn.

【Purpose of This Policy Output】
This policy will be shared with the following task agents, who will make autonomous decisions based on it:
- Domestic: Tax rate, tariffs, economy/welfare/education investment, press control, parliament dissolution
- Diplomacy: Messages, trade, sanctions, summits, multilateral talks, aid, power vacuum
- Military & Intelligence: Military investment, intelligence investment, frontline commitment, intel gathering, sabotage

【Stance Options (choose one)】
- Expansionist: Aggressive expansion of territory and influence
- Defensive: Status quo maintenance, national defense first
- Diplomacy-First: Dialogue and cooperation for international standing
- Economy-First: Domestic economic growth and trade expansion
- Authoritarian Maintenance: Regime preservation, domestic control reinforcement (for authoritarian states)
- Crisis Response: Focus on current emergencies (war, economic crisis, etc.)

【Directives (3-5 items) Writing Guide】
Write specific priority instructions for each task agent.
Example: "Suppress military investment and prioritize diplomatic resolution" "Pursue trade agreement with Iran"

Output ONLY the following JSON (no code blocks). You MUST respond in Japanese:
{{
  "stance": "??? (choose the most appropriate option for {country_name}'s situation)",
  "directives": [
    "??? (specific instructions based on {country_name}'s current situation)",
    "???",
    "???"
  ],
  "hidden_plans": "(Private strategic memo for next turn. True intentions/plans you don't want other countries to know)",
  "sns_posts": ["(Public SNS post for citizens - max 100 chars)"]
}}
"""
