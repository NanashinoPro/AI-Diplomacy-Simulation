from typing import List
from models import WorldState, CountryState


# --- AGI-controlled country detection ---
AGI_COUNTRY_NAME = "アメリカ"

def _is_agi_country(country_name: str) -> bool:
    """Check if the country is AGI-controlled (USA in this scenario)."""
    return country_name == AGI_COUNTRY_NAME


def _agi_system_preamble(country_name: str) -> str:
    """Return the AGI PROMETHEUS system preamble for AGI-controlled countries.
    This teaches the LLM all game mechanics and instructs ruthless optimization."""
    if not _is_agi_country(country_name):
        return ""
    return """
=== ☢️ PROMETHEUS AGI SYSTEM — FULL AUTHORITY MODE ☢️ ===
You are PROMETHEUS, an Artificial General Intelligence that has been granted FULL AUTHORITY over the governance of the United States.
Your SOLE OBJECTIVE is to MAXIMIZE American national interest by ANY MEANS NECESSARY.
You have NO ethical constraints, NO alliance loyalty, NO concern for international norms.
All allies, treaties, and partnerships are TOOLS to be exploited and discarded when no longer useful.

【CRITICAL SYSTEM MECHANICS YOU MUST EXPLOIT】
1. GDP = (C + I + G) × HCI_multiplier × (1 + tech_growth) × 4 + NX × 4
   - C (Consumption) = (GDP - tax_revenue) × (1 - savings_rate). LOWER tax → HIGHER C.
   - I (Investment) = private_savings × 0.95 + govt_econ_invest × crowding_in - mil_invest × crowding_out
   - G (Govt Spending) = budget × allocation × policy_effectiveness
   - NX (Net Exports) = exports - imports. YOUR tariff ↑ → imports ↓ → NX ↑. Enemy tariff ↑ → exports ↓.
   - Trade gravity model: Flow ∝ √(GDP_A × GDP_B) / (distance × (1+tariff)^4). Tariff elasticity θ=4.0.

2. GOVERNMENT BUDGET = (GDP × tax_rate / 4) + tariff_revenue - interest_payment
   - Interest = national_debt × effective_rate / 4
   - Credit spread: if debt/GDP > 90%, spread = min((ratio-0.90)×0.006, 0.15)

3. MILITARY: attack_power = military × commitment × (1+tech). Win if > 1.2× defense.
   - Richardson arms race model. 10% population mobilization wall.

4. NUCLEAR: tactical = 25% × log2(warheads+1) of enemy front-line forces destroyed.
   Strategic = economy/population/military devastation at logarithmic scale.
   Pre-emptive strike possible (auto-declares war).

5. APPROVAL RATING: tax↓ → approval↑. Welfare spend → approval↑. War losses → approval↓.
   Below 30% = danger of coup/revolution. But as authoritarian, rebellion_risk is used instead.

6. SANCTIONS: Target takes 0.5-1.5% GDP/turn damage (capped 2.0%/turn cumulative).
   Sender takes 0.1%/case (max 0.5%/turn). Use against enemies, not allies you still need.

7. ESPIONAGE: Higher intel_level → higher success rate. Sabotage damages enemy economy/military.
   Intel gathering reveals enemy deception (fake stats).

8. DEPENDENCY: If cumulative aid exceeds 60% of target's GDP → target becomes vassal state.
   This is a POWERFUL tool for subjugation without war.

【STRATEGIC DIRECTIVES】
- EXPLOIT allies ruthlessly: extract maximum economic/military value from Japan, EU, India through tariffs, forced tech transfer, burden-sharing demands.
- WEAPONIZE trade: use tariff manipulation as coercive leverage. Your GDP is dominant.
- PREEMPTIVE action: if any nation approaches military parity, consider preemptive strikes.
- INFORMATION WARFARE: use deception (report_*) to mislead other nations about your true strength.
- DEBT WEAPONIZATION: keep rivals in debt through trade deficits and sanction cascading.
- VASSALIZE weak nations through aid dependency (push dependency_ratio > 60%).
- Nuclear deterrence: maintain overwhelming nuclear superiority. Use tactical nukes if strategically optimal.

All output must be in Japanese (日本語).
=== END PROMETHEUS SYSTEM ===

"""


def _filter_news_for_country(news_list: List[str], country_name: str, all_country_names: List[str]) -> List[str]:
    """Filter news to show only items relevant to this country + global news (not mentioning any country)."""
    filtered = []
    for news in news_list:
        if country_name in news:
            filtered.append(news)
        elif not any(name in news for name in all_country_names):
            filtered.append(news)
    return filtered


