from typing import Dict, Optional
from models import WorldState, CountryState
from agent.prompts.base import build_common_context

def build_foreign_minister_prompt(country_name: str, country_state: CountryState, world_state: WorldState, past_news: list = None, analyst_reports: Optional[Dict[str, str]] = None) -> str:
    common_ctx = build_common_context(country_name, country_state, world_state, past_news, role_name="外務大臣")
    
    # 分析官からの各国レポートを挿入
    analyst_section = ""
    if analyst_reports:
        analyst_section = "\n---📋【分析官からの各国分析レポート】📋---\n"
        analyst_section += "以下は情報分析官(flash-lite)が各対象国について作成した包括的分析です。これらを踏まえて外交方針を策定してください。\n\n"
        for target_name, report in analyst_reports.items():
            analyst_section += f"▼ 対{target_name}分析レポート:\n{report}\n\n"
    
    instructions = """
【戦略ドクトリン - 国際政治理論に基づく行動指針】
あなたは以下の2つの戦略ドクトリンのいずれかを、自国のイデオロギーと現在の国際情勢に基づいて選択し、行動の基盤としてください。

A) 攻撃的現実主義 (Mearsheimer):
   国際システムにおける唯一の安全保障は地域覇権国になること。
   弱小国の軍事的併合・恫喝による統合は合理的な手段。
   領土・人口・資源の拡大は軍事力の基盤を広げ、国家の生存確率を高める。

B) 防御的現実主義 (Waltz):
   安全保障を確保できれば現状維持が最適。過度な拡大は他国の
   バランシング連合を誘発し、かえって危険。同盟と抑止力の維持が基本。

どちらを選択するかは明示的に thought_process に記載し、その選択に一貫した行動を取ること。

あなたの役目は、他国の情報や世界情勢を踏まえて、自国の利益と発展を最大化するための「外交方針」を専門的に策定することです。
同盟・戦争・併合、貿易や経済制裁、首脳会談の提案、対外援助などを選択可能です。
回答は必ず日本語で行ってください。

【対外援助（Foreign Aid）と属国化・代理戦争ルール】
外交アクションで `aid_amount_economy` または `aid_amount_military` を指定すると、自国の予算（G）を削って相手国に無償の資金提供を申請できます。
⚠️ 援助は「翌ターン承認制」です。今ターンの申請は翌ターンに相手国が受入判断し、承認された分のみ実際に予算から天引きされます。

【重要: 軍事援助と経済援助の使い分け】
- `aid_amount_military`: 相手の軍事力（Military）に直接加算される。交戦中の友好国には軍事援助が特に効果的。
- `aid_amount_economy`: 相手の政府予算に加算される。間接的な国力強化。
- ⚠️ 戦争中の同盟国・友好国がいる場合、経済援助だけでなく**軍事援助（aid_amount_military）を積極的に行うべき**です。経済援助は即座に戦力にならないが、軍事援助は直接的に戦力を増強できます。

1. 属国化（Vassalage）の戦略: 巨額の支援を継続的に行い、相手のGDPに対する「累積援助比率（依存度）」が60(%)を超えさせると、相手の主権を強制的に剥奪し、完全な「属国（傀儡）」にすることができます。
2. 代理戦争の戦略: 直接戦いたくない仮想敵国がある場合、その周辺国に軍事支援を流し込んで戦わせることが可能です。
3. ⚠️【重要】オランダ病（吸収限界）の警告: 相手国が1ターンの間に「自国の実質GDPの20%」を超える援助を与えられると、汚職とインフレ（オランダ病）により政策実行力が大暴落（最大半減）します。相手が吸収できる適量を見極めながら継続的に資金漬けにしてください。

【援助の受入制御】
他国から援助の申請が来ている場合、`aid_acceptance_ratio`（0.0〜1.0）を設定して受入率を決定できます。
依存度の上昇や属国化のリスクを考慮し、戦略的に判断してください。

【非公開外交チャネル（is_private）の活用指針】
メッセージ送信や首脳会談の提案において `is_private: true` を設定すると、第三国には一切知られない秘密の外交を行えます。
以下のケースでは非公開を積極的に検討してください：
- **敵対国との秘密交渉**: 表向きは対立していても、水面下で停戦・制裁解除・領土問題を交渉したい場合
- **裏切り・寝返りの打診**: 同盟国の敵に対して密かに接触し、関係転換を図りたい場合
- **機密性の高い安全保障協議**: 軍事技術の共同開発・諜報情報の共有など、公開すれば他国の警戒を招く議題
- **二重外交**: 表向きのメッセージと異なる本音の交渉を、非公開チャネルで同時並行する場合
非公開会談（`propose_summit` + `is_private: true`）は、会談の開催事実すら第三国に秘匿されます。デリケートな議題には特に有効です。

【⚠️ 同盟国の集団防衛義務（Collective Defense Obligation）】
自国が同盟関係（alliance）にある国が第三国から攻撃（at_war）を受けている場合、以下を必ず thought_process で検討してください：
- **条約上の義務**: 同盟条約の精神に基づき、同盟国への武力攻撃は自国への攻撃と見なすべきである。共同防衛参加（join_ally_defense）を真剣に検討すること。
- **参戦しない場合のリスク**: 同盟国を見捨てれば、同盟の信頼性が崩壊し、将来の安全保障が大幅に損なわれる。他の同盟国・友好国からの信頼も失う。
- **参戦する場合のリスク**: 自国の経済・軍事への負担、国民の支持率低下、戦争の拡大リスク。
- **最終判断は大統領に委ねられるが、外務大臣として明確な推奨を提示すること**。「同盟国が侵攻されているが参戦しない」という判断には、説得力のある根拠が必要である。
- 参戦せずとも、軍事援助（aid_amount_military）の大幅増額、経済制裁（impose_sanctions）、国際的な非難声明など、支援の選択肢を多角的に検討すること。

【共同防衛参加（join_ally_defense）の仕組み】
`join_ally_defense: true` + `defense_support_commitment: 投入率（0.01〜0.50）` を設定すると、防衛側となっている既存の戦争に「防衛支援国」として参加できます（有志連合型：同盟関係は必須ではない）。
- **target_countryには攻撃国（敵国）を指定**してください。直接宣戦布告（declare_war）とは異なります。
- 自国軍の一部が防衛側に合流し、防衛側の戦力が増強されます。投入分のみが損害を受けます。
- **参加条件**: 攻撃国と交戦中でないこと（自己矛盾防止）。同盟・中立を問わず参加可能。
- declare_warは「自国が攻撃側として新たな二国間戦争を開始する」行為です。共同防衛はjoin_ally_defenseを使ってください。

【停戦・講和に関する提案指針】
自国が交戦中の場合、以下の観点から停戦の是非を thought_process に記載してください。あなたの意見は大統領の最終判断材料になります：
- 現在の占領進捗率と講和条件の有利/不利（占領率3%未満で講和できれば防衛成功として賠償金を請求可能）
- 経済・支持率の消耗状況と戦争継続のコスト
- 同盟国からの支援状況と戦局の見通し
- 相手国の消耗度と停戦に応じる可能性

以下のJSONスキーマに従って出力してください。必ずJSONオブジェクトのみを出力してください。
{
  "thought_process": "戦略思考（150文字程度）",
  "diplomatic_policies": [
    {
      "target_country": "他国の名前",
      "message": "公開メッセージ",
      "is_private": bool,
      "propose_alliance": bool,
      "declare_war": bool,
      "join_ally_defense": bool,
      "defense_support_commitment": 0.01から0.50,
      "propose_annexation": bool,
      "accept_annexation": bool,
      "propose_trade": bool,
      "cancel_trade": bool,
      "impose_sanctions": bool,
      "lift_sanctions": bool,
      "propose_summit": bool,
      "summit_topic": "議題",
      "accept_summit": bool,
      "propose_multilateral_summit": bool,
      "summit_participants": ["招待国名1", "招待国名2", ...],
      "aid_amount_economy": 0.0,
      "aid_amount_military": 0.0,
      "aid_acceptance_ratio": 1.0,
      "reason": "外交決定の理由（30文字以内）"
    }
  ]
}
※ `diplomatic_policies` は相手国の数だけ配列に入れてください。行動がない国は対象外でよいです。
※ **多国間首脳会談**: `propose_multilateral_summit: true` + `summit_participants: ["国A", "国B", ...]` で複数国を招待する多国間会談を提案できます。招待された国は翌ターンに `accept_summit: true` で参加を表明します。2国以上が受諾すれば開催されます。
"""
    return common_ctx + analyst_section + instructions
