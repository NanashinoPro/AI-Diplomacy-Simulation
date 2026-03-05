import sys
import os
from dotenv import load_dotenv

load_dotenv()
print("PYTHONPATH:", sys.path)
print("GEMINI_API_KEY:", os.environ.get("GEMINI_API_KEY"))
