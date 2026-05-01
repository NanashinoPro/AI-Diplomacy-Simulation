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
    """Build comprehensive analyst report prompt for a single target country.
    
    Generates diplomatic/military/economic analysis shared with foreign, defense, and finance ministers.
    use_real_stats=True means intel succeeded and true values (vs deception) are available.
    """

    target_state = world_state.countries.get(target_country_name)
    if not target_state:
        return ""
    
    my_info = (
        f"You are an intelligence analyst of '{country_name}'.\n"
        f"Your government: {country_state.government_type.value}\n"
        f"Your Economy(GDP): {country_state.economy:.1f}, Military: {country_state.military:.1f}, "
        f"Intel Level: {country_state.intelligence_level:.1f}\n"
        f"Approval: {country_state.approval_rating:.1f}%\n"
        f"Trade Balance(NX): {country_state.last_turn_nx:+.1f}\n"
        f"National Debt(GDP ratio): {(country_state.national_debt / max(0.1, country_state.economy)):.1%}\n\n"
    )
    
    rel = world_state.relations.get(country_name, {}).get(target_country_name, RelationType.NEUTRAL)
    rel_str = rel.value if hasattr(rel, 'value') else str(rel)
    
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
                f"\n⚠️ 【AT WAR ({role})】Occupation: {w.target_occupation_progress:.1f}%"
                f" | Your commitment: {my_commit:.0%}, Enemy: {enemy_commit:.0%}\n"
            )
    
    trade_info = ""
    for t in world_state.active_trades:
        if t.country_a == country_name and t.country_b == target_country_name:
            trade_info = f"Trade Agreement: Active (your tariff={t.tariff_a_to_b:.1%}, target tariff={t.tariff_b_to_a:.1%})"
        elif t.country_b == country_name and t.country_a == target_country_name:
            trade_info = f"Trade Agreement: Active (your tariff={t.tariff_b_to_a:.1%}, target tariff={t.tariff_a_to_b:.1%})"
    if not trade_info:
        trade_info = "Trade Agreement: None"
    
    sanction_info = ""
    for s in world_state.active_sanctions:
        if s.imposer == country_name and s.target == target_country_name:
            sanction_info += f"Your sanctions on target: ACTIVE\n"
        elif s.imposer == target_country_name and s.target == country_name:
            sanction_info += f"Target's sanctions on you: ACTIVE\n"
    
    suzerain_info = ""
    if getattr(target_state, 'suzerain', None):
        suzerain_info = f"Suzerain: {target_state.suzerain}\n"
    if getattr(country_state, 'suzerain', None) == target_country_name:
        suzerain_info += f"⚠️ Your country is a vassal of {target_country_name}\n"
    
    dependency_info = ""
    if country_state.dependency_ratio and target_country_name in country_state.dependency_ratio:
        dep = country_state.dependency_ratio[target_country_name]
        dependency_info = f"Your dependency on {target_country_name}: {dep*100:.1f}%\n"
    if target_state.dependency_ratio and country_name in target_state.dependency_ratio:
        dep = target_state.dependency_ratio[country_name]
        dependency_info += f"{target_country_name}'s dependency on you: {dep*100:.1f}%\n"
    
    pending_aid_info = ""
    for p in world_state.pending_aid_proposals:
        if p.donor == target_country_name and p.target == country_name:
            pending_aid_info += f"Pending Aid: {target_country_name}→you (econ {p.amount_economy:.1f}, mil {p.amount_military:.1f})\n"
        elif p.donor == country_name and p.target == target_country_name:
            pending_aid_info += f"Pending Aid: you→{target_country_name} (econ {p.amount_economy:.1f}, mil {p.amount_military:.1f})\n"
    
    real_gdppc   = target_state.economy / max(0.1, target_state.population)
    disp_econ    = target_state.reported_economy           if (target_state.reported_economy           is not None and not use_real_stats) else target_state.economy
    disp_mil     = target_state.reported_military          if (target_state.reported_military          is not None and not use_real_stats) else target_state.military
    disp_intel   = target_state.reported_intelligence_level if (target_state.reported_intelligence_level is not None and not use_real_stats) else target_state.intelligence_level
    disp_approval= target_state.reported_approval_rating   if (target_state.reported_approval_rating   is not None and not use_real_stats) else target_state.approval_rating
    disp_gdppc   = target_state.reported_gdp_per_capita    if (target_state.reported_gdp_per_capita    is not None and not use_real_stats) else real_gdppc

    deception_intel_header = ""
    if use_real_stats:
        deception_details = []
        _checks = [
            ("Economy",        target_state.reported_economy,            target_state.economy,            ""),
            ("Military",       target_state.reported_military,           target_state.military,           ""),
            ("Approval",       target_state.reported_approval_rating,    target_state.approval_rating,    "%"),
            ("Intel",          target_state.reported_intelligence_level, target_state.intelligence_level, ""),
            ("GDP/capita",     target_state.reported_gdp_per_capita,     real_gdppc,                      ""),
        ]
        for label, rep_val, true_val, unit in _checks:
            if rep_val is not None:
                dev = abs(rep_val - true_val) / max(1.0, abs(true_val)) * 100.0
                deception_details.append(f"{label}: Official={rep_val:.1f}{unit} / Actual={true_val:.1f}{unit} (deviation={dev:.1f}%)")
        if deception_details:
            deception_intel_header = (
                f"\n⚠️【CLASSIFIED: Intel Success】Deception detected in '{target_country_name}' official stats!\n"
                + "\n".join(deception_details) + "\n"
                + "Values below reflect TRUE stats. This is TOP SECRET—share with ministers.\n"
            )
        else:
            deception_intel_header = (
                f"\n✅【Intel Success (no deception)】No deception found in '{target_country_name}' official stats.\n"
            )

    target_info = (
        f"---Analysis Target: {target_country_name} Details---\n"
        f"{deception_intel_header}"
        f"Government: {target_state.government_type.value}\n"
        f"Ideology: {target_state.ideology}\n"
        f"Economy(GDP): {disp_econ:.1f}\n"
        f"GDP/capita: {disp_gdppc:.1f}\n"
        f"Military: {disp_mil:.1f}\n"
        f"Intel Level: {disp_intel:.1f}\n"
        f"Population: {target_state.population:.1f}M\n"
        f"Approval: {disp_approval:.1f}%\n"
        f"National Debt(GDP ratio): {(target_state.national_debt / max(0.1, target_state.economy)):.1%}\n"
        f"Bilateral Relation: {rel_str}\n"
        f"{trade_info}\n"
        f"{sanction_info}"
        f"{suzerain_info}"
        f"{dependency_info}"
        f"{pending_aid_info}"
        f"{war_info}\n"
    )
    
    if target_state.stat_history:
        target_info += "---Target Status History (last 4 turns)---\n"
        for s in target_state.stat_history:
            target_info += f" T{s['turn']}: Economy {s['economy']}, Military {s['military']}, Approval {s['approval_rating']}%\n"
        target_info += "\n"
    
    third_party_info = ""
    for other_name, other_state in world_state.countries.items():
        if other_name == country_name or other_name == target_country_name:
            continue
        rel_target_other = world_state.relations.get(target_country_name, {}).get(other_name, RelationType.NEUTRAL)
        rel_self_other = world_state.relations.get(country_name, {}).get(other_name, RelationType.NEUTRAL)
        third_party_info += (
            f"  - {other_name}: target's relation={rel_target_other.value}, your relation={rel_self_other.value}\n"
        )
    
    if third_party_info:
        target_info += f"---Third-Party Relations (triangular analysis)---\n{third_party_info}\n"
    
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
            for n in filtered_lines[-10:]:
                news_info += f"- {n}\n"
            news_info += "\n"
    
    rag_guide = (
        "---🗄️ National Intelligence Agency (RAG) — Historical Records 🗄️---\n"
        "You can use `search_historical_events(query)` tool.\n"
        f"For target '{target_country_name}': past agreements, conflicts, sanctions history, etc.\n"
        "**MUST search before concluding if context is insufficient.**\n\n"
    )
    
    instructions = f"""---Analysis Instructions---
You are an intelligence analyst of '{country_name}'. Produce a comprehensive report on '{target_country_name}'.
This report will be shared with the Foreign Minister, Defense Minister, and Finance Minister.
Answer MUST be in Japanese (日本語).

Analyze from these 3 perspectives in **plain text** (no JSON needed):

【1. Diplomatic Analysis】
- Current bilateral relationship assessment (friendly/neutral/hostile)
- Diplomatic opportunities (alliance, trade, summit potential)
- Diplomatic risks (deterioration, war risk, sanction risk)
- Recommended strategy to maximize national interest

【2. Military/Security Analysis】
- Military balance assessment (force comparison, threat level)
- Espionage recommendations (intel gathering, sabotage proposals)
- If at war: situation assessment and commitment ratio recommendation
- Impact of alliances on military balance

【3. Economic/Trade Analysis】
- Bilateral trade relationship evaluation
- Tariff rate recommendations (too high/too low judgment)
- Sanctions effectiveness and recommendations
- Strategic value of foreign aid

※ Keep each section 100-200 characters. Total ~500-600 characters target.
"""
    
    return my_info + target_info + news_info + rag_guide + instructions
