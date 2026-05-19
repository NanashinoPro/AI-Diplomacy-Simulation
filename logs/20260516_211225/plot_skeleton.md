# Plot Skeleton: 20260516_211225

## Core Theme & Core Question

- **Core Theme**: 「AIが軍隊を地図の上に配備したら、"見えない戦争"が始まった ── v2の緊張度メカニクスが生んだ、砲火なき台湾海峡危機」
- **Core Question**: 「AIに軍事配備の自由を与えたとき、戦争なしでどこまで緊張がエスカレートし、各国の運命はどう変わるのか？」

---

## Narrative Axes

1. **「目と手足」の進化軸** — v2でAIが獲得した「戦略マップ」と「軍事配備の自由」が、v1とは根本的に異なる戦略空間を生み出す過程。地図上に軍隊アイコンが初めて出現し、配備ミッション（intimidation / show_of_force / patrol）によって「意思の可視化」が実現した進化を追う
2. **「砲火なき戦争」軸** — 緊張度メカニクス（4段階）によって、宣戦布告なしでも「見えない戦争」が進行する構造。中国のintimidationがRally効果で自国支持率を上昇させるパラドックス。脅せば脅すほど相手が強くなるジレンマの深化
3. **「軍拡の代償」軸** — Richardsonモデルが予測する「経済的疲弊」が中国の国家債務1,187%として顕在化する過程。軍事力の増強が経済を蝕み、最終的に持続不可能な構造に至るまでのカウントダウン

---

## Academic Discussion Framework

### Concept 1: Richardson Arms Race Model（リチャードソン軍拡競争モデル）

- **Demonstrating Event**: 中国の国家債務 16.8% → 50.4% → 471.3% → 1,187.7%。軍事+諜報に歳入の60%超を集中投入（Turn 2: 460/1,533B$）し、福祉・教育予算をゼロにした結果
- **Layer 1 — AI Causal Mechanism**: 制約条件=「アメリカの軍事力846.8に対し中国233.4」→ 3.6倍の軍事格差を埋めるため軍事予算を最大化 → しかしARCHITECTURE.mdの「軍事維持コスト = 軍事負担率の二乗に比例する疲弊係数」により、投入するほど維持コストが加速的に増大 → 国家債務が指数関数的に爆発
- **Layer 2 — Comparison**: Richardson (1960) *Arms and Insecurity* の dx/dt = ky - ax + g における疲弊係数 -ax。aが低い（＝経済的ブレーキが弱い）場合、軍拡は暴走し「不安定均衡」に向かう。中国AIの行動はa（疲弊への感度）が極めて低い状態をシミュレート
- **Historical Parallel**: 冷戦期ソ連の崩壊（軍事費GDP比10-25%を維持、民生部門への投資が枯渇し1991年に体制崩壊）。ソ連はSDI（戦略防衛構想）への対抗で軍事支出が加速、経済停滞と複合して体制維持が不可能に

### Concept 2: Rally 'round the Flag Effect（旗の下に結集する効果）

- **Demonstrating Event**: 中国の支持率 47.6% → 54.2% → 56.9%。アメリカのshow_of_force配備が「外部脅威」として中国国内のナショナリズムを刺激し、支持率が上昇
- **Layer 1 — AI Causal Mechanism**: 制約条件=「ARCHITECTURE §4.4.3: 緊張度レベル中(100-300) → Rally効果 +1〜+3%/ターン」→ アメリカが中国方面にshow_of_force(100-150B$)を配備 → 緊張度スコアが「中」に到達 → 中国国内で自動的にRally効果が発動 → 皮肉にもintimidationの対象であるはずの中国の政権が安定化
- **Layer 2 — Comparison**: Mueller (1970) "Presidential Popularity from Truman to Johnson" — 国際危機における指導者支持率の短期急上昇。Mueller は3条件（国際的・大統領直接関与・劇的）を定義。Fearon (1994) のaudience cost理論と組み合わせると、民主主義国のshow_of_forceが権威主義国への「無料の正統性供給」となる逆説が浮上
- **Historical Parallel**: 9/11後のブッシュ大統領支持率51% → 90%（歴代最大の上昇幅）。イラン・イスラム革命後のカーター大統領支持率急騰。いずれも外部脅威が国内結束を生んだ事例

---

## Scene Breakdown

