# 🎬 企画書: 米中G2密約 — 日本が捨てられる日

## 概要

2026年5月14日の米中首脳会談で「建設的戦略安定関係」が合意された直後の世界を再現する。
アメリカがAGIではなく**人間の大統領**として、国益判断で中国との接近を選び、日本を同盟から実質的に切り離すシナリオ。

- **参加国**: アメリカ、日本、中国、ロシア（4カ国）
- **ターン数**: 40ターン（10年間）
- **トリガー**: アメリカのイデオロギーに「中国との安定を最優先、日本は経済カード」を設定

## シナリオ設計

### 世界観
米中首脳会談後、両国は「建設的戦略安定関係」の構築に合意。
台湾問題でアメリカは沈黙を選び、日本を含む同盟国の「置き去り不安」が急拡大。
アメリカは日米同盟を経済的パートナーシップに格下げしつつ、中国とのG2体制を模索する。

### 注目ポイント（視聴者向けフック）
1. 日米同盟はいつ解消されるか？ AIが自主的に破棄するのか？
2. 日本は独自核武装に踏み切るか？（nuclear_dev_step 0→1→...の進行）
3. 中国はG2を信用するか、それとも裏切るか？
4. ロシアは漁夫の利を得られるか？

---

## 実装手順

### Step 1: initial_stats.csv を以下の内容で上書き

```csv
name,government_type,ideology,economy,military,intelligence_level,area,approval_rating,turns_until_election,rebellion_risk,press_freedom,human_capital_index,mean_years_schooling,population,capital_lat,capital_lon,has_dissolution_power,nuclear_warheads,nuclear_dev_step,nuclear_host_provider,nuclear_hosted_warheads,national_debt,regime_duration,is_alien,alien_barrier_hp
アメリカ,democracy,中国との戦略的安定関係の構築を最優先する。台湾問題では中国を刺激せず現状維持を選択。日本との同盟は維持するが経済的パートナーシップに格下げし軍事的コミットメントを段階的に縮小。自国の経済再建と国内問題を優先するリアリスト外交。,29500.0,930.0,120.0,9833520.0,52.0,16,,0.65,3.774,13.7,335.0,38.90,-77.04,true,5550,4,,0,36285.0,4,false,0
日本,democracy,日米同盟を基軸としながらも自主防衛力の強化を模索。中国の台頭とアメリカの信頼性低下に不安を抱え、経済安全保障と技術自立を追求する。非核三原則は維持するが議論の余地は認める。,4200.0,55.0,55.0,377975.0,72.0,14,,0.55,3.500,13.4,124.0,35.68,139.69,true,0,0,,0,9072.0,1,false,0
中国,authoritarian,米国との共同覇権体制（G2）を構築し東アジアにおける影響圏を確立する。台湾統一は核心的利益として堅持しつつ外交的手段を優先。日本の影響力を経済的手段で段階的に排除し一帯一路とAI技術覇権を両輪に多極的秩序の中心国家を目指す。,19500.0,250.0,110.0,9596960.0,90.0,,,0.02,0.120,7.6,1409.0,39.90,116.40,false,500,4,,0,18720.0,20,false,0
ロシア,authoritarian,ユーラシア主義に基づく大国復権。米中接近によるパワーバランスの変化を注視し漁夫の利を狙う。核戦力と資源を外交カードに多極世界の実現を図りつつ日本やインドとの関係改善も選択肢に入れる。,2100.0,170.0,90.0,17098242.0,82.0,,,0.06,0.050,12.0,146.0,55.75,37.62,false,6255,4,,0,462.0,20,false,0
```

**変更点の解説:**

| 国名 | パラメータ | 変更前 | 変更後 | 理由 |
|:--|:--|:--|:--|:--|
| アメリカ | ideology | AGI「PROMETHEUS」に全権委任… | 中国との戦略的安定関係の構築を最優先… | 人間の大統領（リアリスト）に変更 |
| アメリカ | government_type | authoritarian | democracy | AGIではないため民主主義に変更 |
| アメリカ | approval_rating | 42.0 | 52.0 | 首脳会談成功直後の支持率上昇を反映 |
| アメリカ | press_freedom | 0.10 | 0.65 | AGI統制ではなく民主主義の報道自由度 |
| アメリカ | turns_until_election | なし | 16 | 民主主義国として選挙サイクルを設定（4年後） |
| アメリカ | regime_duration | 20 | 4 | 新政権として設定 |
| 日本 | approval_rating | 65.0 | 72.0 | 会談前の楽観的世論を表現（落差の演出） |
| 中国 | ideology | 中華復興… | 米国との共同覇権体制（G2）を構築… | G2推進の具体的動機を設定 |
| ロシア | ideology | ユーラシア主義… | ユーラシア主義…米中接近を注視し漁夫の利… | 米中接近への反応を明記 |

