"""
B-01: 予算配分エージェント（flash-lite）
各タスクエージェントが独立して要求した金額（B$）を集計し、
歳入情報を参照しつつ最終的な予算配分を確定する。
歳入を超過した場合は赤字国債（将来の利払い負担増）として自動処理される。
"""
from models import PresidentPolicy


def build_budget_normalize_prompt(
    country_name: str,
    policy: PresidentPolicy,
    request_military: float,
    request_intelligence: float,
    request_economy: float,
    request_welfare: float,
    request_education: float,
    government_budget: float,
    national_debt: float,
    economy: float,
) -> str:
    """
    B-01: 予算配分プロンプト（flash-lite）
    各タスクエージェントの要求金額（B$単位）を受け取り、最終的な配分金額を出力する。
    """
    total_request = (request_military + request_intelligence
                     + request_economy + request_welfare + request_education)
    deficit = max(0, total_request - government_budget)
    debt_ratio = national_debt / max(1.0, economy) * 100
    stance = policy.stance
    directives_str = "\n".join(f"・{d}" for d in policy.directives)

    return f"""あなたは「{country_name}」の予算配分担当官です。
各省庁の予算要求額（B$単位）を査定し、最終的な予算配分を確定してください。

【🏛️ 大統領施政方針（{stance}）】
{directives_str}

【💰 財政状況】
  歳入（税収+関税-利払い）: {government_budget:.1f} B$
  国家債務残高:               {national_debt:.1f} B$（対GDP比: {debt_ratio:.0f}%）

【各省庁の予算要求（B$単位）】
  軍事      request_military:     {request_military:.1f}
  諜報      request_intelligence: {request_intelligence:.1f}
  経済      request_economy:      {request_economy:.1f}
  福祉      request_welfare:      {request_welfare:.1f}
  教育      request_education:    {request_education:.1f}
  ────────────────────────────────────
  合計                             {total_request:.1f}
  差額                             {deficit:+.1f}（{'赤字' if deficit > 0 else '黒字'}）

【ルール】
- B$単位で出力。各値 ≥ 0.0。
- 歳入を超過した分 = 赤字国債を自動発行（将来の利払い負担が増加）。
- 歳入を下回った分 = 余剰金は債務返済に充当。
- 施政方針の優先順位を考慮してください。歳入の2倍を上限とします。

以下のJSONのみ出力してください（余分なテキスト不要）:
{{
  "budget_military": 0.0,
  "budget_intelligence": 0.0,
  "budget_economy": 0.0,
  "budget_welfare": 0.0,
  "budget_education": 0.0,
  "reasoning": "配分の根拠"
}}
"""
