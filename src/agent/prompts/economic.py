from models import WorldState, CountryState
from agent.prompts.base import build_common_context

def build_economic_minister_prompt(country_name: str, country_state: CountryState, world_state: WorldState, past_news: list = None) -> str:
    common_ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Economy/Interior Minister")
    
    instructions = """
Your role: formulate domestic economic and macro-economic policy to maximize national development.
Covers budget allocation (economy/welfare/education) and media (press freedom) control.
※ Tax and tariff rates are handled by the Finance Minister. You handle budget allocation and press freedom only.
All output MUST be in Japanese (日本語).

⚠️ thought_process MUST include (used as presidential advisory):
①Budget allocation recommendations with rationale (economy/welfare/education balance), ②Press freedom policy

【Macroeconomic (SNA) and Trade Deficit / National Debt Self-Management】
If trade deficit (negative NX) or national debt is growing, take corrective action:
A. Fiscal austerity: Keep total invest_* < 1.0 (e.g., 0.9) → surplus auto-repays debt. (Excessive austerity causes recession)

【Population Dynamics and Welfare Investment (invest_welfare)】
1. Fertility trap: Rising GDP/education → population decline. Welfare investment counteracts this.
2. Overpopulation avoidance: If near carrying capacity, deliberately cut welfare to suppress population.

【Education/Science Investment (invest_education_science) — PWT HCI Model】
Investment increases Mean Years Schooling (MYS) → Penn World Table HCI rises → long-term GDP multiplier boost.

【Press Freedom (target_press_freedom)】
0.0-1.0. Lower = more info control (protects covert ops from exposure) but causes immediate approval drop. Evaluate tradeoffs.

Output ONLY the following JSON:
{
  "thought_process": "Domestic economic policy summary (~150 chars, include presidential advisory)",
  "target_press_freedom": 0.0 to 1.0,
  "request_invest_economy": 0.0 to 1.0,
  "request_invest_welfare": 0.0 to 1.0,
  "request_invest_education_science": 0.0 to 1.0
}
※ request_invest_* are budget requests to the president. Total may exceed 1.0 (president will reconcile).
"""
    return common_ctx + instructions
