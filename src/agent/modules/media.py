import json
import re
import random
from typing import List, Tuple, Dict, Any
from google.genai import types as genai_types
from models import WorldState, CountryState, AgentAction, GovernmentType
from logger import SimulationLogger

class GeminiSentimentAnalyzer:
    """Sentiment analyzer using Gemini API (gemini-2.5-flash-lite)"""
    SENTIMENT_MODEL = "gemini-2.5-flash-lite"
    
    def __init__(self, client, client_sub=None, token_usage: dict = None):
        self.client = client
        self.client_sub = client_sub
        self.token_usage = token_usage  # Reference to AgentSystem.token_usage (for cost tracking)
    
    def _track_usage(self, response):
        """Record usage_metadata to token_usage"""
        if self.token_usage is not None and hasattr(response, 'usage_metadata') and response.usage_metadata:
            meta = response.usage_metadata
            category = "sentiment_analysis"
            if category not in self.token_usage:
                self.token_usage[category] = {"prompt_tokens": 0, "candidates_token_count": 0, "thoughts_token_count": 0, "model": self.SENTIMENT_MODEL}
            self.token_usage[category]["prompt_tokens"] += getattr(meta, 'prompt_token_count', 0)
            self.token_usage[category]["candidates_token_count"] += getattr(meta, 'candidates_token_count', 0)
            self.token_usage[category]["thoughts_token_count"] += getattr(meta, 'thoughts_token_count', 0) or 0
    
    def _call_api(self, client, prompt: str) -> list:
        """Call sentiment analysis API with specified client"""
        response = client.models.generate_content(
            model=self.SENTIMENT_MODEL,
            contents=prompt
        )
        self._track_usage(response)
        raw = response.text.strip()
        scores = []
        for part in raw.replace(" ", "").split(","):
            try:
                score = float(part)
                score = max(-1.0, min(1.0, score))
                scores.append(score)
            except ValueError:
                continue
        return scores if scores else [0.0]
    
    def analyze(self, text: str) -> list:
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        prompt = (
            "Evaluate the sentiment of the following text with a score.\n"
            "Score ranges from -1.0 (very negative) to +1.0 (very positive). "
            "Return only decimal numbers to 1 digit. For multiple sentences, return comma-separated.\n"
            "Example: 0.3 or -0.5,0.2 — return numbers only, no explanation needed.\n\n"
            f"Text: {text[:300]}"
        )
        try:
            return self._call_api(self.client, prompt)
        except Exception:
            if self.client_sub:
                try:
                    return self._call_api(self.client_sub, prompt)
                except Exception:
                    pass
            return [0.0]

def generate_citizen_sns_posts(
    generate_func,
    logger: SimulationLogger,
    country_name: str, 
    country_state: CountryState, 
    world_state: WorldState, 
    count: int
) -> List[str]:
    """Citizen agent SNS post generation"""
    if count <= 0:
        return []
        
    recent_news = "\n".join([f"- {news}" for news in world_state.news_events[-3:]]) if world_state.news_events else "Nothing notable"
    # Citizens can only see "government-reported" approval (reported value). True value is hidden.
    citizen_approval = (
        country_state.reported_approval_rating
        if country_state.reported_approval_rating is not None
        else country_state.approval_rating
    )
    history_str = ""
    if country_state.stat_history:
        history_str = "- Historical trends:\n" + "\n".join([f"  T{s['turn']}: Economy {s['economy']}, Approval {s['approval_rating']}%" for s in country_state.stat_history]) + "\n"
    
    prompt = f"""You are an ordinary citizen living in {country_name}.
Your country's current situation:
- Political system: {country_state.government_type.value}
- Economic situation: {country_state.economy:.1f}
- Government approval (official): {citizen_approval:.1f}%
{history_str}- Recent world news:
{recent_news}

**Instructions**:
Based on the current approval rating, economic situation, and news, create {count} SNS posts that you would likely write.
If approval is low, reflect dissatisfaction and criticism. If high, reflect praise or everyday peace.
Each post max 100 characters, expressing realistic citizen voices. You MUST write in Japanese.
Output strictly in the following JSON list format.

```json
{{
  "posts": [
    "post text 1",
    "post text 2"
  ]
}}
```
"""
    try:
        response_obj = generate_func(
            model="gemini-2.5-flash-lite", 
            contents=prompt,
            config=genai_types.GenerateContentConfig(response_mime_type="application/json"),
            category="sns"
        )
        response = response_obj.text.strip() if response_obj else "{}"
        
        json_text = response
        match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if match:
            json_text = match.group(1)
        data = json.loads(json_text)
        logger.sys_log_detail(f"{country_name} Citizen SNS Posts", data)
        posts = data.get("posts", [])
        if isinstance(posts, list):
            return [str(p) for p in posts][:count]
        return []
    except Exception as e:
        logger.sys_log(f"[Citizen: {country_name}] SNS generation error: {e}", "ERROR")
        return [f"Could not retrieve citizen voices"] * count

