import os
import json
import argparse
import glob
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

SIM_LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs", "simulations")

class SimulationSummary(BaseModel):
    summary: str = Field(description="A qualitative summary of each country's movements, strategic transitions, and major events throughout the simulation. Write in Markdown format.")

def generate_summary(log_filepath: str, force: bool = False) -> dict:
    """
    Read simulation JSONL log and generate summary via Gemini
    """
    if not os.path.exists(log_filepath):
        print(f"File not found: {log_filepath}")
        return

    summary_filepath = log_filepath.replace(".jsonl", ".summary.json")
    
    # Skip if summary already exists
    if not force and os.path.exists(summary_filepath):
        print(f"Summary already exists for {log_filepath}")
        return None

    print(f"Generating summary for {log_filepath}...")
    
    turns = []
    with open(log_filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    turns.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if not turns:
        print("No valid turn data found.")
        return

    # Extract data for summary prompt
    # Sending all text may be too long, but ~80 turns fits well within Gemini 2.5 Flash context window
    # Elements to extract: turn count, country status changes, news events, agent thought processes
    
    prompt_text = "The following is an execution log of an AI agent inter-state diplomacy/domestic policy simulation.\n"
    prompt_text += "Each turn records each country's thought processes and major events (news events) in chronological order.\n\n"
    prompt_text += "【Instructions】\n"
    prompt_text += "Analyze how each country strategized and acted throughout the simulation, and create a comprehensive qualitative summary.\n"
    prompt_text += "Include:\n"
    prompt_text += "- Each country's initial strategy and any mid-course strategic changes\n"
    prompt_text += "- Major conflicts, cooperation, and intelligence operation results\n"
    prompt_text += "- Final outcomes and situation\n"
    prompt_text += "Write in clear Markdown format text. You MUST respond in Japanese.\n\n"
    
    prompt_text += "【Simulation Log】\n"
    
    for t in turns:
        turn_num = t.get("turn")
        year = t.get("world_state", {}).get("year", t.get("state", {}).get("year"))
        quarter = t.get("world_state", {}).get("quarter", t.get("state", {}).get("quarter"))
        
        prompt_text += f"\n--- Turn {turn_num} ({year} Q{quarter}) ---\n"
        
        news = t.get("world_state", {}).get("news_events", t.get("state", {}).get("news_events", []))
        if news:
            prompt_text += "📰 News/Events:\n"
            for n in news:
                prompt_text += f"  - {n}\n"
                
        actions = t.get("actions", {})
        for country_name, action_data in actions.items():
            thought = action_data.get("thought_process", "")
            if thought:
                prompt_text += f"🧠 {country_name}'s thinking: {thought}\n"

    # Gemini API call
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set.")
        return

    client = genai.Client(api_key=api_key)
    
    def _call_generate(target_client):
        """Execute API call with specified client"""
        return target_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_text,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SimulationSummary,
                temperature=0.4
            ),
        )
    
    try:
        try:
            response = _call_generate(client)
        except Exception as main_error:
            sub_key = os.environ.get("GEMINI_API_KEY_SUB")
            if not sub_key:
                raise
            print(f"⚠️ Main API key error: {main_error}. Retrying with sub API key...")
            client_sub = genai.Client(api_key=sub_key)
            response = _call_generate(client_sub)
            print("✅ Sub API key call succeeded.")
        
        # Save
        summary_data = json.loads(response.text)
        with open(summary_filepath, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully generated summary and saved to {summary_filepath}")
        
        # Return token usage
        usage = response.usage_metadata
        return {
            "summary": summary_data.get("summary", ""),
            "usage": {
                "prompt_tokens": usage.prompt_token_count if usage else 0,
                "candidates_token_count": usage.candidates_token_count if usage else 0,
                "thoughts_token_count": getattr(usage, 'thoughts_token_count', 0) or 0
            }
        }
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate summary for simulation logs.")
    parser.add_argument("--all", action="store_true", help="Generate summary for all logs in logs/simulations/")
    parser.add_argument("--file", type=str, help="Generate summary for a specific log file")
    parser.add_argument("--force", action="store_true", help="Force regenerate summary even if it exists")
    
    args = parser.parse_args()
    
    if args.all:
        if os.path.exists(SIM_LOG_DIR):
            for filename in os.listdir(SIM_LOG_DIR):
                if filename.endswith(".jsonl"):
                    filepath = os.path.join(SIM_LOG_DIR, filename)
                    generate_summary(filepath, force=args.force)
    elif args.file:
        generate_summary(args.file, force=args.force)
    else:
        print("Please specify --all or --file <filename>")
