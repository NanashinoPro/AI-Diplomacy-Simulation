import types
import time
import json
from typing import List, Tuple, Any, Dict, Optional, Callable
from google.genai import types as genai_types
from models import WorldState, CountryState, SummitProposal
from logger import SimulationLogger

SUMMIT_MODEL = "gemini-2.5-flash"

def _generate_with_tool(generate_func, logger: SimulationLogger, model: str, prompt: str, category: str, 
                        search_tool=None, country_name: str = "Summit") -> str:
    """Call LLM with DB search tool, and follow up on tool calls if any"""
    tools = [search_tool] if search_tool else None
    config = genai_types.GenerateContentConfig(tools=tools, temperature=0.4) if tools else None
    
    response = generate_func(model=model, contents=prompt, config=config, category=category)
    
    # Tool call processing (equivalent to core.py _execute_agent)
    if search_tool and getattr(response, 'function_calls', None):
        for function_call in response.function_calls:
            if function_call.name == "search_historical_events":
                args = function_call.args if isinstance(function_call.args, dict) else dict(function_call.args)
                query = args.get("query", "")
                tool_result = search_tool(query)
                
                follow_up_prompt = prompt + f"\n\nSearch results from agent tool '{query}':\n{tool_result}\n\nBased on these, please make your statement."
                response = generate_func(model=model, contents=follow_up_prompt, category=category)
                break
    
    return response.text.strip() if response and hasattr(response, 'text') else "..."