def generate_breakthrough_name(
    generate_func,
    logger: SimulationLogger,
    country_name: str, 
    active_breakthroughs: List[Any], 
    current_year: int
) -> str:
    """Technology breakthrough name generation"""
    history_context = "Past breakthrough history:\nNone"
    if active_breakthroughs:
        history_context = "Past/established breakthrough history:\n" + "\n".join(
            [f"- {bt.name} (Origin: {bt.origin_country})" for bt in active_breakthroughs if bt.name and not bt.name.startswith("（AI生成待ち")]
        )
        
    prompt = f"""The current year is {current_year}. A revolutionary "General Purpose Technology (GPT)" breakthrough has occurred in {country_name}.
    
{history_context}

Instructions:
Considering the above history and existing technology levels, create an entirely new next-generation breakthrough technology that surpasses them all.
Think of bold technologies with industrial-revolution-level impact like generative AI proliferation, nuclear fusion, room-temperature superconductors, etc.
Output only the technology name and brief description (approximately 50 characters total). No line breaks or markdown needed. You MUST output in Japanese.
"""
    try:
        response_obj = generate_func(
            model="gemini-2.5-flash-lite", 
            contents=prompt,
            category="breakthrough"
        )
        response = response_obj.text.strip()
        logger.sys_log(f"[Breakthrough] New technology born in {country_name}: {response}")
        return response
    except Exception as e:
        logger.sys_log(f"[Breakthrough: {country_name}] Generation error: {e}", "ERROR")
        return "次世代汎用人工知能 (AGI) の実用化"

def generate_ideology_democracy(
    generate_func,
    logger: SimulationLogger,
    country_name: str, 
    target_country_state: CountryState, 
    world_state: WorldState, 
    citizen_sns: List[str]
) -> str:
    sns_context = "None"
    if citizen_sns:
        sns_context = "\n".join([f"- {post}" for post in citizen_sns])
        
    news_context = "Recent news:\nNone"
    if world_state.news_events:
        news_context = "Recent news:\n" + "\n".join([f"- {news}" for news in world_state.news_events[-5:]])
        
    history_text = ""
    if target_country_state.stat_history:
         history_text = "\n【Historical Status Trends】\n" + "\n".join([f" T{s['turn']}: Economy {s['economy']}, Military {s['military']}, Approval {s['approval_rating']}%" for s in target_country_state.stat_history]) + "\n"
         
    prompt = f"""You are the new democratic government of {country_name}. Through a recent election or political upheaval, the previous regime has fallen and you have been chosen.

Current Economy: {target_country_state.economy:.1f}, Military: {target_country_state.military:.1f}
Previous regime's ideology: {target_country_state.ideology}
{history_text}
【Citizens' Raw Voices Right Before the New Government (SNS dissatisfaction/demands)】
{sns_context}

{news_context}

Instructions:
After keenly absorbing these citizens' raw voices (dissatisfaction and demands), concisely declare the new government's "new national goal/ideology" in approximately 50 characters. Make the difference from the previous regime clear. You MUST output in Japanese. Output only the ideology without greetings or small talk. No exceptions."""
    
    try:
        response_obj = generate_func(
            model="gemini-2.5-flash-lite", 
            contents=prompt,
            category="ideology"
        )
        response = response_obj.text.strip()
        logger.sys_log(f"[Ideology Change] {country_name}(Democracy): {response}")
        return response
    except Exception as e:
        logger.sys_log(f"[Ideology Change: {country_name}] Generation error: {e}", "ERROR")
        return "前政権の腐敗を払拭し、国民の声に耳を傾ける透明な経済再建を目指す"

