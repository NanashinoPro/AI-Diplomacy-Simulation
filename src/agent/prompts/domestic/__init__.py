"""Common policy section builder"""
from models import PresidentPolicy

def build_policy_section(policy: PresidentPolicy) -> str:
    lines = "\n".join(f"・{d}" for d in policy.directives)
    return f"\n【🏛️ Presidential Policy ({policy.stance})】\n{lines}\n\nYour task decisions must align with this policy.\n"