def run_summit(
    generate_func,
    logger: SimulationLogger,
    db_manager,
    proposal: SummitProposal, 
    state_a: CountryState, 
    state_b: CountryState, 
    world_state: WorldState, 
    past_news: List[str] = None,
    search_tool_a: Callable = None,
    search_tool_b: Callable = None
) -> Tuple[str, str]:
    """Execute bilateral summit (max 4 turns of dialogue) and return (summary, full_log) tuple"""
    logger.sys_log(f"[{proposal.proposer} and {proposal.target}] Starting summit (Topic: {proposal.topic}, Model: {SUMMIT_MODEL})")
    
    # Recent relevant events for both countries (DB search)
    news_context = f"【Recent events (last 4 quarters/1 year) between {proposal.proposer} and {proposal.target}】\n"
    has_news = False
    
    if db_manager:
        limit_turns = 4
        min_turn = max(1, world_state.turn - limit_turns + 1)
        recent_events = db_manager.get_recent_events_between_countries(
            proposal.proposer, proposal.target, world_state.turn, limit_turns=limit_turns
        )
        
        # Log the search process
        log_header = f"[Summit DB Search] Query: '{proposal.proposer}' & '{proposal.target}' related events (Turns {min_turn}-{world_state.turn}) -> {len(recent_events)} extracted"
        logger.sys_log(log_header)
        
        if recent_events:
            log_detail = ""
            for ev in recent_events:
                t = ev.get('turn', '?')
                c = ev.get('content', '')
                et = ev.get('event_type', '?')
                log_detail += f"[Turn {t}] [{et}] {c}\n"
                
                # Add to prompt context
                y = 2025 + (t - 1) // 4 if isinstance(t, int) else "?"
                q = ((t - 1) % 4) + 1 if isinstance(t, int) else "?"
                news_context += f"〔{y} Q{q} (Turn {t})〕\n- {c}\n"
            
            logger.sys_log_detail("Summit DB Search Result Details", log_detail)
            news_context += "\n"
            has_news = True
            
    # Fallback if DB unavailable or no events found (legacy implementation)
    if not has_news:
        news_context = "【Recent world news (last 1 year)】\n"
        if past_news:
            for i, turn_news in enumerate(past_news):
                t = world_state.turn - len(past_news) + i
                if t > 0:
                    y = 2025 + (t - 1) // 4
                    q = ((t - 1) % 4) + 1
                    news_context += f"〔{y} Q{q}〕\n"
                else:
                    news_context += "〔Past news〕\n"
                
                if isinstance(turn_news, (list, tuple)):
                    if not turn_news:
                        news_context += "Nothing notable\n"
                    else:
                        news_context += "\n".join(f"- {n}" for n in turn_news) + "\n"
                    has_news = True
                elif turn_news:
                    news_context += f"- {turn_news}\n"
                    has_news = True
            news_context += "\n"
        elif world_state.news_events:
            news_context += "\n".join(f"- {n}" for n in world_state.news_events[-20:]) + "\n\n"
            has_news = True
            
        if not has_news:
            news_context = "【Recent important events between both countries (last 1 year)】\nNothing notable\n"
        
    status_a = f"Economy:{state_a.economy:.1f}, Military:{state_a.military:.1f}, Approval:{state_a.approval_rating:.1f}%"
    status_b = f"Economy:{state_b.economy:.1f}, Military:{state_b.military:.1f}, Approval:{state_b.approval_rating:.1f}%"
    
    chat_history = f"【Summit Record】\nParticipants: {proposal.proposer} ({status_a}), {proposal.target} ({status_b})\nTopic: {proposal.topic}\n\n"
    
    is_private_str = "【⚠️ WARNING: This is a strictly confidential private summit. Contents will NOT be leaked to third parties. Frank exchange of views is possible.】\n\n" if getattr(proposal, 'is_private', False) else ""
    
    tool_instruction = "\n【Tool】If needed, use search_historical_events tool to search past diplomatic, domestic, and intelligence records.\n" if (search_tool_a or search_tool_b) else ""
    
    base_context_a = (
        f"You are the head of state governing '{proposal.proposer}'. Regime: {state_a.government_type.value}, Philosophy: {state_a.ideology}.\n"
        f"(※ Real country name, but act as a fictional representative. Do NOT use real politicians' names.)\n"
        f"Your country's power: {status_a}\n"
        f"Counterpart ({proposal.target})'s power: {status_b}\n\n"
        f"Your internal thoughts (private plans, intelligence results, etc.): '{state_a.hidden_plans}'\n\n"
        f"{is_private_str}"
        f"{news_context}\n"
        f"{tool_instruction}"
        f"With the above world situation and your confidential information in mind, discuss '{proposal.topic}' with the counterpart.\n"
        f"You may fabricate details about your own country's information. You MUST speak in Japanese.\n"
    )
    base_context_b = (
        f"You are the head of state governing '{proposal.target}'. Regime: {state_b.government_type.value}, Philosophy: {state_b.ideology}.\n"
        f"(※ Real country name, but act as a fictional representative. Do NOT use real politicians' names.)\n"
        f"Your country's power: {status_b}\n"
        f"Counterpart ({proposal.proposer})'s power: {status_a}\n\n"
        f"Your internal thoughts (private plans, intelligence results, etc.): '{state_b.hidden_plans}'\n\n"
        f"{is_private_str}"
        f"{news_context}\n"
        f"{tool_instruction}"
        f"With the above world situation and your confidential information in mind, discuss '{proposal.topic}' with the counterpart.\n"
        f"You may fabricate details about your own country's information. You MUST speak in Japanese.\n"
    )
    
    logger.sys_log_detail(
        f"Summit Prompt Context ({proposal.proposer} - {proposal.target})",
        f"=== {proposal.proposer} Context ===\n{base_context_a}\n\n=== {proposal.target} Context ===\n{base_context_b}"
    )
    
    messages = []
    total_turns = 4
    for i in range(total_turns):
        current_turn = i + 1
        turn_instruction = f"Currently turn {current_turn} of {total_turns} speaking opportunities.\n【IMPORTANT】Do NOT repeat greetings or closing remarks each time — it's unnatural. Directly respond to the previous statement and continue natural discussion/negotiation.\n【IMPORTANT】Do NOT agree to establish new expert committees or working groups. All matters on the agenda must be decided within this summit.\n【Character limit】Each statement must be within 400 characters."
        if current_turn == total_turns:
             turn_instruction += " This is your final statement. Present conclusions or final proposals."
             
        # A's statement (A goes first)
        prompt_a = base_context_a + turn_instruction + "\nConversation so far:\n" + "\n".join(messages) + f"\n\nPlease input your next statement as {proposal.proposer}:"
        try:
            resp_a = _generate_with_tool(generate_func, logger, SUMMIT_MODEL, prompt_a, "summit", search_tool_a, proposal.proposer)
        except Exception as e:
            logger.sys_log(f"[{proposal.proposer}] API Error (Summit): {e}", "ERROR")
            resp_a = "Communication failure prevented statement."
        messages.append(f"【{proposal.proposer} Leader】: {resp_a}")
        logger.sys_log(f"[Summit {current_turn}/{total_turns}] {proposal.proposer}: {resp_a}")
        
        # B's statement
        prompt_b = base_context_b + turn_instruction + "\nConversation so far:\n" + "\n".join(messages) + f"\n\nPlease input your next statement as {proposal.target}:"
        try:
            resp_b = _generate_with_tool(generate_func, logger, SUMMIT_MODEL, prompt_b, "summit", search_tool_b, proposal.target)
        except Exception as e:
            logger.sys_log(f"[{proposal.target}] API Error (Summit): {e}", "ERROR")
            resp_b = "Communication failure prevented statement."
        messages.append(f"【{proposal.target} Leader】: {resp_b}")
        logger.sys_log(f"[Summit {current_turn}/{total_turns}] {proposal.target}: {resp_b}")
        
    # Agreement summary
    summary_prompt = "From the following summit record, concisely summarize the final 'agreements reached (or failure to reach agreement)' in approximately 100 characters. You MUST respond in Japanese.\n\n" + "\n".join(messages)
    try:
        summary_obj = generate_func(model=SUMMIT_MODEL, contents=summary_prompt, category="summit_summary")
        summary = summary_obj.text.strip() if summary_obj and hasattr(summary_obj, 'text') else "Summit concluded"
    except Exception as e:
        logger.sys_log(f"[Summit Summary] API Error: {e}", "ERROR")
        summary = "API error — failed to summarize summit results."
    
    full_log = chat_history + "\n".join(messages) + f"\n\n【Final Result】\n{summary}"
    logger.sys_log_detail("Summit Log", full_log)
    
    if getattr(proposal, 'is_private', False):
        news_summary = None
    else:
        news_summary = f"🤝 【Summit Result】Summit between {proposal.proposer} and {proposal.target} concluded. Result: {summary}"
        
    return news_summary, full_log


