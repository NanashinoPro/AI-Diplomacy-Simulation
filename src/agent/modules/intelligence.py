import json
import re
from typing import Tuple, Optional
from google.genai import types as genai_types
from logger import SimulationLogger

def generate_espionage_report(
    generate_func,
    logger: SimulationLogger,
    attacker_name: str, 
    target_name: str, 
    target_hidden_plans: str, 
    strategy: str
) -> Tuple[str, Optional[str]]:
    """Espionage agent: analyze classified information and generate report + SNS post"""
    logger.sys_log(f"[Intel: {attacker_name} -> {target_name}] Generating espionage report...")
    prompt = (
        f"You are an elite intelligence/covert operations agency.\n"
        f"Your operation ({strategy}) against target country '{target_name}' has succeeded.\n\n"
        f"【Acquired Target Country's Classified Plans (Raw Data)】\n{target_hidden_plans}\n\n"
        f"Output the following 2 items in JSON format.\n"
        f"1. report: Extract information matching what the leader needs, and write a 50-100 character secret briefing with analytical commentary.\n"
        f"2. sns_post: (As part of sabotage) An SNS post to infiltrate the target country's social media, criticizing the regime or spreading disinformation (max 140 chars). null if not applicable.\n\n"
        f"```json\n{{\n  \"report\": \"briefing text\",\n  \"sns_post\": \"SNS post text or null\"\n}}\n```\n"
        f"【IMPORTANT RULE】Write from an objective perspective without using the target country's internal information (subjective expressions). You MUST respond in Japanese."
    )
    try:
        response_obj = generate_func(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai_types.GenerateContentConfig(response_mime_type="application/json"),
            category="espionage"
        )
        response = response_obj.text.strip() if response_obj and hasattr(response_obj, 'text') else "{}"
        
        json_text = response
        match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if match:
            json_text = match.group(1)
        data = json.loads(json_text)
        
        report = data.get("report", "Analysis failed.")
        sns_post = data.get("sns_post")
        logger.sys_log_detail(f"Intel Report ({attacker_name} -> {target_name})", report)
        return report, sns_post
    except Exception as e:
        logger.sys_log(f"[Intel: {attacker_name}] Report generation error: {e}", "ERROR")
        return f"Intelligence on target country ({target_name}) was acquired but analysis failed.", None
