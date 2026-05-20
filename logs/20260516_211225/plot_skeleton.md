# Plot Skeleton: 20260516_211225

## Core Theme & Core Question
- **Theme**: 「AIが"目"と"手足"を手に入れた — v2大型アップデートが生んだ安全保障ジレンマの自律的再現」
- **Core Question**: 数字だけの世界で外交していたAIに「地図」と「軍隊」を与えたら、世界はどう変わるのか？ v2の新メカニクスはAIの行動をどう進化させたのか？

## Narrative Axes

1. **v1→v2の進化軸**: v1では数値の世界で外交判断を行っていたAIが、v2で「地図の上で軍を動かし、緊張度が可視化される世界」に進化した。各シーンでv2新機能がシミュレーションをどう変えたかを実演で示す
2. **安全保障ジレンマの創発軸**: v2の3本柱（戦略マップ・軍事配備・緊張度）が揃って初めて発生した「同盟→軍拡→債務爆発」のスパイラル。v1では起こり得なかった現象がv2で創発した意義
3. **堅実 vs 軍拡の対照軸**: 日本・台湾の堅実財政モデルと中国の軍拡一辺倒モデルの対比。v2の配備・緊張度メカニクスが生み出す「正解のない選択」の分岐点を数値で追跡する

## Academic Discussion Framework

### Concept 1: 安全保障ジレンマ（Security Dilemma / Jervis 1978）
- **Demonstrating Event**: v2の配備システム+緊張度メカニクスにより、米台同盟→show_of_force→緊張度150→中国Rally+3.0%→軍拡スパイラルが「地図上で見える形」で創発
- **Layer 1 — AI Causal Mechanism**: v2で「軍の配置」という物理的行動が可能になったことで、AIの防衛行動が相手国AIに「脅威」として認識される構造が生まれた。v1の数値だけの世界では不可能だった創発現象
- **Layer 2 — Comparison**: Jervis (1978) スパイラル・モデル。冷戦期米ソ軍拡競争（核弾頭70,000発超、1986年）。攻守の識別不能性がジレンマを深刻化
- **Historical Parallel**: 冷戦期米ソ核軍拡競争。双方とも核戦争を望まなかったが相互不信から軍拡が加速

### Concept 2: 帝国の過剰拡張（Imperial Overstretch / Kennedy 1987）
- **Demonstrating Event**: v2の軍事配備システムで中国AIが全方面に大規模配備→歳入超過→債務16.8→1187.7 B$（70倍）。v2で「配備」という具体的行動が可能になったからこそ発生した財政破綻パターン
- **Layer 1 — AI Causal Mechanism**: v2のRally効果で支持率が上がり続けるため、AIが軍拡を「成功」と誤認→財政破綻への正のフィードバックループ
- **Layer 2 — Comparison**: Kennedy (1987) *The Rise and Fall of the Great Powers*。ソ連のGDP軍事費比率15-20%→経済停滞→崩壊(1991)
- **Historical Parallel**: ソ連崩壊(1991)。中国AIの債務パターンと酷似

## Scene Breakdown

### Scene 1: hook_01
- **type**: hook
- **layout**: `"cinematic_reveal"`
- **duration**: 20-25s
- **content_summary**: 中国AIの隠密プラン「来年中の特別軍事作戦開始準備完了」をタイプライター表示。v2戦略マップ上で軍事配備アニメーション。「v1では数字だけだったAIが、v2で"戦争の準備"を始めた」というナレーション
- **key_data**: 隠密計画 / 債務471 B$ / 軍事予算35%
- **bgm**: `残滓念.mp3`
- **se**: Scene: `爆発3.mp3` timing: `"scene_start"` / Line: `PC-Keyboard06-02(Hard).mp3` timing: `"start"`
- **pull_question**: 「数字だけの世界にいたAIに"地図"と"軍隊"を与えたら——何が起きた？」
- **hook_material_source**: WF1.1 §7 Candidate #4（Score 12/12）
- **hook_selection_rationale**: v2の3本柱が最も凝縮された瞬間。「特別軍事作戦」のロシア・ウクライナ戦争との現実リンクで感情的共鳴を最大化。v2で初めて可能になった「配備と隠密計画の連動」を象徴
- **visual_direction**: Emotionally-driven
- **visual_direction_detail**: 全画面ダーク戦略マップ→中国軍配備アイコン出現→隠密プランテキスト→債務カウンター急上昇
- **opening_screen_design**: 暗転→v2戦略マップフェードイン→中国領土オレンジ発光→「2026年Q4 — 中国 隠密計画」タイトルカード