def run_multilateral_summit(
    generate_func,
    logger: SimulationLogger,
    db_manager,
    proposal: SummitProposal,
    country_states: Dict[str, Any],
    world_state: WorldState,
    past_news: List[str] = None,
    search_tools: Dict[str, Callable] = None
) -> Tuple[str, str]:
    """Execute multilateral summit (round-robin) and return (summary, full_log) tuple"""
    participants = proposal.accepted_participants if proposal.accepted_participants else proposal.participants
    if proposal.proposer not in participants:
        participants = [proposal.proposer] + participants
    
    # Exclude non-existent countries
    participants = [p for p in participants if p in country_states]
    
    if len(participants) < 2:
        logger.sys_log(f"[Multilateral Summit] Cancelled — fewer than 2 participants ({participants})", "WARNING")
        return None, ""
    
    participant_names = ", ".join(participants)
    logger.sys_log(f"[Multilateral Summit] Convened: {participant_names} (Topic: {proposal.topic}, Model: {SUMMIT_MODEL})")
    
    # Build status info for each country
    status_map = {}
    for p in participants:
        cs = country_states[p]
        status_map[p] = f"Economy:{cs.economy:.1f}, Military:{cs.military:.1f}, Approval:{cs.approval_rating:.1f}%"
    
    # Collect related events via DB search (all participant pairs)
    news_context = f"【Recent events (last 4 quarters/1 year) among participants ({participant_names})】\n"
    has_news = False
    
    if db_manager:
        limit_turns = 4
        all_events = []
        # Collect events from all participant pair combinations
        for i, p1 in enumerate(participants):
            for p2 in participants[i+1:]:
                events = db_manager.get_recent_events_between_countries(
                    p1, p2, world_state.turn, limit_turns=limit_turns
                )
                all_events.extend(events)
        
        # Deduplicate (by content)
        seen_contents = set()
        unique_events = []
        for ev in all_events:
            c = ev.get('content', '')
            if c not in seen_contents:
                seen_contents.add(c)
                unique_events.append(ev)
        
        if unique_events:
            for ev in unique_events:
                t = ev.get('turn', '?')
                c = ev.get('content', '')
                y = 2025 + (t - 1) // 4 if isinstance(t, int) else "?"
                q = ((t - 1) % 4) + 1 if isinstance(t, int) else "?"
                news_context += f"〔{y} Q{q} (Turn {t})〕\n- {c}\n"
            news_context += "\n"
            has_news = True
            logger.sys_log(f"[Multilateral Summit DB Search] {len(unique_events)} events extracted")
    
    if not has_news:
        news_context = "【Recent important events among participants (last 1 year)】\nNothing notable\n"
    
    is_private_str = "【⚠️ WARNING: This is a strictly confidential private summit. Contents will NOT be leaked to non-participants. Frank exchange of views is possible.】\n\n" if getattr(proposal, 'is_private', False) else ""
    
    # Build base context for each participant
    base_contexts = {}
    for p in participants:
        cs = country_states[p]
        others_status = "\n".join(f"  - {o}: {status_map[o]}" for o in participants if o != p)
        
        tool_instruction = ""
        if search_tools and search_tools.get(p):
            tool_instruction = "\n【Tool】If needed, use search_historical_events tool to search past diplomatic, domestic, and intelligence records.\n"
        
        base_contexts[p] = (
            f"You are the head of state governing '{p}'. Regime: {cs.government_type.value}, Philosophy: {cs.ideology}.\n"
            f"(※ Real country name, but act as a fictional representative. Do NOT use real politicians' names.)\n"
            f"Your country's power: {status_map[p]}\n"
            f"Other participants' power:\n{others_status}\n\n"
            f"Your internal thoughts (private plans, intelligence results, etc.): '{cs.hidden_plans}'\n\n"
            f"{is_private_str}"
            f"{news_context}\n"
            f"{tool_instruction}"
            f"With the above world situation and your confidential information in mind, engage in multilateral discussions on '{proposal.topic}' with participants.\n"
            f"You may fabricate details about your own country's information. You MUST speak in Japanese.\n"
        )
    
    # Execute round-robin dialogue (4 rounds × all participants)
    chat_history = f"【Multilateral Summit Record】\nParticipants: {participant_names}\nTopic: {proposal.topic}\n\n"
    messages = []
    total_rounds = 4
    
    for round_num in range(total_rounds):
        current_round = round_num + 1
        for speaker in participants:
            turn_instruction = (
                f"Currently round {current_round} of {total_rounds}. {len(participants)} countries participating.\n"
                f"【IMPORTANT】Do NOT repeat greetings or closing remarks each time — it's unnatural. Directly respond to the previous statement and continue natural discussion/negotiation.\n"
                f"【IMPORTANT】Do NOT agree to establish new expert committees or working groups. All matters on the agenda must be decided within this summit.\n"
                f"【Character limit】Each statement must be within 400 characters."
            )
            if current_round == total_rounds and speaker == participants[-1]:
                turn_instruction += " This is the final statement of the summit. Present conclusions or final proposals."
            
            prompt = (
                base_contexts[speaker] + turn_instruction + 
                "\nConversation so far:\n" + "\n".join(messages) + 
                f"\n\nPlease input your next statement as {speaker}:"
            )
            
            search_tool = search_tools.get(speaker) if search_tools else None
            try:
                resp = _generate_with_tool(generate_func, logger, SUMMIT_MODEL, prompt, "summit", search_tool, speaker)
            except Exception as e:
                logger.sys_log(f"[{speaker}] API Error (Multilateral Summit): {e}", "ERROR")
                resp = "Communication failure prevented statement."
            
            messages.append(f"【{speaker} Leader】: {resp}")
            logger.sys_log(f"[Multilateral Summit R{current_round}] {speaker}: {resp}")
    
    # Agreement summary
    summary_prompt = (
        f"From the following multilateral summit record (Participants: {participant_names}), "
        f"concisely summarize the final 'agreements reached (or failure to reach agreement)' in approximately 150 characters. You MUST respond in Japanese.\n\n"
        + "\n".join(messages)
    )
    try:
        summary_obj = generate_func(model=SUMMIT_MODEL, contents=summary_prompt, category="summit_summary")
        summary = summary_obj.text.strip() if summary_obj and hasattr(summary_obj, 'text') else "Summit concluded"
    except Exception as e:
        logger.sys_log(f"[Multilateral Summit Summary] API Error: {e}", "ERROR")
        summary = "API error — failed to summarize summit results."
    
    full_log = chat_history + "\n".join(messages) + f"\n\n【Final Result】\n{summary}"
    logger.sys_log_detail("Multilateral Summit Log", full_log)
    
    if getattr(proposal, 'is_private', False):
        news_summary = None
    else:
        news_summary = f"🤝 【Multilateral Summit Result】Multilateral summit by {participant_names} concluded. Result: {summary}"
    
    return news_summary, full_log