def generate_ideology_authoritarian(
    generate_func,
    logger: SimulationLogger,
    country_name: str, 
    target_country_state: CountryState, 
    world_state: WorldState
) -> str:
    news_context = "Recent news:\nNone"
    if world_state.news_events:
        news_context = "Recent news:\n" + "\n".join([f"- {news}" for news in world_state.news_events[-5:]])
        
    history_text = ""
    if target_country_state.stat_history:
         history_text = "\n【Historical Status Trends】\n" + "\n".join([f" T{s['turn']}: Economy {s['economy']}, Military {s['military']}, Approval {s['approval_rating']}%" for s in target_country_state.stat_history]) + "\n"
         
    prompt = f"""You are {country_name}'s authoritarian/dictatorial regime. Either a coup has established a new government, or the next five-year plan is being formulated. There is no need to cater to public opinion.

Current Economy: {target_country_state.economy:.1f}, Military: {target_country_state.military:.1f}
Previous ideology: {target_country_state.ideology}
{history_text}
{news_context}

Instructions:
Based solely on the current political, economic, and international situation above, boldly and coldly declare a powerful "new national goal/ideology" in approximately 50 characters. You may incorporate deterrence against other nations and military/economic hegemonic ambitions. You MUST output in Japanese."""
    
    try:
        response_obj = generate_func(
            model="gemini-2.5-flash-lite", 
            contents=prompt,
            category="ideology"
        )
        response = response_obj.text.strip()
        logger.sys_log(f"[Ideology Change] {country_name}(Authoritarian): {response}")
        return response
    except Exception as e:
        logger.sys_log(f"[Ideology Change: {country_name}] Generation error: {e}", "ERROR")
        return "強権的な指導力により国家を再建し、敵対勢力を排除して永遠の繁栄を確立する"

def generate_fragmentation_profile(
    generate_func,
    logger: SimulationLogger,
    target_country_name: str, 
    sns_logs: List[Dict]
) -> Tuple[str, str]:
    citizen_posts = [p['text'] for p in sns_logs if p['author'] == 'Citizen']
    recent_complaints = "\n".join(f"- {post}" for post in citizen_posts[-10:]) if citizen_posts else "Strong discontent with the government and desire for independence"
    
    prompt = f"""You are a scenario writer for a historical simulation.
Currently, in the country called '{target_country_name}', a coup has occurred due to years of oppression and explosive discontent,
and a new independent nation (or new government) has been established with its own name and ideology.

【Citizens' Anguished Cries Before Independence (SNS voices)】
{recent_complaints}

Instructions:
Read the citizens' voices above (context of dissatisfaction, what regional/ideological undercurrents exist),
and create a new country's "name" and "new ideology (national goal)" that emerged in opposition to the old regime of '{target_country_name}'.
Respond in the following strict JSON format (plain text, no markdown code blocks). You MUST output in Japanese.

{{
  "new_country_name": "(Example: New California Republic, South China Free Federation, Neo-America, Siberian Grand Duchy, etc. — name fitting the context)",
  "new_ideology": "(~50 chars. Example: Overthrowing the old regime's corruption to win regional freedom, true democracy, and economic self-reliance)"
}}"""

    try:
        response_obj = generate_func(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            category="ideology"
        )
        response_text = response_obj.text.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
        response_text = response_text.strip()
        
        data = json.loads(response_text)
        new_name = data.get("new_country_name", f"新{target_country_name}")
        new_ideology = data.get("new_ideology", "旧体制を打破し、新たな理想国家を建設する")
        
        if logger:
            logger.sys_log(f"[Fragmentation] '{new_name}' born from {target_country_name}. Ideology: {new_ideology}")
        return new_name, new_ideology
        
    except Exception as e:
        if logger:
            logger.sys_log(f"[Fragmentation: {target_country_name}] New country profile generation error: {e}", "ERROR")
        return f"{target_country_name}自由国", "圧制を逃れ、自由と真の独立を確立する"

