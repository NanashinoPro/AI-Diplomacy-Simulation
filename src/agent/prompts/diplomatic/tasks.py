from typing import Dict, List
from models import WorldState, CountryState, PresidentPolicy
from agent.prompts.base import build_common_context
from agent.prompts.diplomatic import build_policy_section

# Generate list of other countries (common to all diplomatic tasks)
def _other_countries(world_state: WorldState, country_name: str) -> List[str]:
    return [n for n in world_state.countries if n != country_name]


def build_message_prompt(country_name, country_state: CountryState, world_state: WorldState,
                         policy: PresidentPolicy, analyst_reports: Dict = None, past_news=None) -> str:
    """D-01: Diplomatic Message Sending (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Diplomatic Officer (Messages)")
    others = _other_countries(world_state, country_name)
    return ctx + build_policy_section(policy) + f"""
Other countries: {', '.join(others)}
If there are countries that should receive messages, create public or private messages.
Return empty list if not needed. You MUST respond in Japanese.

Output ONLY JSON:
{{"messages": [{{"target_country": "country name", "message": "message content", "is_private": false, "reason": "reason (max 30 chars)"}}]}}
"""


def build_trade_prompt(country_name, country_state: CountryState, world_state: WorldState,
                       policy: PresidentPolicy, past_news=None) -> str:
    """D-02: Trade Agreement Proposal/Cancellation (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Diplomatic Officer (Trade)")
    trade_partners = [t.country_b if t.country_a == country_name else t.country_a for t in world_state.active_trades
                      if t.country_a == country_name or t.country_b == country_name]
    others = _other_countries(world_state, country_name)
    return ctx + build_policy_section(policy) + f"""
Current Trade Partners: {', '.join(trade_partners) or 'None'}
All Countries: {', '.join(others)}

Specify countries for new trade proposals (propose_trade=true) or cancellations (cancel_trade=true). You MUST respond in Japanese.

Output ONLY JSON:
{{"trade_actions": [{{"target_country": "country name", "propose_trade": false, "cancel_trade": false, "reason": "reason (max 30 chars)"}}]}}
"""


def build_sanctions_prompt(country_name, country_state: CountryState, world_state: WorldState,
                           policy: PresidentPolicy, past_news=None) -> str:
    """D-03: Economic Sanctions Imposition/Lifting (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Diplomatic Officer (Sanctions)")
    active_out = [s.target for s in world_state.active_sanctions if s.imposer == country_name]
    active_in  = [s.imposer for s in world_state.active_sanctions if s.target == country_name]
    others = _other_countries(world_state, country_name)
    return ctx + build_policy_section(policy) + f"""
Own Sanctions Active: {', '.join(active_out) or 'None'}
Sanctions Received: {', '.join(active_in) or 'None'}
Target Candidates: {', '.join(others)}

Specify countries to impose sanctions (impose_sanctions=true) or lift sanctions (lift_sanctions=true). You MUST respond in Japanese.

Output ONLY JSON:
{{"sanction_actions": [{{"target_country": "country name", "impose_sanctions": false, "lift_sanctions": false, "reason": "reason (max 30 chars)"}}]}}
"""


def build_summit_prompt(country_name, country_state: CountryState, world_state: WorldState,
                        policy: PresidentPolicy, past_news=None) -> str:
    """D-04: Summit Proposal/Acceptance (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Diplomatic Officer (Summits)")
    pending_in = [s.proposer for s in world_state.pending_summits
                  if s.target == country_name and not s.participants]
    others = _other_countries(world_state, country_name)
    return ctx + build_policy_section(policy) + f"""
Pending Summit Proposals (received last turn): {', '.join(pending_in) or 'None'}
Target Candidates: {', '.join(others)}

Decide on bilateral summit proposals and acceptances. You MUST respond in Japanese.

Output ONLY JSON:
{{"summit_actions": [{{"target_country": "country name", "propose_summit": false, "accept_summit": false, "summit_topic": null, "reason": "reason (max 30 chars)"}}]}}
"""


def build_multilateral_summit_prompt(country_name, country_state: CountryState, world_state: WorldState,
                                     policy: PresidentPolicy, past_news=None) -> str:
    """D-05: Multilateral Summit Proposal (flash)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Diplomatic Officer (Multilateral)")
    others = _other_countries(world_state, country_name)
    pending_multi = [s for s in world_state.pending_summits
                     if s.participants and country_name in s.participants and s.proposer != country_name]
    pending_str = ", ".join(f"{s.proposer} proposal ({s.topic})" for s in pending_multi) or "None"
    return ctx + build_policy_section(policy) + f"""
Pending Multilateral Summits: {pending_str}
Invitable Countries: {', '.join(others)}

Decide on multilateral summit proposals (propose_multilateral_summit=true) or acceptance (accept_summit=true).
Return empty list if not needed. You MUST respond in Japanese.

Output ONLY JSON:
{{"multilateral_actions": [{{"target_country": "host country (acceptance) or own (proposal)", "propose_multilateral_summit": false, "accept_summit": false, "summit_participants": [], "summit_topic": null, "reason": "reason (max 30 chars)"}}]}}
"""


def build_aid_donor_prompt(country_name, country_state: CountryState, world_state: WorldState,
                           policy: PresidentPolicy, past_news=None) -> str:
    """D-06: Foreign Aid Configuration (Donor) (flash)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Diplomatic Officer (Aid Sending)")
    aid_out = [c for c in world_state.recurring_aid_contracts if c.donor == country_name]
    aid_str = "\n".join(f"  - {c.target}: Economy {c.amount_economy:.1f}/T, Military {c.amount_military:.1f}/T" for c in aid_out) or "(None)"
    others = _other_countries(world_state, country_name)
    return ctx + build_policy_section(policy) + f"""
【Current Aid Contracts (Subscription - Auto-renewed Each Turn)】
{aid_str}

Aid Candidates: {', '.join(others)}
【Note】Do not output if no changes needed (0.0 = no change). Cancel with aid_cancel=true.
⚠️ Cumulative aid ratio >60% = vassalization risk / >20% GDP per turn = Dutch Disease.

You MUST respond in Japanese. Output ONLY JSON (only countries with changes/cancellations):
{{"aid_actions": [{{"target_country": "country name", "aid_amount_economy": 0.0, "aid_amount_military": 0.0, "aid_cancel": false, "reason": "reason (max 30 chars)"}}]}}
"""


def build_aid_acceptance_prompt(country_name, country_state: CountryState, world_state: WorldState,
                                policy: PresidentPolicy, past_news=None) -> str:
    """D-07: Aid Acceptance Ratio Configuration (Recipient) (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Diplomatic Officer (Aid Receiving)")
    aid_in = [c for c in world_state.recurring_aid_contracts if c.target == country_name]
    if not aid_in:
        return ""  # Skip if not receiving aid
    aid_str = "\n".join(f"  - {c.donor}: Economy {c.amount_economy:.1f}/T, Military {c.amount_military:.1f}/T" for c in aid_in)
    dep_str = ", ".join(f"{k}:{v*100:.1f}%" for k, v in country_state.dependency_ratio.items()) or "None"
    return ctx + build_policy_section(policy) + f"""
【Aid Contracts Received】
{aid_str}
【Current Foreign Dependency】{dep_str} (>60% = vassalization risk)

Set aid acceptance ratio (0.0=reject to 1.0=full acceptance) per donor country.
Consider reducing ratio for countries where dependency is rising. You MUST respond in Japanese.

Output ONLY JSON:
{{"acceptance_actions": [{{"target_country": "donor country name", "aid_acceptance_ratio": 1.0, "reason": "reason (max 30 chars)"}}]}}
"""


def build_power_vacuum_prompt(country_name, country_state: CountryState, world_state: WorldState,
                              policy: PresidentPolicy, past_news=None) -> str:
    """D-08: Power Vacuum / Influence Intervention Bidding (flash)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Diplomatic Officer (Sphere of Influence)")
    auctions = list(world_state.pending_vacuum_auctions) + list(world_state.pending_influence_auctions)
    if not auctions:
        return ""  # Skip if no auctions
    auction_str = ""
    for a in auctions:
        new_c = a.get("new_country") or a.get("target_country", "")
        old_c = a.get("old_country", "")
        c_state = world_state.countries.get(new_c)
        if c_state:
            auction_str += f"  - {new_c} (former: {old_c}): Military {c_state.military:.1f}, Economy {c_state.economy:.1f}\n"
    return ctx + build_policy_section(policy) + f"""
【Available Auctions for Intervention】
{auction_str}
vacuum_bid (0 to own military power). 0 = no intervention. Higher = higher absorption/influence probability.

You MUST respond in Japanese. Output ONLY JSON:
{{"vacuum_actions": [{{"target_country": "country name", "vacuum_bid": 0.0, "reason": "reason (max 30 chars)"}}]}}
"""