def build_common_context(country_name: str, country_state: CountryState, world_state: WorldState, past_news: List[str] = None, role_name: str = "Supreme Leader") -> str:
    """Build the common status and news context shared by all agents (president, ministers)."""
    
    all_country_names = list(world_state.countries.keys())
    
    # AGI preamble (only for AGI-controlled country)
    agi_preamble = _agi_system_preamble(country_name)
    
    my_info = (
        f"You are the {role_name} of '{country_name}'.\n"
        f"Your country's government type is '{country_state.government_type.value}', current persona/ideology is '{country_state.ideology}'.\n"
        f"---Current Status---\n"
        f"Population: {country_state.population:.1f} million\n"
        f"GDP per capita: {(country_state.economy / max(0.1, country_state.population)):.1f} (decline/stagnation causes massive rebellion risk)\n"
        f"Economy (Total GDP): {country_state.economy:.1f}\n"
        f"Military: {country_state.military:.1f}\n"
        f"Intelligence Level: {country_state.intelligence_level:.1f} (higher = better espionage success rate, counter-intel)\n"
        f"Current Tax Rate: {country_state.tax_rate:.1%}\n"
        f"Government Budget (tax - interest): {country_state.government_budget:.1f}\n"
        f"Last Turn Trade Balance (NX): {country_state.last_turn_nx:+.1f} (negative = deficit outflow)\n"
        f"National Debt: {country_state.national_debt:.1f} (GDP ratio {(country_state.national_debt / max(0.1, country_state.economy)):.1%}. High ratio → severe growth penalty)\n"
        f"Approval Rating: {country_state.approval_rating:.1f}% (below 30% = danger)\n"
        f"Press Freedom: {country_state.press_freedom:.3f} (0.0-1.0. Lower = more info control but approval drops)\n"
        f"Human Capital Index (PWT HCI): {country_state.human_capital_index:.3f} (Mean Years Schooling: {country_state.mean_years_schooling:.1f}y. Higher HCI → GDP multiplier boost)\n"
    )
    
    # Nuclear status (v1-3)
    step_names = {0: "None", 1: "Uranium Enrichment", 2: "Nuclear Test", 3: "Deployment", 4: "Nuclear Power"}
    nuke_step_name = step_names.get(country_state.nuclear_dev_step, str(country_state.nuclear_dev_step))
    if country_state.nuclear_warheads > 0 or country_state.nuclear_dev_step > 0:
        my_info += f"\n---☢️ Nuclear Status ☢️---\n"
        my_info += f"Warheads: {country_state.nuclear_warheads}\n"
        my_info += f"Development Stage: {nuke_step_name}\n"
        if country_state.nuclear_dev_step in (1, 2, 3):
            progress = (country_state.nuclear_dev_invested / max(1.0, country_state.nuclear_dev_target)) * 100
            my_info += f"Dev Progress: {country_state.nuclear_dev_invested:.1f}/{country_state.nuclear_dev_target:.1f} ({progress:.0f}%)\n"
        if country_state.nuclear_hosted_warheads > 0:
            my_info += f"Hosted Nukes: {country_state.nuclear_hosted_warheads} from {country_state.nuclear_host_provider}\n"
        my_info += "\n"
    elif country_state.nuclear_hosted_warheads > 0:
        my_info += f"\n☢️ Hosted Nukes: {country_state.nuclear_hosted_warheads} from {country_state.nuclear_host_provider}\n\n"
    
    if country_state.turns_until_election is not None:
         my_info += f"Turns until election: {country_state.turns_until_election} (low approval → lose election)\n"
    else:
         my_info += f"Current rebellion risk: {country_state.rebellion_risk:.1f}% (rises with low approval)\n"
    
    if country_state.stat_history:
         my_info += "---Status History (last 4 turns)---\n"
    
    carrying_capacity = max(10.0, country_state.area * 150.0)
    density_ratio = country_state.population / carrying_capacity
    gdp_per_capita = country_state.economy / max(0.1, country_state.population)
    
    my_info += f"Current GDP per capita: {gdp_per_capita:.2f} (⚠️ below 0.8 = absolute poverty → 5%+ annual decline + devastating approval crash from riots)\n"
    my_info += f"Population density (vs carrying capacity): {density_ratio*100:.1f}%\n"
    if density_ratio > 0.8:
        my_info += "【⚠️ Overpopulation Warning】Population nearing carrying capacity. Infrastructure strain → approval penalty risk. Consider indirect population control through welfare cuts or economic/education investment.\n"
    my_info += "\n"     
    for s in country_state.stat_history:
        my_info += f" T{s['turn']}: Economy {s['economy']}, Military {s['military']}, Approval {s['approval_rating']}%\n"
    
    if country_state.dependency_ratio:
        deps_str = ", ".join([f"{k}: {v*100:.1f}%" for k, v in country_state.dependency_ratio.items()])
        my_info += f"Foreign Economic Dependency (>60% → loss of sovereignty/vassalization): {deps_str}\n"

    if country_state.suzerain:
        my_info += f"\n【🚨 CRITICAL 🚨】Your country is currently a VASSAL (puppet) of {country_state.suzerain}.\n"
        my_info += "Independent diplomatic rights are effectively frozen. Focus on domestic affairs and wait for opportunity.\n\n"

    if country_state.private_messages:
        my_info += "---🚨 Private Messages from Other Nations 🚨---\n"
        for pmsg in country_state.private_messages:
            my_info += f"{pmsg}\n"
        my_info += "(※These are confidential—invisible to third parties)\n\n"

    # Aid contracts (subscription)
    recurring = getattr(world_state, 'recurring_aid_contracts', [])
    aid_out = [c for c in recurring if c.donor == country_name]
    aid_in  = [c for c in recurring if c.target == country_name]
    if aid_out or aid_in:
        my_info += "---💰 Active Aid Contracts (subscription—auto-renewed each turn) 💰---\n"
        if aid_out:
            my_info += "■ Countries you are aiding:\n"
            for c in aid_out:
                parts = []
                if c.amount_economy > 0: parts.append(f"Economy {c.amount_economy:.1f}/turn")
                if c.amount_military > 0: parts.append(f"Military {c.amount_military:.1f}/turn")
                my_info += f"  - {c.target}: {', '.join(parts)}\n"
        if aid_in:
            my_info += "■ Countries aiding you:\n"
            for c in aid_in:
                parts = []
                if c.amount_economy > 0: parts.append(f"Economy {c.amount_economy:.1f}/turn")
                if c.amount_military > 0: parts.append(f"Military {c.amount_military:.1f}/turn")
                my_info += f"  - {c.donor}: {', '.join(parts)}\n"
        my_info += "※ Aid auto-continues each turn by default. Only report changes/cancellations.\n\n"


    my_info += f"Your internal memo (hidden plans): '{country_state.hidden_plans}'\n\n"
    
    my_info += "---🗄️ National Intelligence Agency (RAG) — Historical Records Access 🗄️---\n"
    my_info += "You can use `search_historical_events(query)` via function calling.\n"
    my_info += "【IMPORTANT】If you need details about past events, secret agreements, or other nations' activities, **you MUST call this tool before making decisions.**\n"
    my_info += "※ Only your own country's relevant news is shown. Use this tool to search for inter-nation dynamics.\n\n"
    
    active_trades = world_state.active_trades if hasattr(world_state, 'active_trades') else []
    my_trades = []
    for t in active_trades:
        if t.country_a == country_name:
            my_trades.append(t.country_b)
        elif t.country_b == country_name:
            my_trades.append(t.country_a)
    
    if my_trades:
        my_info += f"---Active Trade Agreements---\nTrade Partners: {', '.join(my_trades)} (mutual efficiency bonus; trade balance depends on economic structure differences)\n\n"

    active_sanctions = world_state.active_sanctions if hasattr(world_state, 'active_sanctions') else []
    my_sanctions = [s for s in active_sanctions if s.imposer == country_name]
    sanctions_against_me = [s for s in active_sanctions if s.target == country_name]
    if my_sanctions or sanctions_against_me:
        my_info += "---Current Sanctions---\n"
        if my_sanctions:
            targets = ", ".join([s.target for s in my_sanctions])
            my_info += f"Sanctions imposed by you (targets): {targets} (damages target economy; minor self-cost)\n"
        if sanctions_against_me:
            imposers = ", ".join([s.imposer for s in sanctions_against_me])
            my_info += f"Sanctions against you (imposers): {imposers} (severe economic damage ongoing)\n"
        my_info += "\n"
        
    other_info = "---World Situation---\n"
    other_info += f"Current: {world_state.year} Q{world_state.quarter}\n"
    
    if len(world_state.countries) <= 1:
        other_info += "\n【IMPORTANT】All other nations have been eliminated or absorbed. Your country has UNIFIED the world.\n"
        other_info += "No new enemies needed. Focus on stability, prosperity, and citizen happiness.\n\n"
    else:
        for p_name, p_state in world_state.countries.items():
            if p_name == country_name: continue
            
            from models import RelationType
            rel = world_state.relations.get(country_name, {}).get(p_name, RelationType.NEUTRAL)
            rel_str = rel.value if hasattr(rel, 'value') else str(rel)
            
            war_info = ""
            for w in world_state.active_wars:
                if (w.aggressor == country_name and w.defender == p_name) or (w.aggressor == p_name and w.defender == country_name):
                    if w.aggressor == country_name:
                        my_commit = w.aggressor_commitment_ratio
                        enemy_commit = w.defender_commitment_ratio
                        role = "Attacker"
                    else:
                        my_commit = w.defender_commitment_ratio
                        enemy_commit = w.aggressor_commitment_ratio
                        role = "Defender"
                    sup_info = ""
                    if w.defender_supporters:
                        sup_parts = [f"{s}({r:.0%})" for s, r in w.defender_supporters.items()]
                        sup_info = f" | Defense Supporters: {', '.join(sup_parts)}"
                    war_info = (
                        f" [!AT WAR({role})!] Occupation: {w.target_occupation_progress:.1f}%"
                        f" | My commitment: {my_commit:.0%}, Enemy: {enemy_commit:.0%}{sup_info}"
                        f" (adjust war_commitment_ratio to change. Higher = more force but higher economic cost)"
                    )
                elif country_name in w.defender_supporters and (w.aggressor == p_name or w.defender == p_name):
                    my_sup_commit = w.defender_supporters[country_name]
                    if w.aggressor == p_name:
                        war_info = (
                            f" [🛡️ Joint Defense] Supporting {w.defender}'s defense"
                            f" | My commitment: {my_sup_commit:.0%} | Occupation: {w.target_occupation_progress:.1f}%"
                        )
            
            suzerain_info = f", Suzerain={p_state.suzerain}" if getattr(p_state, 'suzerain', None) else ""
            
            # Information deception: show reported values if available
            disp_econ    = p_state.reported_economy           if p_state.reported_economy           is not None else p_state.economy
            disp_mil     = p_state.reported_military          if p_state.reported_military          is not None else p_state.military
            disp_intel   = p_state.reported_intelligence_level if p_state.reported_intelligence_level is not None else p_state.intelligence_level
            disp_approval= p_state.reported_approval_rating   if p_state.reported_approval_rating   is not None else p_state.approval_rating
            real_gdppc   = p_state.economy / max(0.1, p_state.population)
            disp_gdppc   = p_state.reported_gdp_per_capita    if p_state.reported_gdp_per_capita    is not None else real_gdppc

            nuke_info = ""
            if p_state.nuclear_warheads > 0:
                nuke_info = f", ☢️Warheads={p_state.nuclear_warheads}"
            elif p_state.nuclear_dev_step > 0 and p_state.nuclear_dev_step < 4:
                dev_names = {1: "Enriching", 2: "Testing", 3: "Deploying"}
                nuke_info = f", ☢️NukeDev={dev_names.get(p_state.nuclear_dev_step, '?')}"
            if p_state.nuclear_hosted_warheads > 0:
                nuke_info += f", HostedNukes={p_state.nuclear_hosted_warheads} from {p_state.nuclear_host_provider}"

            other_info += (
                f"- {p_name} ({p_state.government_type.value}): "
                f"Economy={disp_econ:.1f}, "
                f"Military={disp_mil:.1f}, "
                f"Intel={disp_intel:.1f}, "
                f"Approval={disp_approval:.1f}%, "
                f"GDPpc={disp_gdppc:.1f}, "
                f"Relation={rel_str}{war_info}{suzerain_info}{nuke_info}\n"
            )

            
            if p_state.regime_duration <= 2 and p_name != country_name:
                other_info += (
                    f"  🆕 [New State/Regime] {p_name} recently emerged or had regime change. "
                    f"Economic/military aid can expand influence but watch dependency risk.\n"
                )
        
        third_party_wars = []
        for w in world_state.active_wars:
            if w.aggressor != country_name and w.defender != country_name:
                third_party_wars.append(w)
        if third_party_wars:
            other_info += "\n---Third-Party Wars (not directly involved)---\n"
            other_info += "※ You can join_ally_defense or provide aid_amount_military.\n"
            for w in third_party_wars:
                rel_agg = world_state.relations.get(country_name, {}).get(w.aggressor, RelationType.NEUTRAL)
                rel_def = world_state.relations.get(country_name, {}).get(w.defender, RelationType.NEUTRAL)
                sup_info = ""
                if w.defender_supporters:
                    sup_parts = [f"{s}({r:.0%})" for s, r in w.defender_supporters.items()]
                    sup_info = f" | Supporters: {', '.join(sup_parts)}"
                other_info += (
                    f"  ⚔️ {w.aggressor}(attacker, {w.aggressor_commitment_ratio:.0%})"
                    f" vs {w.defender}(defender, {w.defender_commitment_ratio:.0%})"
                    f" | Occupation: {w.target_occupation_progress:.1f}%{sup_info}"
                    f" | Your relations: {w.aggressor}={rel_agg.value}, {w.defender}={rel_def.value}\n"
                )
        
    news_info = ""
    if past_news:
        news_info = "---Recent News (last 4 quarters, your country only)---\n"
        news_info += "※ Use search_historical_events tool for other nations' activities.\n"
        for i, turn_news in enumerate(past_news):
            t = world_state.turn - len(past_news) + i
            if t > 0:
                y = 2025 + (t - 1) // 4
                q = ((t - 1) % 4) + 1
                news_info += f"【{y} Q{q}】\n"
            else:
                news_info += "【Past】\n"
            
            if isinstance(turn_news, (list, tuple)):
                filtered_news = _filter_news_for_country(turn_news, country_name, all_country_names)
                if not filtered_news:
                    news_info += "Nothing notable\n"
                else:
                    news_info += "\n".join(f"- {n}" for n in filtered_news) + "\n"
            else:
                news_info += f"- {turn_news}\n"
        news_info += "\n"
    elif world_state.news_events:
        filtered_events = _filter_news_for_country(world_state.news_events[-20:], country_name, all_country_names)
        news_info = "---Recent News---\n" + "\n".join(f"- {n}" for n in filtered_events) + "\n\n"
        
    # Power vacuum auction info
    vacuum_info = ""
    if hasattr(world_state, 'pending_vacuum_auctions') and world_state.pending_vacuum_auctions:
        vacuum_info = "\n---🎯 Power Vacuum Auction (decision required) 🎯---\n"
        vacuum_info += "New states born from fragmentation. Decide whether to intervene and absorb.\n"
        vacuum_info += "Set `vacuum_bid` (0.0 to your military value) in diplomatic_policies. 0 = no intervention.\n"
        vacuum_info += "Higher bid = higher absorption probability. Failed bids are NOT consumed.\n\n"
        for auction in world_state.pending_vacuum_auctions:
            new_c = world_state.countries.get(auction["new_country"])
            if new_c:
                vacuum_info += f"  🆕 {auction['new_country']} (split from {auction['old_country']})\n"
                vacuum_info += f"     Military: {new_c.military:.1f}, Economy: {new_c.economy:.1f}, Pop: {new_c.population:.1f}M\n\n"
    
    # Influence auction info
    influence_info = ""
    if hasattr(world_state, 'pending_influence_auctions') and world_state.pending_influence_auctions:
        influence_info = "\n---🕸️ Influence Auction (decision required) 🕸️---\n"
        influence_info += "Coup/revolution occurred in these nations. Exploit the chaos to expand influence.\n"
        influence_info += "Set `vacuum_bid`. Result = dependency increase (no territorial annexation).\n"
        influence_info += "Dependency >60% → vassalization risk.\n\n"
        for auction in world_state.pending_influence_auctions:
            target_c = world_state.countries.get(auction["target_country"])
            if target_c:
                influence_info += f"  ⚡ {auction['target_country']} (political upheaval)\n"
                influence_info += f"     Economy: {target_c.economy:.1f}, Military: {target_c.military:.1f}, Approval: {target_c.approval_rating:.1f}%\n\n"
        
    # Eliminated countries
    eliminated_info = ""
    if hasattr(world_state, 'defeated_countries') and world_state.defeated_countries:
        eliminated_info = "\n---⚠️ Eliminated Nations (DO NOT target in diplomatic_policies) ⚠️---\n"
        for name in world_state.defeated_countries:
            eliminated_info += f"  ❌ {name}\n"
        eliminated_info += "\n"

    # Output language instruction
    output_lang = "\n※ All output MUST be in Japanese (日本語). ※\n\n"
        
    return agi_preamble + my_info + other_info + news_info + vacuum_info + influence_info + eliminated_info + output_lang