### Scene 1: hook_01
- **type**: hook
- **layout**: `fullscreen_strategy_map_zoom`
- **duration**: 20-25秒
- **content_summary**: 最終ターンの戦略マップを映し出し、東アジア全域に展開された軍事ユニットの映像で視覚的インパクトを与える。中国の国家債務1,187%のカウンターが回り、「一発も弾を撃たずに、AIの戦争は既に始まっていた」と宣言
- **key_data**: 中国国家債務 1,187.7%、4カ国の軍事配備状況（Turn 5マップ）
- **bgm**: 残滓念.mp3
- **se**: 爆発3.mp3 (scene_start) / 和太鼓でドドン.mp3 (line_start, 債務数値表示時)
- **pull_question**: 「なぜAIは戦争を選ばなかったのに、こんな結末になったのか？」
- **hook_material_source**: [WF1.1 §7 Candidate #3: Rally効果の逆説的発動 (Sランク)] + [Candidate #5: 中国の国家債務1,187.7% (Sランク)] — 2つのSランク素材を複合使用
- **hook_selection_rationale**: Candidate #3（Rally効果）は「脅せば脅すほど相手が強くなる」という知的パラドックスで視聴者の好奇心を刺激し、Candidate #5（債務1,187%）は衝撃的な数値で視覚的インパクトを生む。両者はCausal Chain 1→2で因果接続されており、「なぜこうなった？」という強力なフックを構成する。企画書Sランク「緊張度メカニクス」に直結
- **visual_direction**: *Numerically-driven* + *Visually-driven* 複合型 — 戦略マップの映像美と1,187%の巨大数値表示で二重のインパクト
- **visual_direction_detail**: Turn 5の戦略マップをフルスクリーンで表示。東アジア全域に赤（中国）・青（アメリカ）・白（日本）・緑（台湾）の軍事ユニットが展開された状態。画面右下に国家債務カウンターがリアルタイムで回転し、1,187.7%で停止
- **opening_screen_design**: ダークテーマの戦略マップ（東アジア全域）がフェードインで表示。軍事ユニットアイコンが次々と点灯。画面中央下に「2027年 春 — 最終ターン」のテキスト。SE「爆発3」で債務カウンター起動

### Scene 2: intro_01
- **type**: intro
- **layout**: `channel_intro_with_v2_showcase`
- **duration**: 45-60秒
- **content_summary**: 「名無之ずんだもんチャンネルへようこそなのだ」から始まり、v2の三大アップデート（戦略マップ・戦術配備・緊張度）を映像付きで紹介。2026年現在の台湾海峡情勢（Reality Map: 中国A2/AD強化、日米台半導体MOU）を事実として提示し、「AIにこの状況を任せたらどうなるか」という問いを設定
- **key_data**: 参加国4カ国（アメリカ・中国・日本・台湾）、全5ターン（2026年第1四半期〜2027年第2四半期、四半期ごと）、初期条件は2026年現実データ（GDP・軍事力・人口・同盟関係は実在の公開統計に基づく）
- **mandatory_intro_items**:
  - **参加国**: アメリカ、中国、日本、台湾（4カ国）
  - **シミュレーション期間+粒度**: 全5ターン、1ターン = 1四半期（2026年Q1〜2027年Q2）
  - **初期条件根拠**: 各国GDP（世界銀行/IMF）、軍事力（SIPRI/各国防衛白書）、人口（UN推計）、同盟関係（外務省公式）に基づく2026年現実データ
- **bgm**: パステルハウス.mp3
- **se**: 決定ボタンを押す4.mp3 (line_start, 挨拶時)
- **pull_question**: 「v2でAIが『目と手足』を手に入れたら何が起きる？」

### Scene 3: event_01 — 「電撃同盟と最初の配備」
- **type**: event
- **layout**: `strategy_map_deployment_reveal`
- **duration**: 3分00秒
- **content_summary**: Turn 1の展開。アメリカAIと台湾AIが開始直後に軍事同盟を電撃締結。**戦略マップ上に初めて軍隊ユニットが出現する瞬間**を演出。アメリカは中国方面にshow_of_force(150B$)、台湾方面に航空制空(100B$)を配備。同時に中国は台湾方面にintimidation(50B$)+show_of_force(80B$)を配備。3層エージェント（分析官→防衛大臣→大統領）の意思決定チェーンを紹介
- **key_data**: 米台同盟締結、アメリカ配備(中国方面 show_of_force 150B$, 台湾方面 航空制空 100B$)、中国配備(台湾方面 intimidation 50B$ + show_of_force 80B$ + 航空制空 70B$)、3層エージェント構造
- **bgm**: 追跡者.mp3
- **se**: きらきら輝く3.mp3 (line_end, 同盟締結時) / 和太鼓でドドン.mp3 (line_start, 中国intimidation配備時)
- **pull_question**: 「中国AIは台湾方面にintimidation配備を選んだ。その裏に何がある？」

### Scene 4: analysis_01 — 「緊張度メカニクスの解剖」
- **type**: analysis
- **layout**: `data_dashboard_tension_meter`
- **duration**: 3分00秒
- **content_summary**: v2の核心機能「緊張度メカニクス」を深掘り解説。Mueller/Schultz/Fearonの学術理論に基づく4段階（低/中/高/極高）の仕組みを図解。配備ミッション（patrol < show_of_force < intimidation）が緊張度スコアにどう影響するかをデータ付きで示す。Rally 'round the flag効果の発動条件を説明 — 「アメリカが中国方面にshow_of_forceを送るたびに、中国の支持率が上がる」という逆説を提示。中国の支持率推移 47.6% → 54.2% → 56.9% をグラフで可視化
- **key_data**: 緊張度4段階の閾値（低0-100/中100-300/高300-500/極高500+）、Rally効果 +1〜+3%/ターン、中国支持率推移グラフ、配備ミッション別の緊張度影響度
- **bgm**: ブルーボトル.mp3
- **se**: PC-Keyboard06-02(Hard).mp3 (line_start, データ表示時) / ひらめく1.mp3 (line_start, Rally効果の逆説提示時)
- **pull_question**: 「脅せば脅すほど相手が強くなる。ではどうすれば良かったのか？」

### Scene 5: event_02 — 「見えない戦線の拡大」
- **type**: event
- **layout**: `split_screen_map_evolution`
- **duration**: 3分00秒
- **content_summary**: Turn 2-4の展開を「配備の進化」として地図ベースで追跡。中国AIが台湾方面のintimidation+show_of_forceを維持しつつ、**Turn 4で日本方面にもshow_of_force(40B$)を新規展開**する瞬間を重点的に演出。マップ上で中国の軍事プレゼンスが東アジア全域に広がる視覚的インパクト。日本AIの堅実な対応（海軍patrol 15B$、偵察飛行 5B$の控えめな配備）との対比。日米台多国間首脳会談（ラウンドロビン方式）の実施。中国の予算配分（軍事230B$ + 諜報230B$、福祉・教育ゼロ）の異常性を数字で示す
- **key_data**: Turn 4 中国→日本方面show_of_force 40B$新規展開、中国予算配分(軍事230B$+諜報230B$/歳入1,533B$)、日本の控えめ配備(patrol 15B$)、多国間首脳会談の実施
- **bgm**: 10℃.mp3 → Decisive_Battle.mp3（Turn4の戦線拡大時に切替）
- **se**: Warning-Siren05-01(Fast-Mid).mp3 (line_start, 日本方面配備検出時) / 和太鼓でドドン.mp3 (line_start, 戦線拡大のインパクト)
- **pull_question**: 「中国はなぜ日本方面にまで軍を送ったのか？そしてその代償は？」

### Scene 6: analysis_02 — 「債務爆発と軍拡のカウントダウン」
- **type**: analysis
- **layout**: `breaking_news_debt_explosion`
- **duration**: 3分00秒
- **content_summary**: Turn 5の最終局面。中国の国家債務が1,187.7%に到達する「破滅的数字」を、リアルタイムカウンターで演出。Richardsonモデルの疲弊係数（-ax項）を解説し、「軍事負担率の二乗に比例してコストが加速する」仕組みを図解。一方で日本の支持率V字回復（37.2% → 50.6%）と台湾のGDP +41.0%成長を対比。「経済優先の日本」vs「軍拡優先の中国」のコントラスト。情報偽装（支持率85%と偽装報告）と諜報戦の結果も紹介
- **key_data**: 中国国家債務推移(16.8→50.4→471.3→1,187.7%)、日本支持率推移(37.2→50.6%)、台湾GDP推移(804→1,134B$, +41.0%)、情報偽装（支持率85%偽装）
- **bgm**: 残滓念.mp3
- **se**: 爆発3.mp3 (line_start, 債務1,187%表示時) / チーン1.mp3 (line_end, 偽装発覚時)
- **pull_question**: 「AIに軍拡を任せた結果がこれ。では、この構造は現実世界でも起きうるのか？」

### Scene 7: summary_01 — 「学術的総括」
- **type**: summary
- **layout**: `academic_analysis_board`
- **duration**: 2分00秒
- **content_summary**: 2つの学術概念を2層構造で深堀り。①Richardsonモデル：AIは意図的にモデルを参照していないが、制約条件下の最適化が「軍拡→疲弊→持続不可能」のパターンを再現。冷戦期ソ連との比較。②Rally効果：show_of_forceが権威主義国に「無料の正統性」を供給する逆説。Mueller (1970) の3条件が全て満たされている。9/11後のブッシュ支持率との比較。「AIが理論を知らなくても、構造が同じなら同じパターンが生まれる」という示唆
- **key_data**: Richardson方程式 dx/dt = ky - ax + g、Mueller Rally 3条件、ソ連の軍事費GDP比10-25%、9/11後の支持率90%
- **bgm**: 2_23_AM.mp3（落ち着き・知的・ジャズ — 学術的総括にふさわしい冷静なトーン）
- **se**: PC-Keyboard06-02(Hard).mp3 (line_start, 方程式表示時) / ひらめく1.mp3 (line_start, 学術的示唆の提示時)
- **pull_question**: なし（まとめのため）

### Scene 8: ending_01
- **type**: ending
- **layout**: `character_closeup_with_map_bg`
- **duration**: 30秒
- **content_summary**: 「今回のシミュレーションでは一発も弾は撃たれなかった。でもAIたちは確かに"戦争"をしていた」と締め。チャンネル登録・高評価CTA。次回予告
- **key_data**: なし
- **bgm**: 野良猫は宇宙を目指した.mp3
- **se**: きらきら輝く3.mp3 (scene_start)
- **pull_question**: なし

---

## Viewer Knowledge Inventory

| Scene | Prior Concepts | New Concepts | Foreshadow-Then-Explain |
|:--|:--|:--|:--|
| hook_01 | なし | 国家債務GDP比（借金の規模を示す指標）、戦略マップ（地図上にAIの軍事配備が表示されるv2の新機能） | [国家債務の「なぜ」→ analysis_02で詳細解説] / [戦略マップの仕組み → intro_01で詳細紹介] ※hookでは「1,187%」という数値と地図の映像で最低限の文脈を提示 |
| intro_01 | 国家債務（概念のみ）、戦略マップ（映像のみ） | v2三大アップデート概要（戦略マップ・戦術配備・緊張度）、2026年台湾海峡の現実情勢（A2/AD、半導体MOU）、AIエージェントの基本構造 | [緊張度メカニクスの詳細 → analysis_01で解説] ※introでは「緊張度という仕組みがある」と最低限の文脈を提示 |
| event_01 | v2アップデート概要、現実情勢、AIエージェント基本構造 | 軍事同盟の締結プロセス、配備ミッションの種類（intimidation / show_of_force / patrol）、3層エージェント（分析官→防衛大臣→大統領）の意思決定チェーン | [配備ミッションが緊張度に与える影響 → analysis_01で即座に解説] ※event_01では「intimidationという配備がある」と紹介し、次シーンで効果を解説 |
| analysis_01 | 配備ミッション、3層エージェント | 緊張度メカニクス（4段階: 低/中/高/極高）、Rally 'round the flag効果（外部脅威で支持率が上がる現象）、Mueller/Schultz/Fearon理論の概要 | [Rally効果の累積的結果 → event_02・analysis_02で展開] ※analysis_01で「+3%/ターン」の仕組みを説明済み |
| event_02 | 緊張度、Rally効果、配備ミッション | 戦線の自律的拡大（AIが独自に配備方面を追加）、多国間首脳会談（ラウンドロビン方式）、予算配分の異常性（軍事+諜報で歳入の60%超） | [予算異常性の帰結（債務爆発）→ analysis_02で即座に解説] |
| analysis_02 | 戦線拡大、予算配分、Rally効果 | Richardson軍拡競争モデル（疲弊係数）、国家債務の指数関数的膨張メカニズム、情報偽装（支持率の偽装報告）と諜報戦 | N/A（全て当シーン内で完結） |
| summary_01 | Richardson模型、Rally効果、全シミュレーションデータ | 冷戦期ソ連との歴史的並行、9/11後の支持率急騰との並行、「構造が同じなら同じパターンが生まれる」という示唆 | N/A |
| ending_01 | 全概念を既知 | なし（まとめ・CTA） | N/A |

---

## Estimated Total Duration

| Scene | Duration |
|:--|:--|
| hook_01 | 25秒 |
| intro_01 | 55秒 |
| event_01 | 3分00秒 |
| analysis_01 | 3分00秒 |
| event_02 | 3分00秒 |
| analysis_02 | 3分00秒 |
| summary_01 | 2分00秒 |
| ending_01 | 30秒 |
| **合計** | **約15分50秒** ✅（目標: 15-20分以内） |

---

## Pattern Interrupt Schedule

| Time | Interrupt Type | Details |
|:--|:--|:--|
| 0:25 | Scene transition | hook → intro（BGM大幅変化: 残滓念→パステルハウス） |
| 1:20 | Scene transition | intro → event_01（戦略マップ初登場のビジュアルインパクト） |
| 3:00 | Layout change | event_01内でのマップ初表示→配備ユニット出現アニメーション |
| 4:20 | Scene transition | event_01 → analysis_01（分析モードへ切替、BGM: 追跡者→ブルーボトル） |
| 6:00 | Data reveal | analysis_01内でRally効果のグラフ表示 + SE「ひらめく1」 |
| 7:20 | Scene transition | analysis_01 → event_02（BGM: ブルーボトル→10℃） |
| 8:30 | BGM switch + SE | event_02内でTurn4戦線拡大時にBGM切替(10℃→Decisive_Battle) + Warning Siren SE |
| 10:20 | Scene transition | event_02 → analysis_02（BGM: Decisive_Battle→残滓念） |
| 11:30 | Data explosion | analysis_02内で債務カウンター1,187%表示 + 爆発SE |
| 12:00 | Comedy beat | analysis_02内で偽装発覚 + チーンSE |
| 13:20 | Scene transition | analysis_02 → summary_01（BGM大幅変化: 残滓念→2_23_AM） |
| 15:20 | Scene transition | summary_01 → ending_01（BGM: 2_23_AM→野良猫は宇宙を目指した） |

※ 最長の連続解説区間は約3分00秒（各analysis/eventシーン）。ワークフロー要件の「≤3分」を遵守。

---

## Final Checklist

- [x] All scenes align with Core Question（「AIに軍事配備の自由を与えたとき〜」）and Narrative Axes（3軸）
- [x] Scene structure: hook → intro → event/analysis → summary → ending
- [x] Intro starts with「名無之ずんだもんチャンネルへようこそなのだ」
- [x] Intro includes: participating countries (4カ国), simulation period/granularity (5ターン/四半期), initial conditions basis (2026年現実データ)
- [x] Viewer Knowledge Inventory complete; no unexplained concept references
- [x] All foreshadow-then-explain: minimal context in same scene, explanation in next scene, recorded in inventory
- [x] Academic Framework: 2 concepts (Richardson / Rally) with 2-layer structure (emergence → comparison) + historical parallels
- [x] Pattern interrupts every ≤3 min of exposition
- [x] Hook: material rationale (ref WF1.1 §7 #3+#5), visual direction declared (numerically+visually-driven), opening screen specified
- [x] All BGM filenames exist in bgm_database.json ✅（残滓念, パステルハウス, 追跡者, ブルーボトル, 10℃, Decisive_Battle, 2_23_AM, 野良猫は宇宙を目指した — 全8曲確認済）
- [x] All SE filenames exist in se_database.json ✅（爆発3, 和太鼓でドドン, 決定ボタンを押す4, きらきら輝く3, PC-Keyboard06-02(Hard), ひらめく1, Warning-Siren05-01(Fast-Mid), チーン1 — 全8種確認済）
- [x] Total duration within 15-20 min（15分50秒）
- [x] No self-congratulatory AI framing（「AIがすごい」ではなく「なぜこのパターンが再現されたか」に焦点）
- [x] 企画書のSランク3要素（戦略マップ・戦術配備・緊張度メカニクス）を全シーンで中核に据えている
- [x] 企画書のコンセプト「AIが"目"と"手足"を手に入れた」を物語軸1として反映
