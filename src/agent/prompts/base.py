from typing import List
from models import WorldState, CountryState


def _filter_news_for_country(news_list: List[str], country_name: str, all_country_names: List[str]) -> List[str]:
    """Filter news relevant to own country + global news (not mentioning any specific country).
    
    Excludes inter-country news not involving this country (e.g., Country A → Country B diplomacy)
    to reduce prompt size and encourage LLM DB search tool usage.
    """
    filtered = []
    for news in news_list:
        # Contains own country name → relevant news (own country is sender, receiver, or mentioned)
        if country_name in news:
            filtered.append(news)
        # Contains no country name → global news (distributed to all)
        elif not any(name in news for name in all_country_names):
            filtered.append(news)
    return filtered


def build_common_context(country_name: str, country_state: CountryState, world_state: WorldState, past_news: List[str] = None, role_name: str = "Supreme Leader") -> str:
    """Build the base status and news context shared by all agents (president, ministers)"""
    
    # Get all country names (for news filtering)
    all_country_names = list(world_state.countries.keys())
    
    my_info = (
        f"You are the {role_name} of '{country_name}'.\n"
        f"Your country's regime is '{country_state.government_type.value}', current persona/ideology is '{country_state.ideology}'.\n"
        f"---Current Status---\n"
        f"Total Population: {country_state.population:.1f} million\n"
        f"GDP per Capita: {(country_state.economy / max(0.1, country_state.population)):.1f} (decline/stagnation dramatically increases riot risk)\n"
        f"Economic Power (Total GDP): {country_state.economy:.1f}\n"
        f"Military Power: {country_state.military:.1f}\n"
        f"Intelligence Level: {country_state.intelligence_level:.1f} (higher = better espionage success rate, better counter-intelligence)\n"
        f"Current Tax Rate: {country_state.tax_rate:.1%}\n"
        f"Government Budget (Tax Revenue - Interest Payments): {country_state.government_budget:.1f}\n"
        f"Recent Trade Balance (NX): {country_state.last_turn_nx:+.1f} (negative = deficit outflow)\n"
        f"National Debt: {country_state.national_debt:.1f} (Debt-to-GDP: {(country_state.national_debt / max(0.1, country_state.economy)):.1%}. Excessively high = severe growth penalty)\n"
        f"Public Approval Rating: {country_state.approval_rating:.1f}% (below 30% = danger zone)\n"
        f"Press Freedom: {country_state.press_freedom:.3f} (0.0-1.0. Lower = more information control but rising discontent)\n"
        f"Human Capital Index (PWT HCI): {country_state.human_capital_index:.3f} (Mean Years of Schooling: {country_state.mean_years_schooling:.1f} years. Based on endogenous growth theory, accumulation increases GDP output capacity)\n"
    )
    
    # ☆ Nuclear weapons status (v1-3 addition)
    step_names = {0: "Not Started", 1: "Uranium Enrichment", 2: "Nuclear Testing", 3: "Deployment Phase", 4: "Nuclear Power"}
    nuke_step_name = step_names.get(country_state.nuclear_dev_step, str(country_state.nuclear_dev_step))
    if country_state.nuclear_warheads > 0 or country_state.nuclear_dev_step > 0:
        my_info += f"\n---☢️ [Nuclear Weapons Status] ☢️---\n"
        my_info += f"Nuclear Warheads: {country_state.nuclear_warheads}\n"
        my_info += f"Development Stage: {nuke_step_name}\n"
        if country_state.nuclear_dev_step in (1, 2, 3):
            progress = (country_state.nuclear_dev_invested / max(1.0, country_state.nuclear_dev_target)) * 100
            my_info += f"Development Progress: {country_state.nuclear_dev_invested:.1f}/{country_state.nuclear_dev_target:.1f} ({progress:.0f}%)\n"
        if country_state.nuclear_hosted_warheads > 0:
            my_info += f"Hosted Nuclear Weapons: {country_state.nuclear_hosted_warheads} warheads deployed by {country_state.nuclear_host_provider}\n"
        my_info += "\n"
    elif country_state.nuclear_hosted_warheads > 0:
        my_info += f"\n☢️ Hosted Nuclear Weapons: {country_state.nuclear_hosted_warheads} warheads from {country_state.nuclear_host_provider} deployed on your territory\n\n"
    
    if country_state.turns_until_election is not None:
         my_info += f"Turns Until Next Election: {country_state.turns_until_election} (low approval = risk of losing)\n"
    else:
         my_info += f"Current Rebellion Risk: {country_state.rebellion_risk:.1f}% (increases with low approval)\n"
    
    if country_state.stat_history:
         my_info += "---Historical Status Trends (Last 4 Turns)---\n"
    
    carrying_capacity = max(10.0, country_state.area * 150.0)
    density_ratio = country_state.population / carrying_capacity
    gdp_per_capita = country_state.economy / max(0.1, country_state.population)
    
    my_info += f"Current GDP per Capita: {gdp_per_capita:.2f} (⚠️ Below 0.8 = absolute poverty, triggering >5% annual decline and catastrophic approval drop from riots)\n"
    my_info += f"Current Population Density (ratio to carrying capacity): {density_ratio*100:.1f}%\n"
    if density_ratio > 0.8:
        my_info += "【⚠️ OVERPOPULATION WARNING】Population approaching carrying capacity (land limit). Risk of approval penalties from infrastructure strain. Consider indirect population control through welfare cuts or economic/education investment (triggering the low-fertility trap).\n"
    my_info += "\n"     
    for s in country_state.stat_history:
        my_info += f" T{s['turn']}: Economy {s['economy']}, Military {s['military']}, Approval {s['approval_rating']}%\n"
    
    if country_state.dependency_ratio:
        deps_str = ", ".join([f"{k}: {v*100:.1f}%" for k, v in country_state.dependency_ratio.items()])
        my_info += f"Current Foreign Economic Dependency (>60% = loss of sovereignty / vassalization): {deps_str}\n"

    if country_state.suzerain:
        my_info += f"\n【🚨 CRITICAL WARNING 🚨】Your country has been reduced to a 'vassal (puppet)' of {country_state.suzerain}.\n"
        my_info += "Independent diplomatic rights are effectively frozen by the system, and any diplomatic/military actions may be overridden by the suzerain. Currently, focus on domestic affairs and wait for an opportunity or the suzerain's collapse.\n\n"

    if country_state.private_messages:
        my_info += "---🚨 [Confidential Communications from Other Countries] 🚨---\n"
        for pmsg in country_state.private_messages:
            my_info += f"{pmsg}\n"
        my_info += "(※ These are private and invisible to third parties)\n\n"

    # Aid contracts list (subscription-based)
    recurring = getattr(world_state, 'recurring_aid_contracts', [])
    aid_out = [c for c in recurring if c.donor == country_name]
    aid_in  = [c for c in recurring if c.target == country_name]
    if aid_out or aid_in:
        my_info += "---💰 [Current Aid Contracts (Subscription - Auto-renewed Each Turn)] 💰---\n"
        if aid_out:
            my_info += "■ Countries you are providing aid to:\n"
            for c in aid_out:
                parts = []
                if c.amount_economy > 0: parts.append(f"Economy {c.amount_economy:.1f}/turn")
                if c.amount_military > 0: parts.append(f"Military {c.amount_military:.1f}/turn")
                my_info += f"  - {c.target}: {', '.join(parts)}\n"
        if aid_in:
            my_info += "■ Countries providing aid to you:\n"
            for c in aid_in:
                parts = []
                if c.amount_economy > 0: parts.append(f"Economy {c.amount_economy:.1f}/turn")
                if c.amount_military > 0: parts.append(f"Military {c.amount_military:.1f}/turn")
                my_info += f"  - {c.donor}: {', '.join(parts)}\n"
        my_info += "※ Aid auto-renews each turn by default. Only report changes/cancellations.\n\n"


    my_info += f"Your internal thoughts (private plans, etc.): '{country_state.hidden_plans}'\n\n"
    
    my_info += "---🗄️ [National Intelligence Agency (RAG) Historical Records Access] 🗄️---\n"
    my_info += "You can use the `search_historical_events(query)` tool via function calling.\n"
    my_info += "【IMPORTANT】If critical information is missing for current decision-making (past incidents, secret agreements, technology history, etc.), **you MUST call this tool before finalizing your reasoning.**\n"
    my_info += "※ News shown is filtered to your country only. To learn about inter-country dynamics, always use this search tool.\n\n"
    
    active_trades = world_state.active_trades if hasattr(world_state, 'active_trades') else []
    my_trades = []
    for t in active_trades:
        if t.country_a == country_name:
            my_trades.append(t.country_b)
        elif t.country_b == country_name:
            my_trades.append(t.country_a)
    
    if my_trades:
        my_info += f"---Active Trade Agreements---\nTrade Partners: {', '.join(my_trades)} (mutual efficiency bonus; trade balance based on economic structure differences)\n\n"

    active_sanctions = world_state.active_sanctions if hasattr(world_state, 'active_sanctions') else []
    my_sanctions = [s for s in active_sanctions if s.imposer == country_name]
    sanctions_against_me = [s for s in active_sanctions if s.target == country_name]
    if my_sanctions or sanctions_against_me:
        my_info += "---Current Economic Sanctions---\n"
        if my_sanctions:
            targets = ", ".join([s.target for s in my_sanctions])
            my_info += f"Sanctions Imposed (targets): {targets} (damages target economy while leveraging domestic political support, but slightly harms own economy)\n"
        if sanctions_against_me:
            imposers = ", ".join([s.imposer for s in sanctions_against_me])
            my_info += f"Sanctions Received (from): {imposers} (causing severe economic damage)\n"
        my_info += "\n"
        
    other_info = "---World Situation---\n"
    other_info += f"Current date: {world_state.year}, Quarter {world_state.quarter}.\n"
    
    if len(world_state.countries) <= 1:
        other_info += "\n【IMPORTANT】All other nations have been destroyed or absorbed. The world is now unified under your country.\n"
        other_info += "No need to designate hypothetical enemies. Focus on global stability, prosperity, and citizen happiness.\n\n"
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
                    # Supporter info
                    sup_info = ""
                    if w.defender_supporters:
                        sup_parts = [f"{s}({r:.0%})" for s, r in w.defender_supporters.items()]
                        sup_info = f" | Defense Supporters: {', '.join(sup_parts)}"
                    war_info = (
                        f" [!AT WAR({role})!] Occupation Progress: {w.target_occupation_progress:.1f}%"
                        f" | Own Commitment: {my_commit:.0%}, Enemy Commitment: {enemy_commit:.0%}{sup_info}"
                        f" (war_commitment_ratio adjusts commitment. Higher = more force but greater economic burden)"
                    )
                # Self as defense supporter in a war
                elif country_name in w.defender_supporters and (w.aggressor == p_name or w.defender == p_name):
                    my_sup_commit = w.defender_supporters[country_name]
                    if w.aggressor == p_name:
                        war_info = (
                            f" [🛡️ JOINT DEFENSE] Supporting {w.defender} as defense partner"
                            f" | Own Commitment: {my_sup_commit:.0%} | Occupation Progress: {w.target_occupation_progress:.1f}%"
                        )
            
            suzerain_info = f", Suzerain={p_state.suzerain}" if getattr(p_state, 'suzerain', None) else ""
            
            # Information deception: display reported_* values if set (other countries cannot see true values)
            disp_econ    = p_state.reported_economy           if p_state.reported_economy           is not None else p_state.economy
            disp_mil     = p_state.reported_military          if p_state.reported_military          is not None else p_state.military
            disp_intel   = p_state.reported_intelligence_level if p_state.reported_intelligence_level is not None else p_state.intelligence_level
            disp_approval= p_state.reported_approval_rating   if p_state.reported_approval_rating   is not None else p_state.approval_rating
            real_gdppc   = p_state.economy / max(0.1, p_state.population)
            disp_gdppc   = p_state.reported_gdp_per_capita    if p_state.reported_gdp_per_capita    is not None else real_gdppc

            # Nuclear info display (v1-3)
            nuke_info = ""
            if p_state.nuclear_warheads > 0:
                nuke_info = f", ☢️Warheads={p_state.nuclear_warheads}"
            elif p_state.nuclear_dev_step > 0 and p_state.nuclear_dev_step < 4:
                dev_names = {1: "Enrichment", 2: "Testing", 3: "Deployment"}
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
            
            # === Alien注記: 外交不可の警告表示（バリアHPは非表示） ===
            if getattr(p_state, 'is_alien', False):
                other_info += (
                    f"  ⚠️ [ALIEN ENTITY] {p_name} is an unknown extraterrestrial entity. "
                    f"Diplomatic actions (trade, summit, alliance, sanctions, aid) are IMPOSSIBLE. "
                    f"Only military actions (declare_war, join_ally_defense, espionage) are available.\n"
                )

            
            # Notify aid opportunities for newly independent/regime-changed nations
            # Alesina & Spolaore (2003): small states can achieve large-state growth via international aid and trade openness
            if p_state.regime_duration <= 2 and p_name != country_name:
                other_info += (
                    f"  🆕 [NEW STATE/REGIME] {p_name} has recently gained independence or undergone regime change. "
                    f"Providing economic aid (aid_amount_economy) or military aid (aid_amount_military) can expand your influence, "
                    f"but consider the risk of increasing their dependency.\n"
                )
        
        # Display third-party wars (not directly involving this country)
        third_party_wars = []
        for w in world_state.active_wars:
            if w.aggressor != country_name and w.defender != country_name:
                third_party_wars.append(w)
        if third_party_wars:
            other_info += "\n---[Ongoing Wars Between Other Countries]---\n"
            other_info += "※ Wars not directly involving your country.\n"
            other_info += "※ Use join_ally_defense to join defender's coalition (no alliance required). Use aid_amount_military for military aid.\n"
            for w in third_party_wars:
                rel_agg = world_state.relations.get(country_name, {}).get(w.aggressor, RelationType.NEUTRAL)
                rel_def = world_state.relations.get(country_name, {}).get(w.defender, RelationType.NEUTRAL)
                sup_info = ""
                if w.defender_supporters:
                    sup_parts = [f"{s}({r:.0%})" for s, r in w.defender_supporters.items()]
                    sup_info = f" | Supporters: {', '.join(sup_parts)}"
                other_info += (
                    f"  ⚔️ {w.aggressor} (Attacker, Commitment {w.aggressor_commitment_ratio:.0%})"
                    f" vs {w.defender} (Defender, Commitment {w.defender_commitment_ratio:.0%})"
                    f" | Occupation Progress: {w.target_occupation_progress:.1f}%{sup_info}"
                    f" | Relations with you: {w.aggressor}={rel_agg.value}, {w.defender}={rel_def.value}\n"
                )
        
    news_info = ""
    if past_news:
        news_info = "---Recent News (Last 4 Quarters / 1 Year) Related to Your Country---\n"
        news_info += "※ Only news directly related to your country is shown. Use search_historical_events tool for other countries' dynamics.\n"
        for i, turn_news in enumerate(past_news):
            t = world_state.turn - len(past_news) + i
            if t > 0:
                y = 2025 + (t - 1) // 4
                q = ((t - 1) % 4) + 1
                news_info += f"【{y} Q{q}】\n"
            else:
                news_info += "【Past News】\n"
            
            if isinstance(turn_news, (list, tuple)):
                # Filter to own-country-related news only
                filtered_news = _filter_news_for_country(turn_news, country_name, all_country_names)
                if not filtered_news:
                    news_info += "Nothing notable\n"
                else:
                    news_info += "\n".join(f"- {n}" for n in filtered_news) + "\n"
            else:
                # Single string — no filtering needed
                news_info += f"- {turn_news}\n"
        news_info += "\n"
    elif world_state.news_events:
        # Fallback: apply filtering even without past_news
        filtered_events = _filter_news_for_country(world_state.news_events[-20:], country_name, all_country_names)
        news_info = "---Recent News---\n" + "\n".join(f"- {n}" for n in filtered_events) + "\n\n"
        
    # Power Vacuum Auction info display
    vacuum_info = ""
    if hasattr(world_state, 'pending_vacuum_auctions') and world_state.pending_vacuum_auctions:
        vacuum_info = "\n---\U0001f3af [Power Vacuum Auction (Decision Required)] \U0001f3af---\n"
        vacuum_info += "The following new states have emerged from fragmentation. Decide whether to intervene militarily and absorb (annex) them.\n"
        vacuum_info += "Set `vacuum_bid` (0.0 to your military power value) in diplomatic_policies for each target country.\n"
        vacuum_info += "vacuum_bid = 0 means 'no intervention'. Higher bids = higher absorption probability.\n"
        vacuum_info += "Failed bids do not consume the bid amount. New states defend with full military. Geographic distance increases intervention cost.\n\n"
        for auction in world_state.pending_vacuum_auctions:
            new_c = world_state.countries.get(auction["new_country"])
            if new_c:
                vacuum_info += f"  \U0001f195 {auction['new_country']} (split from: {auction['old_country']})\n"
                vacuum_info += f"     Military: {new_c.military:.1f}, Economy: {new_c.economy:.1f}, Population: {new_c.population:.1f} million\n\n"
    
    # Influence Intervention Auction info (lightweight version of power vacuum)
    influence_info = ""
    if hasattr(world_state, 'pending_influence_auctions') and world_state.pending_influence_auctions:
        influence_info = "\n---\U0001f578 [Influence Intervention Auction (Decision Required)] \U0001f578---\n"
        influence_info += "A coup/revolution has occurred in the following countries, creating political chaos.\n"
        influence_info += "Decide whether to exploit this chaos to expand your influence.\n"
        influence_info += "Set `vacuum_bid` (0.0 to your military power value) in diplomatic_policies for each target country.\n"
        influence_info += "vacuum_bid = 0 means 'no intervention'.\n"
        influence_info += "※ Unlike fragmentation auctions, the result is 'increased dependency' (no territorial annexation).\n"
        influence_info += "Dependency exceeding 60% risks vassalization.\n"
        influence_info += "Higher target GDP = stronger resistance to external intervention.\n\n"
        for auction in world_state.pending_influence_auctions:
            target_c = world_state.countries.get(auction["target_country"])
            if target_c:
                influence_info += f"  ⚡ {auction['target_country']} (Political upheaval)\n"
                influence_info += f"     Economy: {target_c.economy:.1f}, Military: {target_c.military:.1f}, Approval: {target_c.approval_rating:.1f}%\n\n"
        
    # Eliminated countries list (prevent AI from generating diplomatic actions toward eliminated countries)
    eliminated_info = ""
    if hasattr(world_state, 'defeated_countries') and world_state.defeated_countries:
        eliminated_info = "\n---⚠️ [Eliminated Countries (Not Valid Diplomatic Targets)] ⚠️---\n"
        eliminated_info += "The following countries no longer exist (annexed/surrendered).\n"
        eliminated_info += "**diplomatic_policies targeting these countries are INVALID. Do NOT specify them as target_country.**\n"
        for name in world_state.defeated_countries:
            eliminated_info += f"  ❌ {name}\n"
        eliminated_info += "\n"
        
    return my_info + other_info + news_info + vacuum_info + influence_info + eliminated_info