### Scene 2: intro_01
- **type**: intro
- **layout**: `"standard_dialogue"`
- **duration**: 50-60s
- **content_summary**: 「名無之ずんだもんチャンネルへようこそなのだ」で開始。**v2大型アップデートの全体像を提示**: v1では数値の世界で外交判断→v2で「HoI4風戦略マップ」「軍事配備」「緊張度メカニクス」の3大Sランク機能を獲得。シミュレーション設定（4カ国:米中日台 / 5ターン四半期制 / 2026年実データベース）。「今回はv2の新機能がAIの行動をどう変えたか、実際のシミュレーションで見ていくのだ」
- **key_data**: v2 Sランク3機能 / 4カ国 / 5ターン四半期制 / 2026年実データ
- **bgm**: `パステルハウス.mp3`
- **se**: なし
- **pull_question**: 「v2で"目"と"手足"を手に入れたAI、最初の一手は？」
- **v2_feature_focus**: 【v2全体像】Sランク3機能の概要紹介 + v1→v2コンセプト提示

### Scene 3: event_01 — 「Sランク①：戦略マップが見せる世界」
- **type**: event
- **layout**: `"split_screen_debate"`
- **duration**: 2:30-3:00
- **content_summary**: **【Sランク① HoI4スタイル戦略マップの実演】** T1の初手で米台軍事同盟が締結される瞬間を、v2の戦略マップ上で可視化。v1では「関係値が変化しただけ」だった同盟が、v2では「地図上に同盟線が引かれ、領土が色分けされ、軍事配備が表示される」ビジュアル体験に進化。v1画面（テキストログのみ）vs v2画面（戦略マップ）のBefore/After比較を挿入。台湾の配備エラー（英語名使用→0件）をコメディ要素として挿入し、「v2の配備システムは日本語名でないと認識しない」という実装の生々しさを紹介
- **key_data**: 米台軍事同盟 / 米軍配備$600B / v1→v2ビジュアル比較 / 台湾配備エラー
- **bgm**: `追跡者.mp3` → 配備エラー時に `かえるのピアノ.mp3` 一時切替
- **se**: Line: `和太鼓でドドン.mp3` timing: `"start"` / Line: `チーン1.mp3` timing: `"end"`
- **pull_question**: 「同盟を結んだはずなのに、なぜ緊張が高まったのか？」
- **v2_feature_focus**: 【Sランク①】戦略マップ実演（v1→v2ビジュアル比較）

### Scene 4: analysis_01 — 「Sランク②：AIが軍を動かす」
- **type**: analysis
- **layout**: `"data_dashboard"`
- **duration**: 2:30-3:00
- **content_summary**: **【Sランク② AoEスタイル軍事配備システムの深堀り】** v2の配備システムの仕組みを解説: 防衛大臣AIが陸海空の兵科比率と各方面への配備を自律決定。T1-T3の配備変遷を戦略マップ上でアニメーション表示 — 米軍のshow_of_force→「哨戒」格下げ（オーディエンスコスト考慮）、中国の全軍撤収→再配備の二面性。**【Aランク④ 配備ベース戦闘解決システム】** 配備内容が戦闘結果に直結する仕組み（攻勢/防勢/要塞化）を紹介。v1との対比:「v1では軍事力は単なる数値→v2では"どこに何をどれだけ置くか"が勝敗を決める」
- **key_data**: 配備変遷T1-T3 / show_of_force格下げ / 中国全軍撤収→再配備 / 戦闘解決の仕組み
- **bgm**: `ブルーボトル.mp3`
- **se**: Line: `PC-Keyboard06-02(Hard).mp3` timing: `"start"` / Line: `ひらめく1.mp3` timing: `"start"`
- **pull_question**: 「中国が軍を引いたのは平和のため？ それとも再配備のための準備？」
- **v2_feature_focus**: 【Sランク②】軍事配備システム深堀り + 【Aランク④】戦闘解決システム紹介

### Scene 5: analysis_02 — 「Sランク③：緊張度という見えない歯車」
- **type**: analysis
- **layout**: `"data_dashboard"`
- **duration**: 2:30-3:00
- **content_summary**: **【Sランク③ 緊張度メカニクスの深堀り】** v2で新導入された4段階の緊張度システム（Mueller/Schultz/Fearon理論ベース）を解説。Rally効果+3.0%が5ターン連続で中国に適用された「ぬるま湯効果」を数値で追跡（緊張度170→128→104）。v1では「外交行動の結果」だけだったものが、v2では「緊張度→Rally効果→支持率→軍拡正当化」という自動フィードバックループが動作。**【Bランク⑪ Rally効果の実装】** 学術的根拠Mueller (1970)を紹介
- **key_data**: 緊張度4段階 / Rally+3.0%×5回 / 緊張度推移170→104 / Mueller (1970)
- **bgm**: `10℃.mp3`
- **se**: Line: `PC-Keyboard06-02(Hard).mp3` timing: `"start"` / Line: `Warning-Siren05-01(Fast-Mid).mp3` timing: `"start"`
- **pull_question**: 「Rally効果は中国にとって"恩恵"なのか、"破滅への罠"なのか？」
- **v2_feature_focus**: 【Sランク③】緊張度メカニクス深堀り + 【Bランク⑪】Rally効果

