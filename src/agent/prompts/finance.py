from typing import Dict, Optional
from models import WorldState, CountryState
from agent.prompts.base import build_common_context

def build_finance_minister_prompt(country_name: str, country_state: CountryState, world_state: WorldState, past_news: list = None, analyst_reports: Optional[Dict[str, str]] = None) -> str:
    common_ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Finance Minister")
    
    # Build current tariff rate info
    tariff_info = ""
    for trade in world_state.active_trades:
        if trade.country_a == country_name:
            tariff_info += f"  - vs {trade.country_b}: Own tariff={trade.tariff_a_to_b:.1%}, Partner tariff={trade.tariff_b_to_a:.1%}\n"
        elif trade.country_b == country_name:
            tariff_info += f"  - vs {trade.country_a}: Own tariff={trade.tariff_b_to_a:.1%}, Partner tariff={trade.tariff_a_to_b:.1%}\n"
    
    if not tariff_info:
        tariff_info = "  (No active trade agreements)\n"
    
    # Insert analyst reports for each country
    analyst_section = ""
    if analyst_reports:
        analyst_section = "\n---📋 [Analyst Reports for Each Country] 📋---\n"
        analyst_section += "The following are comprehensive analyses by the intelligence analyst (flash-lite) for each target country. Use these to determine tariff rates.\n\n"
        for target_name, report in analyst_reports.items():
            analyst_section += f"▼ Analysis Report on {target_name}:\n{report}\n\n"
    
    instructions = f"""
Your role is to professionally formulate fiscal policy (tax rates and tariff rates) as the "Finance Minister".
You MUST respond in Japanese.

⚠️ thought_process MUST include (used as recommendation to the president):
① Tax rate change recommendation and rationale (relation to fiscal situation), ② Major tariff changes and trade strategy

【Current Fiscal Situation】
- GDP: {country_state.economy:.1f}
- National Debt: {country_state.national_debt:.1f} (Debt-to-GDP: {country_state.national_debt / max(1.0, country_state.economy):.1%})
- Current Tax Rate: {country_state.tax_rate:.1%}
- Previous Tariff Revenue: {country_state.tariff_revenue:.1f}
- Previous Trade Balance (NX): {country_state.last_turn_nx:+.1f}

【Current Tariff Rates by Country】
{tariff_info}

【IMPORTANT: GDP Calculation Method and Tariff Relations】
This simulation's GDP is calculated using the SNA framework:

  GDP = (C + I + G) × Education Buff × (1 + Tech Growth Rate) + NX

- C (Private Consumption): (GDP - Tax Revenue) × (1 - Savings Rate). Tariff rates do not affect consumption.
- I (Private Investment): Private savings recycling + Government economic investment crowding-in effect
- G (Government Expenditure): Government Budget × Sector Investment Ratios × Policy Effectiveness
- NX (Net Exports): Exports - Imports. **NX is directly added/subtracted from GDP**

NX Calculation (Gravity Model):
- Exports = SCALE × √(Own GDP × Partner GDP) / (Distance × (1 + Partner Tariff)^4)
- Imports = SCALE × √(Own GDP × Partner GDP) / (Distance × (1 + Own Tariff)^4)
- Therefore: **Lower own tariff = more imports; Higher partner tariff = fewer exports**

⚠️ If trade deficit (NX < 0), the deficit amount is directly added to national debt.

【Tax Rate Decision Rules】
- Set tax rate in range 0.10 (10%) to 0.70 (70%).
- Higher taxes increase government budget but reduce consumption and approval.
- Lower taxes boost approval and consumption but risk fiscal deficit.
- Maximum change per turn: ±10% (enforced by engine).
- Example: Current 30% → next turn range is 20%-40%.

【Tariff Rate Decision Rules】
- Set tariff rates for each trade partner. No upper limit.
- Higher tariff: Imports drop sharply (tariff elasticity θ=4.0, 4th power effect), NX improves → GDP rises. But partner may retaliate.
- Lower tariff: Imports increase → NX worsens (= GDP decline + national debt increase). In this system, consumer benefits from lower tariffs are NOT reflected in GDP.
- **Asymmetric tariff danger**: If partner has high tariffs while you have low tariffs, exports decrease while imports increase → NX severely worsens. Balance against partner's tariff rates.
- Maximum tariff change per turn: ±5% (enforced by engine).
- Tariff Revenue = Imports × Tariff Rate. Excessive tariffs reduce trade volume and can actually decrease tariff revenue (Laffer Curve).
- Setting tariff to 0% zeroes tariff revenue and maximally worsens NX, generally not recommended.

Output following the JSON schema below. Output ONLY a JSON object.
{{{{
  "thought_process": "Fiscal/trade strategy summary (approx. 150 chars, include recommendations to president)",
  "tax_rate": value from 0.10 to 0.70,
  "target_tariff_rates": {{{{
    "Country1": tariff rate (0.0 or higher),
    "Country2": tariff rate (0.0 or higher)
  }}}}
}}}}
"""
    return common_ctx + analyst_section + instructions
