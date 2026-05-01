from typing import Dict, List
from models import WorldState, CountryState, PresidentPolicy
from agent.prompts.base import build_common_context
from agent.prompts.diplomatic import build_policy_section

def _other_countries(world_state: WorldState, country_name: str) -> List[str]:
    return [n for n in world_state.countries if n != country_name]


def build_message_prompt(country_name, country_state: CountryState, world_state: WorldState,
                         policy: PresidentPolicy, analyst_reports: Dict = None, past_news=None) -> str:
    """D-01: Diplomatic Messages (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Diplomatic Officer (Messages)")
    others = _other_countries(world_state, country_name)
    return ctx + build_policy_section(policy) + f"""
Other nations: {', '.join(others)}
Send public or private messages to nations if needed. Return empty list if none needed.

Output ONLY JSON:
{{"messages": [{{"target_country": "country", "message": "message content", "is_private": false, "reason": "理由（30文字以内）"}}]}}
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
All Nations: {', '.join(others)}

Propose new trade (propose_trade=true) or cancel existing (cancel_trade=true) if needed.

Output ONLY JSON:
{{"trade_actions": [{{"target_country": "country", "propose_trade": false, "cancel_trade": false, "reason": "理由（30文字以内）"}}]}}
"""


def build_sanctions_prompt(country_name, country_state: CountryState, world_state: WorldState,
                           policy: PresidentPolicy, past_news=None) -> str:
    """D-03: Economic Sanctions (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Diplomatic Officer (Sanctions)")
    active_out = [s.target for s in world_state.active_sanctions if s.imposer == country_name]
    active_in  = [s.imposer for s in world_state.active_sanctions if s.target == country_name]
    others = _other_countries(world_state, country_name)
    return ctx + build_policy_section(policy) + f"""
Your active sanctions: {', '.join(active_out) or 'None'}
Sanctions against you: {', '.join(active_in) or 'None'}
Targets: {', '.join(others)}

Impose (impose_sanctions=true) or lift (lift_sanctions=true) sanctions if needed.

Output ONLY JSON:
{{"sanction_actions": [{{"target_country": "country", "impose_sanctions": false, "lift_sanctions": false, "reason": "理由（30文字以内）"}}]}}
"""


def build_summit_prompt(country_name, country_state: CountryState, world_state: WorldState,
                        policy: PresidentPolicy, past_news=None) -> str:
    """D-04: Bilateral Summit (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Diplomatic Officer (Summit)")
    pending_in = [s.proposer for s in world_state.pending_summits
                  if s.target == country_name and not s.participants]
    others = _other_countries(world_state, country_name)
    return ctx + build_policy_section(policy) + f"""
Pending summit proposals (received last turn): {', '.join(pending_in) or 'None'}
Targets: {', '.join(others)}

Propose or accept bilateral summits.

Output ONLY JSON:
{{"summit_actions": [{{"target_country": "country", "propose_summit": false, "accept_summit": false, "summit_topic": null, "reason": "理由（30文字以内）"}}]}}
"""


def build_multilateral_summit_prompt(country_name, country_state: CountryState, world_state: WorldState,
                                     policy: PresidentPolicy, past_news=None) -> str:
    """D-05: Multilateral Summit (flash)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Diplomatic Officer (Multilateral)")
    others = _other_countries(world_state, country_name)
    pending_multi = [s for s in world_state.pending_summits
                     if s.participants and country_name in s.participants and s.proposer != country_name]
    pending_str = ", ".join(f"{s.proposer} proposal ({s.topic})" for s in pending_multi) or "None"
    return ctx + build_policy_section(policy) + f"""
Pending multilateral summits: {pending_str}
Invitable nations: {', '.join(others)}

Propose (propose_multilateral_summit=true) or accept (accept_summit=true) multilateral summits.
Return empty list if none needed.

Output ONLY JSON:
{{"multilateral_actions": [{{"target_country": "host (self for proposal, host for acceptance)", "propose_multilateral_summit": false, "accept_summit": false, "summit_participants": [], "summit_topic": null, "reason": "理由（30文字以内）"}}]}}
"""


def build_aid_donor_prompt(country_name, country_state: CountryState, world_state: WorldState,
                           policy: PresidentPolicy, past_news=None) -> str:
    """D-06: Foreign Aid (donor side) (flash)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Diplomatic Officer (Aid Donor)")
    aid_out = [c for c in world_state.recurring_aid_contracts if c.donor == country_name]
    aid_str = "\n".join(f"  - {c.target}: Econ {c.amount_economy:.1f}/T, Mil {c.amount_military:.1f}/T" for c in aid_out) or "(None)"
    others = _other_countries(world_state, country_name)
    return ctx + build_policy_section(policy) + f"""
【Current Aid Contracts (subscription—auto-renewed each turn)】
{aid_str}

Aid targets: {', '.join(others)}
【Note】Do NOT output if no change needed (0.0 = no change to existing contract). Cancel = aid_cancel: true.
⚠️ Cumulative aid ratio >60% → vassalization risk / Single turn >20% GDP → Dutch Disease.

Output ONLY JSON (only for countries with changes/cancellations):
{{"aid_actions": [{{"target_country": "country", "aid_amount_economy": 0.0, "aid_amount_military": 0.0, "aid_cancel": false, "reason": "理由（30文字以内）"}}]}}
"""


def build_aid_acceptance_prompt(country_name, country_state: CountryState, world_state: WorldState,
                                policy: PresidentPolicy, past_news=None) -> str:
    """D-07: Aid Acceptance Rate (receiver side) (flash-lite)"""
    ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="Diplomatic Officer (Aid Acceptance)")
    aid_in = [c for c in world_state.recurring_aid_contracts if c.target == country_name]
    if not aid_in:
        return ""  # Skip if no aid received
    aid_str = "\n".join(f"  - {c.donor}: Econ {c.amount_economy:.1f}/T, Mil {c.amount_military:.1f}/T" for c in aid_in)
    dep_str = ", ".join(f"{k}:{v*100:.1f}%" for k, v in country_state.dependency_ratio.items()) or "None"
    return ctx + build_policy_section(policy) + f"""
【Aid Being Received】
{aid_str}
【Current Foreign Dependency】{dep_str} (>60% = vassalization risk)

Set acceptance rate (0.0=reject to 1.0=accept all) per donor.
Consider reducing rate for high-dependency donors.

Output ONLY JSON:
{{"acceptance_actions": [{{"target_country": "donor_country", "aid_acceptance_ratio": 1.0, "reason": "理由（30文字以内）"}}]}}
"""


def build_power_vacuum_prompt(country_name, country_state: CountryState, world_state: WorldState,
                              policy: PresidentPolicy, past_news=None) -> str:
    """D-08: Power Vacuum / Influence Auction (flash)"""
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
            auction_str += f"  - {new_c} (ex:{old_c}): Military {c_state.military:.1f}, Economy {c_state.economy:.1f}\n"
    return ctx + build_policy_section(policy) + f"""
【Available Auctions】
{auction_str}
vacuum_bid (0 to your military value). 0 = no intervention. Higher = higher absorption/influence probability.

Output ONLY JSON:
{{"vacuum_actions": [{{"target_country": "country", "vacuum_bid": 0.0, "reason": "理由（30文字以内）"}}]}}
"""