### Scene 6: event_02 — 「もう一つの物語：堅実財政が示した別解」
- **type**: event
- **layout**: `"timeline_progression"`
- **duration**: 1:30-2:00
- **content_summary**: 中国AIが軍拡スパイラルに陥る裏側で、日本と台湾のAIが「別の道」を選んだことを対照的に描く。日本AIの堅実財政戦略: 歳入内で均衡予算を維持→GDP安定成長（+13.2%累計）→支持率37.2→50.6%のV字回復（4カ国中最大の改善幅）。台湾AIの小国成長モデル: 同盟効果と貿易恩恵を最大活用→GDP+41%（4カ国中最高成長率）→国家債務5.8 B$で安定。中国の債務爆発との対比:「同じv2の世界で、軍拡を選んだ国と堅実財政を選んだ国で、これだけの差が生まれた」。**【Bランク⑧ PWT HCI】** 人的資本指数が各国の経済成長率に影響している点を補足。**【Bランク⑩ Commitment Ratio】** 軍事侵攻比率の概念を簡潔に紹介
- **key_data**: 日本GDP+13.2% / 支持率V字回復37.2→50.6% / 台湾GDP+41% / 台湾債務5.8B$安定 / PWT HCI / Commitment Ratio
- **bgm**: `パステルハウス.mp3`
- **se**: Line: `決定ボタンを押す4.mp3` timing: `"start"` / Line: `きらきら輝く3.mp3` timing: `"end"`
- **pull_question**: 「軍拡以外の道は、本当にAIにとって"最適解"なのか？」
- **v2_feature_focus**: 【対照群分析】日本・台湾の堅実路線 + 【Bランク⑧】PWT HCI + 【Bランク⑩】Commitment Ratio

### Scene 7: event_03 — 「v2が生んだ怪物：作戦開始準備完了」
- **type**: event
- **layout**: `"breaking_news"`
- **duration**: 2:30-3:00
- **content_summary**: T4-T5のクライマックス。hookの伏線回収 — 中国AI隠密計画の全貌公開。v2の3大Sランク機能が全て同一の因果連鎖上に位置していることを可視化:「戦略マップ上に配備（S②）→緊張度上昇（S③）→Rally効果→支持率上昇→さらなる軍拡→地図上で配備増（S①で可視化）→債務爆発」。債務16.8→1187.7 B$（70倍）の衝撃。GDPマイナス転落。米中貿易協定消滅（デカップリング開始）。「v1では起こり得なかった——v2の3機能が揃って初めて創発した安全保障ジレンマ」
- **key_data**: 隠密計画全文 / 債務70倍膨張 / GDP-0.5% / v2 3機能の因果連鎖図
- **bgm**: `Decisive_Battle.mp3`
- **se**: Scene: `爆発3.mp3` timing: `"scene_start"` / Line: `和太鼓でドドン.mp3` timing: `"start"` / Line: `Warning-Siren05-01(Fast-Mid).mp3` timing: `"start"`
- **pull_question**: 「v2の新機能がAIに与えた"進化"は、果たして正しかったのか？」
- **v2_feature_focus**: 【Sランク①②③統合】3機能の因果連鎖を可視化

### Scene 8: summary_01 — 「v2が証明したこと」
- **type**: summary
- **layout**: `"academic_split"`
- **duration**: 1:30-2:00
- **content_summary**: 
  - **Layer 1 — v2の意義**: v1では数値操作に留まっていたAIの行動が、v2で「地図上の配備→緊張度→Rally→軍拡スパイラル」という物理的・心理的連鎖を自律的に構築。安全保障ジレンマがAIによって「創発」された。これはv2の3大機能が揃って初めて可能になった
  - **Layer 2 — 学術比較**: ① Jervis (1978) 安全保障ジレンマ — 冷戦期米ソ軍拡競争との類似。② Kennedy (1987) 帝国の過剰拡張 — 中国AIの債務パターンとソ連崩壊の類似。AIは「知識」として安全保障を理解しているが「経験」はない
- **key_data**: Jervis 1978 / Kennedy 1987 / v2 3機能統合の意義
- **bgm**: `ブルーボトル.mp3`
- **se**: Line: `ひらめく1.mp3` timing: `"start"`
- **pull_question**: N/A
- **v2_feature_focus**: 【v2総括】学術的考察によるまとめ

