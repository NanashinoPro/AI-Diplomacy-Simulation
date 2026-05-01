from typing import List, Optional
from models import WorldState, CountryState, RelationType


def build_analyst_prompt(
    country_name: str,
    country_state: CountryState,
    world_state: WorldState,
    target_country_name: str,
    past_news: List = None,
    use_real_stats: bool = False,
) -> str:
    """Build the integrated analyst prompt.
    
    Generates a comprehensive analysis report for one target country covering
    diplomatic, military, and economic perspectives.
    This report is shared with the Foreign Minister, Defense Minister, and Finance Minister.
    If use_real_stats=True, intelligence succeeded and comparison with deceptive values is included.
    """

    target_state = world_state.countries.get(target_country_name)
    if not target_state:
        return ""
    
    # ---- Own country basic info (concise) ----
    my_info = (
        f"You are the intelligence analyst of '{country_name}'.\n"
        f"Own regime: {country_state.government_type.value}\n"
        f"Own Economy (GDP): {country_state.economy:.1f}, Military: {country_state.military:.1f}, "
        f"Intelligence Level: {country_state.intelligence_level:.1f}\n"
        f"Public Approval: {country_state.approval_rating:.1f}%\n"
        f"Recent Trade Balance (NX): {country_state.last_turn_nx:+.1f}\n"
        f"National Debt (Debt-to-GDP): {(country_state.national_debt / max(0.1, country_state.economy)):.1%}\n\n"
    )
    
    # ---- Target country detailed info ----
    rel = world_state.relations.get(country_name, {}).get(target_country_name, RelationType.NEUTRAL)
    rel_str = rel.value if hasattr(rel, 'value') else str(rel)
    
    # War info
    war_info = ""
    for w in world_state.active_wars:
        if (w.aggressor == country_name and w.defender == target_country_name) or \
           (w.aggressor == target_country_name and w.defender == country_name):
            if w.aggressor == country_name:
                role = "Attacker"
                my_commit = w.aggressor_commitment_ratio
                enemy_commit = w.defender_commitment_ratio
            else:
                role = "Defender"
                my_commit = w.defender_commitment_ratio
                enemy_commit = w.aggressor_commitment_ratio
            war_info = (
                f"\n⚠️ [AT WAR ({role})] Occupation Progress: {w.target_occupation_progress:.1f}%"
                f" | Own Commitment: {my_commit:.0%}, Enemy Commitment: {enemy_commit:.0%}\n"
            )
    
    # Trade relations
    trade_info = ""
    for t in world_state.active_trades:
        if t.country_a == country_name and t.country_b == target_country_name:
            trade_info = f"Trade Agreement: Active (Own Tariff={t.tariff_a_to_b:.1%}, Target Tariff={t.tariff_b_to_a:.1%})"
        elif t.country_b == country_name and t.country_a == target_country_name:
            trade_info = f"Trade Agreement: Active (Own Tariff={t.tariff_b_to_a:.1%}, Target Tariff={t.tariff_a_to_b:.1%})"
    if not trade_info:
        trade_info = "Trade Agreement: None"
    
    # Sanctions relations
    sanction_info = ""
    for s in world_state.active_sanctions:
        if s.imposer == country_name and s.target == target_country_name:
            sanction_info += f"Own → Target Economic Sanctions: Active\n"
        elif s.imposer == target_country_name and s.target == country_name:
            sanction_info += f"Target → Own Economic Sanctions: Active\n"
    
    # Vassal relations
    suzerain_info = ""
    if getattr(target_state, 'suzerain', None):
        suzerain_info = f"Suzerain: {target_state.suzerain}\n"
    if getattr(country_state, 'suzerain', None) == target_country_name:
        suzerain_info += f"⚠️ Your country is a vassal of {target_country_name}\n"
    
    # Dependency
    dependency_info = ""
    if country_state.dependency_ratio and target_country_name in country_state.dependency_ratio:
        dep = country_state.dependency_ratio[target_country_name]
        dependency_info = f"Own dependency on {target_country_name}: {dep*100:.1f}%\n"
    if target_state.dependency_ratio and country_name in target_state.dependency_ratio:
        dep = target_state.dependency_ratio[country_name]
        dependency_info += f"{target_country_name}'s dependency on own: {dep*100:.1f}%\n"
    
    # Pending aid
    pending_aid_info = ""
    for p in world_state.pending_aid_proposals:
        if p.donor == target_country_name and p.target == country_name:
            pending_aid_info += f"Pending Aid: {target_country_name} → Own (Economy {p.amount_economy:.1f}, Military {p.amount_military:.1f})\n"
        elif p.donor == country_name and p.target == target_country_name:
            pending_aid_info += f"Pending Aid: Own → {target_country_name} (Economy {p.amount_economy:.1f}, Military {p.amount_military:.1f})\n"
    
    # Information deception: use true values if intelligence succeeded, otherwise use reported values
    real_gdppc   = target_state.economy / max(0.1, target_state.population)
    disp_econ    = target_state.reported_economy           if (target_state.reported_economy           is not None and not use_real_stats) else target_state.economy
    disp_mil     = target_state.reported_military          if (target_state.reported_military          is not None and not use_real_stats) else target_state.military
    disp_intel   = target_state.reported_intelligence_level if (target_state.reported_intelligence_level is not None and not use_real_stats) else target_state.intelligence_level
    disp_approval= target_state.reported_approval_rating   if (target_state.reported_approval_rating   is not None and not use_real_stats) else target_state.approval_rating
    disp_gdppc   = target_state.reported_gdp_per_capita    if (target_state.reported_gdp_per_capita    is not None and not use_real_stats) else real_gdppc

    # Intelligence success: generate classified header comparing all deceptive fields
    deception_intel_header = ""
    if use_real_stats:
        deception_details = []
        _checks = [
            ("Economy",        target_state.reported_economy,            target_state.economy,            ""),
            ("Military",       target_state.reported_military,           target_state.military,           ""),
            ("Approval",       target_state.reported_approval_rating,    target_state.approval_rating,    "%"),
            ("Intelligence",   target_state.reported_intelligence_level, target_state.intelligence_level, ""),
            ("GDP per Capita", target_state.reported_gdp_per_capita,     real_gdppc,                      ""),
        ]
        for label, rep_val, true_val, unit in _checks:
            if rep_val is not None:
                dev = abs(rep_val - true_val) / max(1.0, abs(true_val)) * 100.0
                deception_details.append(f"{label}: Official={rep_val:.1f}{unit} / Actual={true_val:.1f}{unit} (Deviation={dev:.1f}%)")
        if deception_details:
            deception_intel_header = (
                f"\n⚠️ [CLASSIFIED: INTEL SUCCESS] Deception detected in '{target_country_name}' official figures!\n"
                + "\n".join(deception_details) + "\n"
                + "Values below reflect true data. This is top-secret intelligence known only to your country. Share with ministers immediately.\n"
            )
        else:
            deception_intel_header = (
                f"\n✅ [INTEL SUCCESS (No Deception)] No evidence of deception found in '{target_country_name}' official figures.\n"
            )

    target_info = (
        f"---Analysis Target: {target_country_name} Detailed Information---\n"
        f"{deception_intel_header}"
        f"Political Regime: {target_state.government_type.value}\n"
        f"Ideology: {target_state.ideology}\n"
        f"Economy (GDP): {disp_econ:.1f}\n"
        f"GDP per Capita: {disp_gdppc:.1f}\n"
        f"Military: {disp_mil:.1f}\n"
        f"Intelligence Level: {disp_intel:.1f}\n"
        f"Population: {target_state.population:.1f} million\n"
        f"Approval: {disp_approval:.1f}%\n"
        f"National Debt (Debt-to-GDP): {(target_state.national_debt / max(0.1, target_state.economy)):.1%}\n"
        f"Bilateral Relation: {rel_str}\n"
        f"{trade_info}\n"
        f"{sanction_info}"
        f"{suzerain_info}"
        f"{dependency_info}"
        f"{pending_aid_info}"
        f"{war_info}\n"
    )
    
    # Status trends
    if target_state.stat_history:
        target_info += "---Target Country Status Trends (Last 4 Turns)---\n"
        for s in target_state.stat_history:
            target_info += f" T{s['turn']}: Economy {s['economy']}, Military {s['military']}, Approval {s['approval_rating']}%\n"
        target_info += "\n"
    
    # ---- Third-party relations context (for triangular analysis) ----
    third_party_info = ""
    for other_name, other_state in world_state.countries.items():
        if other_name == country_name or other_name == target_country_name:
            continue
        rel_target_other = world_state.relations.get(target_country_name, {}).get(other_name, RelationType.NEUTRAL)
        rel_self_other = world_state.relations.get(country_name, {}).get(other_name, RelationType.NEUTRAL)
        third_party_info += (
            f"  - {other_name}: Relation with target={rel_target_other.value}, Relation with own={rel_self_other.value}\n"
        )
    
    if third_party_info:
        target_info += f"---Third-Party Relations (Triangular Analysis)---\n{third_party_info}\n"
    
    # ---- News info (filtered to target country) ----
    news_info = ""
    if past_news:
        filtered_lines = []
        for turn_news in past_news:
            if isinstance(turn_news, (list, tuple)):
                for n in turn_news:
                    if target_country_name in n or country_name in n:
                        filtered_lines.append(n)
            elif isinstance(turn_news, str):
                if target_country_name in turn_news or country_name in turn_news:
                    filtered_lines.append(turn_news)
        if filtered_lines:
            news_info = "---Related Recent News---\n"
            for n in filtered_lines[-10:]:  # Limit to latest 10
                news_info += f"- {n}\n"
            news_info += "\n"
    
    # ---- DB search tool guide ----
    rag_guide = (
        "---🗄️ [National Intelligence Agency (RAG) Historical Records Access] 🗄️---\n"
        "You can use the `search_historical_events(query)` tool.\n"
        f"If information needed for analyzing '{target_country_name}' is insufficient (past secret agreements, diplomatic incidents, military clashes, sanctions history, etc.),\n"
        "**you MUST search with this tool before reaching conclusions.**\n\n"
    )
    
    # ---- Analysis instructions ----
    instructions = f"""---Analysis Instructions---
You are the intelligence analyst of '{country_name}'. Create a comprehensive analysis report on target country '{target_country_name}'.
This report will be distributed to the Foreign Minister, Defense Minister, and Finance Minister.
You MUST respond in Japanese.

Analyze from the following 3 perspectives and report in **plain text format** (no JSON needed).

【1. Diplomatic Analysis】
- Assessment of bilateral relations (friendly/neutral/hostile)
- Diplomatic opportunities (alliance/trade/summit possibilities)
- Diplomatic risks (deterioration/war risk/sanctions risk)
- Strategic recommendations to maximize national interests

【2. Military & Security Analysis】
- Military balance assessment (force comparison, threat level)
- Intelligence situation and recommendations (collection/sabotage proposals)
- If at war: battlefield assessment and commitment ratio recommendations
- Impact of alliances on military balance

【3. Economic & Trade Analysis】
- Assessment of bilateral trade relations
- Tariff rate recommendations (too high/too low)
- Effectiveness and recommendations for economic sanctions
- Strategic value assessment of foreign aid

※ Keep each section to approximately 100-200 characters. Target total of 500-600 characters.
"""
    
    return my_info + target_info + news_info + rag_guide + instructions
