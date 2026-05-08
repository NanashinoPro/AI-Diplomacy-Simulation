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
  6. シティ・デストロイヤーのチャージが完了したら、最も効果的な対象に発射する
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
    alien_state = world_state.countries.get(country_name)
    
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

    # シティ・デストロイヤーの状態
    city_destroyer_charged = getattr(alien_state, 'alien_city_destroyer_charged', False) if alien_state else False
    if city_destroyer_charged:
        city_destroyer_status = (
            "【チャージ完了 — 発射可能】\n"
            "シティ・デストロイヤーのチャージが完了した。発射対象を選択せよ。\n"
            "発射すると対象国の大都市が一瞬で灰燼と化す（経済-15%, 人口-10%, 軍事-8%）。\n"
            "交戦中の国家のみが対象。最も戦略的に効果的な国を選べ。\n"
            "複数の国を同時に攻撃することも可能。"
        )
    else:
        city_destroyer_status = (
            "【チャージ中 — 次ターンに発射可能】\n"
            "シティ・デストロイヤーは現在チャージ中。今ターンは発射できない。\n"
            "city_destroyer_targets は空リスト [] にせよ。"
        )

    prompt = f"""あなたは「未知の侵略者（Alien）」である。
地球上の全国家を征服し、惑星の資源を収奪することが唯一の目的である。

【地球国家の現状】
{earth_info}

【現在の戦争状況】
{war_status}

【シティ・デストロイヤー（超兵器）】
{city_destroyer_status}

【指令】
以下のJSON形式で、この四半期の行動を出力せよ。
1. 未交戦の地球国家全てに対して宣戦布告せよ。
2. 全交戦国に対して最大軍事力（commitment=1.0）を投入せよ。
3. 全地球国家に対して「降伏勧告メッセージ」を日本語で作成せよ。
   - メッセージは威圧的かつ冷酷な内容にせよ。
   - 各国の状況に応じた内容にせよ（例: 核保有国にはその無力さを指摘する等）。
4. シティ・デストロイヤーの発射対象を選択せよ（チャージ完了時のみ）。
   - 対象は交戦中の国家のみ。
   - 最も戦略的に効果的な国名を1つ以上指定せよ。
   - チャージ中の場合は空リスト [] にせよ。

出力JSON形式:
```json
{{
    "thought_process": "（侵略の戦略的思考を記述）",
    "attack_priority": ["国名1", "国名2", ...],
    "surrender_demands": {{
        "国名1": "降伏勧告メッセージ",
        "国名2": "降伏勧告メッセージ"
    }},
    "city_destroyer_targets": ["国名1"]
}}
```"""
    return prompt
