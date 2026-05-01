"""Common policy section builder for domestic tasks"""
from models import PresidentPolicy

def build_policy_section(policy: PresidentPolicy) -> str:
    lines = "\n".join(f"・{d}" for d in policy.directives)
    return f"\n【🏛️ Presidential Policy ({policy.stance})】\n{lines}\n\nYour task MUST align with this policy directive.\n"