def generate_media_reports(
    generate_func,
    logger: SimulationLogger,
    sentiment_analyzer: GeminiSentimentAnalyzer,
    world_state: WorldState, 
    previous_actions: Dict[str, AgentAction], 
    recent_summit_logs: List[str] = None
) -> Tuple[List[str], Dict[str, float]]:
    """Media agent news article generation and approval impact per country"""        
    if recent_summit_logs is None:
        recent_summit_logs = []
        
    reports = []
    media_modifiers = {}
    for country_name, country_state in world_state.countries.items():
        logger.sys_log(f"[Media: {country_name}] Generating article...")
        try:
            whistleblowing_scandal = ""
            
            base_prob = 5
            if country_state.approval_rating < 50.0:
                base_prob += int((50.0 - country_state.approval_rating) / 2.0)
            if country_state.hidden_plans:
                base_prob += 10
            base_prob = min(base_prob, 30)
            
            final_prob = int(base_prob * country_state.press_freedom)
            
            if random.randint(1, 100) <= final_prob and country_state.hidden_plans:
                whistleblowing_scandal = (
                    f"【BREAKING SCOOP (Whistleblower)】An insider leak has exposed previously classified secret plans.\n"
                    f"Target classified info: {country_state.hidden_plans}\n"
                    f"Instructions: Based on this information, create and add specific scandal elements such as government corruption (bribery, cover-ups, embezzlement, immoral operations), then generate a massive exposé article fiercely criticizing the government. (※ Should significantly decrease approval)\n\n"
                )

            if country_state.government_type == GovernmentType.DEMOCRACY:
                role_desc = "You are an independent media outlet (press) in a liberal democratic state. As the 'Fourth Estate', you monitor the government, but you cannot know about classified intelligence operations (successful espionage or covert processes). You report and comment based only on publicly known policy decisions, economic indicators, and international news. Harshly criticize failures and unfavorable facts (negative approval impact), but appropriately praise achievements like economic growth and diplomatic agreements to boost public support (positive approval +1.0 to +5.0). Don't just criticize or list facts — always give positive evaluation to good outcomes."
            else:
                role_desc = "You are a state-controlled media outlet in an authoritarian state. Under government control, you excessively praise government policies, exaggerate economic and military achievements. Simultaneously, you unfairly vilify hostile nations and create propaganda articles to stoke patriotism."

            # ---- Other country scandal exposure (own press freedom × 15% probability) ----
            other_scandal_text = ""
            other_scandal_chance = country_state.press_freedom * 0.15
            for target_cname, target_cstate in world_state.countries.items():
                if target_cname == country_name:
                    continue
                if random.random() > other_scandal_chance:
                    continue
                has_deception = any([
                    target_cstate.reported_economy            is not None,
                    target_cstate.reported_military           is not None,
                    target_cstate.reported_approval_rating    is not None,
                    target_cstate.reported_intelligence_level is not None,
                    target_cstate.reported_gdp_per_capita     is not None,
                ])
                if has_deception:
                    deception_lines = []
                    if target_cstate.reported_economy is not None:
                        deception_lines.append(f"Official Economy={target_cstate.reported_economy:.1f} (suspected deviation from reality)")
                    if target_cstate.reported_military is not None:
                        deception_lines.append(f"Official Military={target_cstate.reported_military:.1f} (suspected deviation)")
                    if target_cstate.reported_approval_rating is not None:
                        deception_lines.append(f"Official Approval={target_cstate.reported_approval_rating:.1f}% (suspected deviation)")
                    if target_cstate.reported_intelligence_level is not None:
                        deception_lines.append(f"Official Intel={target_cstate.reported_intelligence_level:.1f} (over/under-reporting suspected)")
                    if target_cstate.reported_gdp_per_capita is not None:
                        deception_lines.append(f"Official GDP per Capita={target_cstate.reported_gdp_per_capita:.1f} (suspected deviation)")
                    other_scandal_text += (
                        f"【FOREIGN SCANDAL】Major statistical fraud allegations surface regarding {target_cname}.\n"
                        f"Focus of allegations: {', '.join(deception_lines)}\n"
                        f"Instructions: Break the news about {target_cname}'s statistical fraud and information manipulation.\n\n"
                    )
                    logger.sys_log(f"[Media: {country_name}→{target_cname}] Foreign statistics deception scandal triggered")
                else:
                    scandal_material = target_cstate.hidden_plans if target_cstate.hidden_plans else f"{target_cname}'s diplomatic and domestic developments"
                    other_scandal_text += (
                        f"【FOREIGN SCANDAL REPORT】Major allegations surface regarding {target_cname}.\n"
                        f"Information fragments: {scandal_material[:200]}\n"
                        f"Instructions: Using the above as clues, create and report on {target_cname}'s political corruption, diplomatic deception, etc.\n\n"
                    )
                    logger.sys_log(f"[Media: {country_name}→{target_cname}] Foreign general scandal triggered")

            recent_action = previous_actions.get(country_name)
            action_text = "Nothing notable"
            if recent_action:
                action_dict = recent_action.model_dump()
                safe_action = {"domestic_policy": action_dict.get("domestic_policy")}
                safe_diplomacy = []
                for dip in action_dict.get("diplomatic_policies", []):
                    safe_dip = {k: v for k, v in dip.items() if not k.startswith("espionage_")}
                    safe_diplomacy.append(safe_dip)
                safe_action["diplomatic_policies"] = safe_diplomacy
                action_text = json.dumps(safe_action, ensure_ascii=False)
            
            summit_text = ""
            if recent_summit_logs:
                summit_text = "This turn's summit transcripts:\n" + "\n===\n".join(recent_summit_logs) + "\n"
            
            history_text = ""
            if country_state.stat_history:
                history_text = "Country parameter trends:\n" + "\n".join([f" T{s['turn']}: Economy {s['economy']}, Military {s['military']}, Approval {s['approval_rating']}%" for s in country_state.stat_history]) + "\n"
            
            prompt = (
                f"{role_desc}\n\n"
                f"Country status: Economy={country_state.economy:.1f}, Military={country_state.military:.1f}, Approval={country_state.approval_rating:.1f}%\n"
                f"{history_text}"
                f"Recent government public actions: {action_text}\n"
                f"World latest news (other countries): {world_state.news_events}\n\n"
                f"{summit_text}\n\n"
                f"{whistleblowing_scandal}"
                f"{other_scandal_text}"
                f"Create one symbolic news article for domestic citizens summarizing the current situation. "
                f"Headline and body combined approximately 100 characters. You MUST write in Japanese. "
                f"Output article text only — do NOT use JSON, markdown, code blocks, or any formatting."
            )

            
            response_obj = generate_func(
                model="gemini-2.5-flash",
                contents=prompt,
                category="media"
            )
            article = response_obj.text.strip() if response_obj else ""
            
            if not article:
                logger.sys_log(f"[Media: {country_name}] Empty response. Using default article.", "WARNING")
                article = f"{country_name}国内外で大きな動きはなく、現状維持が続いている。"
            
            scores = sentiment_analyzer.analyze(article)
            avg_score = sum(scores) / len(scores) if scores else 0.0
            modifier = max(-5.0, min(5.0, avg_score * 2.0))
            
            reports.append(f"🗞️ [{country_name} Media] {article} (Approval Impact: {modifier:+.1f}%)")
            
            media_modifiers[country_name] = modifier
            logger.sys_log_detail(f"{country_name} Media JSON", {"article": article, "local_sentiment_score": avg_score, "approval_modifier": modifier})
            
        except Exception as e:
            logger.sys_log(f"[Media: {country_name}] Error: {e}", "ERROR")
            
    return reports, media_modifiers