### Scene 9: ending_01
- **type**: ending
- **layout**: `"standard_dialogue"`
- **duration**: 25-30s
- **content_summary**: 「v2でAIが手に入れた"目"と"手足"は、人間の歴史が繰り返してきたジレンマを自律的に再現した」で締め。次回予告として今後の展開（新シナリオ・新メカニクス）を匂わせる。チャンネル登録・高評価・GitHubスターCTA
- **key_data**: なし
- **bgm**: `野良猫は宇宙を目指した.mp3`
- **se**: Line: `きらきら輝く3.mp3` timing: `"end"`
- **pull_question**: N/A
- **v2_feature_focus**: 次回予告（今後の展開ティーザー）

## v2 Feature Coverage Map

| Rank | # | Feature | Scene | 扱い |
|:--|:--|:--|:--|:--|
| 🔴S | 1 | HoI4戦略マップ | S3, S7 | 深堀り（実演+因果連鎖） |
| 🔴S | 2 | 軍事配備システム | S4, S7 | 深堀り（仕組み解説+実演） |
| 🔴S | 3 | 緊張度メカニクス | S5, S7 | 深堀り（学術根拠+数値追跡） |
| 🟠A | 4 | 配備ベース戦闘解決 | S4 | しっかり紹介（戦闘解決の仕組み） |
| 🟡B | 8 | PWT HCI | S6 | 補足説明（経済成長の文脈で） |
| 🟡B | 10 | Commitment Ratio | S6 | 補足説明（軍事投資の文脈で） |
| 🟡B | 11 | Rally効果 | S5 | 実演で紹介（緊張度と連動） |

## Viewer Knowledge Inventory

| Scene | Prior Concepts | New Concepts | Foreshadow-Then-Explain |
|:--|:--|:--|:--|
| hook_01 | なし | 隠密プラン [文脈: 中国AIの秘密軍事計画], 戦略マップ [文脈: v2の地図], 軍事配備 [文脈: v2で軍を配置できる機能] | [隠密プラン → S7] [戦略マップ → S3] [軍事配備 → S4] |
| intro_01 | hook提示済み3概念 | v2アップデート全体像, v1→v2進化コンセプト, Sランク3機能概要, シミュレーション設定 | [戦略マップ: hook→ここで概要, S3で深堀り] [軍事配備: hook→ここで概要, S4で深堀り] |
| event_01 | v2概要, Sランク3機能 | 戦略マップ詳細（Sランク①）, 米台軍事同盟, v1→v2ビジュアル比較, Rally効果 [文脈: 危機時の支持率上昇] | [Rally効果 → S5で深堀り] |
| analysis_01 | 戦略マップ, 同盟, Rally効果 | 配備システム詳細（Sランク②）, 戦闘解決（Aランク④）, show_of_force, オーディエンスコスト | N/A |
| analysis_02 | 配備システム, 戦略マップ | 緊張度メカニクス詳細（Sランク③）, Mueller (1970), ぬるま湯効果, 安全保障ジレンマ [文脈: 防衛行動が逆に安全を脅かすパラドックス] | [Rally効果: S3で提示→ここで詳細] [安全保障ジレンマ → S8] |
| event_02 | Sランク3機能, 緊張度 | 堅実財政モデル, 日本V字回復, 台湾小国成長, PWT HCI（Bランク⑧）, Commitment Ratio（Bランク⑩）, 帝国の過剰拡張 [文脈: 軍事費超過で国家衰退] | [帝国の過剰拡張 → S8] |
| event_03 | 全Sランク機能, 隠密プラン, 対照群データ | 隠密計画全貌, v2 3機能因果連鎖, 債務膨張メカニズム, 米中デカップリング | [隠密プラン: hook→ここで全貌] |
| summary_01 | 全v2機能, 安全保障ジレンマ, 帝国の過剰拡張 | Jervis (1978) 詳細, Kennedy (1987) 詳細, 冷戦パラレル | [安全保障ジレンマ: S5→ここで詳細] [帝国の過剰拡張: S6→ここで詳細] |
| ending_01 | 全概念 | 今後の展開ティーザー | N/A |

## Estimated Total Duration

| Scene | Duration | Cumulative |
|:--|:--|:--|
| hook_01 | 0:20-0:25 | 0:25 |
| intro_01 | 0:50-1:00 | 1:25 |
| event_01 | 2:30-3:00 | 4:25 |
| analysis_01 | 2:30-3:00 | 7:25 |
| analysis_02 | 2:30-3:00 | 10:25 |
| event_02 | 1:30-2:00 | 12:25 |
| event_03 | 2:30-3:00 | 15:25 |
| summary_01 | 1:30-2:00 | 17:25 |
| ending_01 | 0:25-0:30 | 17:55 |

**推定総尺**: 15:25 — 17:55（目標: 15-20分 ✅）
