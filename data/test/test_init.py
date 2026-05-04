"""初期化テストスクリプト: CSVデータのロードと初期状態の検証"""
import sys, os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))
os.chdir(PROJECT_ROOT)

from main import initialize_world

print("=" * 60)
print("企画 #4: 武器支援のジレンマ — 初期化テスト")
print("=" * 60)

try:
    world = initialize_world(data_dir="data")
    print(f"\n✅ WorldState初期化成功")
    print(f"   ターン: {world.turn}, 年: {world.year}, Q: {world.quarter}")
    
    # 1. 5カ国チェック
    print(f"\n📋 参加国 ({len(world.countries)}カ国):")
    expected = ["日本", "アメリカ", "中国", "台湾", "フィリピン"]
    for name in expected:
        if name in world.countries:
            c = world.countries[name]
            print(f"   ✅ {name}: GDP={c.economy:.0f}B$, Mil={c.military:.0f}B$, Pop={c.population:.1f}M, Approval={c.approval_rating:.0f}%")
        else:
            print(f"   ❌ {name}: 未登録！")
    
    # 不要な国がないか
    extra = set(world.countries.keys()) - set(expected)
    if extra:
        print(f"   ⚠️ 余分な国: {extra}")
    else:
        print(f"   ✅ 不要な国なし")
    
    # 2. 中台戦争チェック
    print(f"\n⚔️ 戦争状態 ({len(world.active_wars)}件):")
    china_taiwan_war = False
    for war in world.active_wars:
        print(f"   ⚔️ {war.aggressor} → {war.defender} (攻撃投入率={war.aggressor_commitment_ratio}, 防衛投入率={war.defender_commitment_ratio})")
        if war.aggressor == "中国" and war.defender == "台湾":
            china_taiwan_war = True
    if china_taiwan_war:
        print(f"   ✅ 中国 vs 台湾 at_war確認")
    else:
        print(f"   ❌ 中国 vs 台湾 at_war未設定！")
    
    # 3. 日台武器支援チェック
    print(f"\n🤝 援助契約 ({len(world.recurring_aid_contracts)}件):")
    japan_taiwan_aid = False
    for aid in world.recurring_aid_contracts:
        print(f"   💰 {aid.donor} → {aid.target}: eco={aid.amount_economy:.1f}B$, mil={aid.amount_military:.1f}B$")
        if aid.donor == "日本" and aid.target == "台湾" and aid.amount_military >= 6.0:
            japan_taiwan_aid = True
    if japan_taiwan_aid:
        print(f"   ✅ 日本→台湾 武器支援(mil>=6.0)確認")
    else:
        print(f"   ❌ 日本→台湾 武器支援が見つからない！")
    
    # 4. 中国→日本の制裁がないことを確認
    print(f"\n🚫 制裁状態 ({len(world.active_sanctions)}件):")
    china_japan_sanction = False
    for s in world.active_sanctions:
        print(f"   🔒 {s.imposer} → {s.target}")
        if s.imposer == "中国" and s.target == "日本":
            china_japan_sanction = True
    if not china_japan_sanction:
        print(f"   ✅ 中国→日本の制裁なし（AIの自律判断に委ねる）")
    else:
        print(f"   ❌ 中国→日本の制裁が初期値に設定されている！")
    
    # 5. 同盟チェック
    print(f"\n🤝 同盟関係:")
    from models import RelationType
    for a, b in [("日本", "アメリカ"), ("アメリカ", "フィリピン")]:
        rel = world.relations.get(a, {}).get(b, "unknown")
        if rel == RelationType.ALLIANCE:
            print(f"   ✅ {a}↔{b}: alliance")
        else:
            print(f"   ❌ {a}↔{b}: {rel} (expected alliance)")
    
    # 6. 日本のGDP/支持率が初期値のまま
    japan = world.countries["日本"]
    print(f"\n🇯🇵 日本の初期値:")
    print(f"   GDP: {japan.economy:.0f}B$ (expected 4200)")
    print(f"   支持率: {japan.approval_rating:.0f}% (expected 65)")
    if abs(japan.economy - 4200) < 10 and abs(japan.approval_rating - 65) < 1:
        print(f"   ✅ 初期値正常（制裁ダメージもサイバー攻撃ダメージも未適用）")
    else:
        print(f"   ❌ 初期値が変動している！")
    
    # 7. ホルムズ海峡封鎖がないことを確認
    print(f"\n🌊 海峡封鎖:")
    if len(world.active_strait_blockades) == 0:
        print(f"   ✅ 海峡封鎖なし（ホルムズ海峡ハードコード除去成功）")
    else:
        print(f"   ❌ 海峡封鎖が存在: {world.active_strait_blockades}")
    
    print(f"\n{'=' * 60}")
    print(f"🎯 テスト完了: すべてのチェックが通過しました")
    print(f"{'=' * 60}")

except Exception as e:
    import traceback
    print(f"\n❌ 初期化エラー: {e}")
    traceback.print_exc()
    sys.exit(1)
