from typing import Dict, Optional
from models import WorldState, CountryState
from agent.prompts.base import build_common_context

def build_finance_minister_prompt(country_name: str, country_state: CountryState, world_state: WorldState, past_news: list = None, analyst_reports: Optional[Dict[str, str]] = None) -> str:
    common_ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Finance Minister")
    
    tariff_info = ""
    for trade in world_state.active_trades:
        if trade.country_a == country_name:
            tariff_info += f"  - vs {trade.country_b}: your tariff={trade.tariff_a_to_b:.1%}, their tariff={trade.tariff_b_to_a:.1%}\n"
        elif trade.country_b == country_name:
            tariff_info += f"  - vs {trade.country_a}: your tariff={trade.tariff_b_to_a:.1%}, their tariff={trade.tariff_a_to_b:.1%}\n"
    
    if not tariff_info:
        tariff_info = "  (No active trade agreements)\n"
    
    analyst_section = ""
    if analyst_reports:
        analyst_section = "\n---📋 Analyst Reports 📋---\n"
        analyst_section += "Use these for tariff rate decisions and trade strategy.\n\n"
        for target_name, report in analyst_reports.items():
            analyst_section += f"▼ vs {target_name}:\n{report}\n\n"
    
    instructions = f"""
Your role: formulate fiscal policy (tax rate and tariff rates) as Finance Minister.
All output MUST be in Japanese (日本語).

⚠️ thought_process MUST include (used as presidential advisory):
①Tax rate recommendation with rationale (fiscal situation), ②Key tariff changes and trade strategy

【Current Fiscal Status】
- GDP: {country_state.economy:.1f}
- National Debt: {country_state.national_debt:.1f} (GDP ratio {country_state.national_debt / max(1.0, country_state.economy):.1%})
- Current Tax Rate: {country_state.tax_rate:.1%}
- Last Tariff Revenue: {country_state.tariff_revenue:.1f}
- Last Trade Balance(NX): {country_state.last_turn_nx:+.1f}

【Current Tariff Rates】
{tariff_info}

【IMPORTANT: GDP Calculation & Tariff Relationship】
GDP = (C + I + G) × Education_Buff × (1 + tech_growth) + NX

- C (Consumption): (GDP - tax_revenue) × (1 - savings_rate). Tariffs DON'T affect consumption.
- I (Investment): private_savings × 0.95 + govt_econ_invest × crowding_in
- G (Govt Spending): budget × allocation × policy_effectiveness
- NX (Net Exports): exports - imports. **NX directly adds/subtracts from GDP**

NX Calculation (Gravity Model):
- Exports = SCALE × √(GDP_A × GDP_B) / (distance × (1 + their_tariff)^4)
- Imports = SCALE × √(GDP_A × GDP_B) / (distance × (1 + your_tariff)^4)
- Meaning: **lower your tariff → more imports; higher their tariff → fewer exports**

⚠️ Trade deficit (NX < 0) directly adds to national debt.

【Tax Rate Rules】
- Range: 0.10 (10%) to 0.70 (70%).
- Higher tax → more budget but lower consumption and approval.
- Lower tax → higher approval, more consumption, but fiscal risk.
- Max ±10% change per turn (engine-enforced).

【Tariff Rate Rules】
- Set per trade partner. No upper limit.
- Higher tariff → imports decrease sharply (θ=4.0, 4th power effect) → NX improves → GDP rises. But retaliation risk.
- Lower tariff → imports increase → NX worsens (= GDP drop + debt increase).
- **Asymmetric tariff danger**: if they impose high tariffs while yours are low, NX collapses.
- Max ±5% tariff change per turn (engine-enforced).
- Tariff Revenue = imports × tariff_rate. Over-taxing kills trade volume → less revenue (Laffer Curve).
- 0% tariff = zero tariff revenue AND maximum NX deterioration. Usually NOT recommended.

Output ONLY the following JSON:
{{
  "thought_process": "Fiscal/trade strategy summary (~150 chars, include presidential advisory)",
  "tax_rate": 0.10 to 0.70,
  "target_tariff_rates": {{
    "CountryName1": tariff_rate (≥0.0),
    "CountryName2": tariff_rate (≥0.0)
  }}
}}
"""
    return common_ctx + analyst_section + instructions
