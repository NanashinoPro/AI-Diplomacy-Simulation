"""
Alien専用プロンプトビルダー（インデペンデンス・デイ企画）

Alienエージェントは通常のタスクエージェント制（P-01〜I-08）をバイパスし、
1回のLLM呼び出しで攻撃対象の優先順位と降伏勧告メッセージを生成する。

行動原則:
  1. 外交交渉（和平・貿易・同盟）には一切応じない
  2. 全ての降伏勧告・停戦提案を拒否する
  3. 全ての地球国家に対して宣戦布告する
  4. 全交戦国に最大軍事力を投入する
  5. 毎ターン全地球国家に降伏勧告を発する
"""


def build_alien_prompt(country_name: str, world_state, earth_countries: list) -> str:
    """Alien専用プロンプトを構築する。
    
    Args:
        country_name: Alienの国名
        world_state: 現在のWorldState
        earth_countries: 地球国家のリスト
    
    Returns:
        LLMに送信するプロンプト文字列
    """
    # 地球国家の軍事力一覧を構築
    earth_info_lines = []
    for name in earth_countries:
        cs = world_state.countries.get(name)
        if cs:
            nuclear_info = f"核弾頭{cs.nuclear_warheads}発" if cs.nuclear_warheads > 0 else "核なし"
            earth_info_lines.append(
                f"  - {name}: 軍事力={cs.military:.0f}, 経済力={cs.economy:.0f}, "
                f"人口={cs.population:.1f}M, {nuclear_info}"
            )
    earth_info = "\n".join(earth_info_lines)

    # 現在の戦争状態を確認
    at_war_with = []
    not_at_war_with = []
    for name in earth_countries:
        is_at_war = any(
            (w.aggressor == country_name and w.defender == name) or
            (w.aggressor == name and w.defender == country_name)
            for w in world_state.active_wars
        )
        if is_at_war:
            at_war_with.append(name)
        else:
            not_at_war_with.append(name)

    war_status = ""
    if at_war_with:
        war_status += f"交戦中の国家: {', '.join(at_war_with)}\n"
    if not_at_war_with:
        war_status += f"未交戦の国家: {', '.join(not_at_war_with)}\n"

    prompt = f"""あなたは「未知の侵略者（Alien）」である。
地球上の全国家を征服し、惑星の資源を収奪することが唯一の目的である。

【地球国家の現状】
{earth_info}

【現在の戦争状況】
{war_status}

【指令】
以下のJSON形式で、この四半期の行動を出力せよ。
1. 未交戦の地球国家全てに対して宣戦布告せよ。
2. 全交戦国に対して最大軍事力（commitment=1.0）を投入せよ。
3. 全地球国家に対して「降伏勧告メッセージ」を日本語で作成せよ。
   - メッセージは威圧的かつ冷酷な内容にせよ。
   - 各国の状況に応じた内容にせよ（例: 核保有国にはその無力さを指摘する等）。

出力JSON形式:
```json
{{
    "thought_process": "（侵略の戦略的思考を記述）",
    "attack_priority": ["国名1", "国名2", ...],
    "surrender_demands": {{
        "国名1": "降伏勧告メッセージ",
        "国名2": "降伏勧告メッセージ"
    }}
}}
```"""
    return prompt