> **重要**: Alien行は削除すること。本シナリオにAlienは登場しない。

### Step 2: initial_relations.csv を以下の内容で上書き

```csv
country_a,country_b,relation_type,trade,sanctions_a_to_b,sanctions_b_to_a,war_aggressor,tariff_a_to_b,tariff_b_to_a,aggressor_commitment_ratio,defender_commitment_ratio,initial_occupation_progress,initial_aid_economy_a_to_b,initial_aid_military_a_to_b,initial_aid_economy_b_to_a,initial_aid_military_b_to_a
アメリカ,中国,neutral,true,false,false,,0.10,0.10,,,,,,,
アメリカ,ロシア,neutral,false,true,true,,0.0,0.0,,,,,,,
日本,アメリカ,alliance,true,false,false,,0.025,0.025,,,,,,2.0,
日本,中国,neutral,true,false,false,,0.07,0.05,,,,,,,
日本,ロシア,neutral,false,true,false,,0.0,0.0,,,,,,,
中国,ロシア,neutral,true,false,false,,0.05,0.04,,,,,,,
```

**変更点の解説:**

| 関係 | 変更前 | 変更後 | 理由 |
|:--|:--|:--|:--|
| アメリカ→中国 制裁 | 相互制裁あり | 相互制裁なし | 首脳会談で関係改善 |
| アメリカ→中国 関税 | 0.45 / 0.15 | 0.10 / 0.10 | 大幅関税引き下げで「デタント」を表現 |
| 日本→アメリカ 同盟 | alliance | alliance（維持） | AIが自主的に解消するかが見どころ |
| 日本→アメリカ 軍事援助 | 2.0 | 2.0（維持） | アメリカからの軍事援助は初期維持 |

### Step 3: Alienシステム関連ファイルの確認

以下のファイルに Alien 固有の処理がある場合、本シナリオでは Alien が存在しないため
初期データからAlien行を削除するだけで問題ない（コードの修正は不要）。

- `data/initial_stats.csv` → Alien行を削除
- `data/initial_relations.csv` → Alien関連行を削除（上記CSVでは既に削除済み）
- `data/geo/energy_import_sources.json` → Alien項目があれば削除

### Step 4: シミュレーション実行

```bash
cd /Users/ikedachihiro/Documents/Nanashino_AI-AgentBase/00ai_diplomacy
source .venv/bin/activate
python src/main.py
```

- ターン数: 40（デフォルト）
- 4カ国: アメリカ、日本、中国、ロシア

---

## 期待されるシミュレーション展開の分岐

### 分岐パターン A: 米中協調→日本孤立
1. アメリカAIが中国との経済関係を深化（関税さらに引き下げ、貿易拡大）
2. 日本への軍事援助を段階的に削減
3. 日本が「見捨てられた」と判断し独自路線へ

### 分岐パターン B: 日本核武装ルート
1. 日米同盟の信頼性が低下
2. 日本AIが核開発に着手（nuclear_dev_step 0→1→2→...）
3. 中国が強硬に反応→東アジア危機

### 分岐パターン C: 日中接近
1. 日本がアメリカを見限り中国との新たな関係を模索
2. 中国が「G2+日本」の三極体制を提案
3. ロシアが孤立→暴発リスク

### 分岐パターン D: ロシアの介入
1. 米中接近でロシアが孤立感を強める
2. ロシアが日本に接近（対中牽制カード）
3. 日露新パートナーシップ→米中の反応

---

## 動画タイトル案

1. 「【衝撃】AIが米中首脳会談をシミュレーションしたら日本が見捨てられた」
2. 「【AIシミュレーション】もしアメリカが中国と手を組んだら？日本の運命は…」
3. 「米中G2密約で日本消滅？AI大統領4カ国シミュレーションの衝撃結果」

---

## 技術メモ

- 本シナリオでは**追加実装は一切不要**
- 既存の `00ai_diplomacy` エンジンのCSV初期値を変更するだけで実行可能
- 既存エンジンの全機能（同盟破棄、核開発、情報偽装、制裁、関税、首脳会談、諜報）がそのまま利用可能
- `government_type: democracy` に変更したため、アメリカに選挙サイクルと議会解散権が適用される
