"""
シティ・デストロイヤー（Alien超兵器）Mixin

Alien専用の超兵器「シティ・デストロイヤー」の処理を担当するMixin。
チャージに1ターンを要し、発射するとAlien AIが指定した大都市を壊滅させる。

設計:
  - チャージ: 沈黙期間終了後、毎ターン自動チャージ
  - 発射判断: Alien AIがLLMで対象を選択（__CITY_DESTROYER__ 仮想フラグ経由）
  - ダメージ: GDP-15%, 人口-10%, 軍事-8%, 支持率-15%
"""

from agent.prompts.base import _is_agi_country
from .constants import (
    CITY_DESTROYER_ECON_DAMAGE,
    CITY_DESTROYER_POP_DAMAGE,
    CITY_DESTROYER_MIL_DAMAGE,
    CITY_DESTROYER_APPROVAL_PENALTY,
)


class CityDestroyerMixin:
    def _process_city_destroyer(self, actions):
        """Alien AIが指定した対象にシティ・デストロイヤーを発射する。
        
        process_turn() の戦争処理直前に呼び出される。
        actions辞書のDiplomaticAction内にある __CITY_DESTROYER__ 仮想フラグを
        読み取り、チャージ済みであれば発射処理を実行する。
        """
        for country_name, country in self.state.countries.items():
            if not getattr(country, 'is_alien', False):
                continue
            
            # actions辞書からAlienの行動を取得
            action = actions.get(country_name)
            if not action:
                continue
            
            # DiplomaticActionから __CITY_DESTROYER__ 仮想フラグを抽出
            targets = []
            for dip in action.diplomatic_policies:
                if dip.target_country.startswith("__CITY_DESTROYER__"):
                    target_name = dip.target_country.replace("__CITY_DESTROYER__", "")
                    targets.append(target_name)
            
            if country.alien_city_destroyer_charged and targets:
                # === チャージ済み + ターゲット指定あり → 発射 ===
                for target_name in targets:
                    target = self.state.countries.get(target_name)
                    if target and not getattr(target, 'is_alien', False):
                        self._fire_city_destroyer(country_name, target_name, target)
                # 発射後にチャージをリセット（次ターンに再チャージ開始）
                country.alien_city_destroyer_charged = False
                self.sys_logs_this_turn.append(
                    f"[{country_name} シティ・デストロイヤー] 発射完了。チャージをリセット。"
                )
            elif not country.alien_city_destroyer_charged:
                # === 未チャージ → チャージ開始 ===
                country.alien_city_destroyer_charged = True
                self.sys_logs_this_turn.append(
                    f"[{country_name} シティ・デストロイヤー] チャージ完了。次ターンに発射可能。"
                )
            # else: チャージ済みだがターゲット未指定 → チャージ維持（AIが発射を控えた）

    def _fire_city_destroyer(self, alien_name: str, target_name: str, target):
        """シティ・デストロイヤーの発射処理。対象国にダメージを適用する。"""
        old_econ = target.economy
        old_pop = target.population
        old_mil = target.military
        old_approval = target.approval_rating

        econ_damage = target.economy * CITY_DESTROYER_ECON_DAMAGE
        pop_damage = target.population * CITY_DESTROYER_POP_DAMAGE
        mil_damage = target.military * CITY_DESTROYER_MIL_DAMAGE

        target.economy = max(1.0, target.economy - econ_damage)
        target.population = max(0.1, target.population - pop_damage)
        target.military = max(0.0, target.military - mil_damage)
        # AGI完全管理国家: 支持率ペナルティを免除（物理ダメージは維持）
        if not _is_agi_country(target_name):
            target.approval_rating = max(0.0, target.approval_rating - CITY_DESTROYER_APPROVAL_PENALTY)

        # ニュースイベント
        self.log_event(
            f"☄️ 【シティ・デストロイヤー発射】{alien_name}が{target_name}の"
            f"大都市に壊滅的ビーム兵器を発射！都市は一瞬で灰燼と化しました。"
            f"（経済 {old_econ:.0f}→{target.economy:.0f} [-{econ_damage:.0f}], "
            f"人口 {old_pop:.1f}M→{target.population:.1f}M [-{pop_damage:.1f}M], "
            f"軍事 {old_mil:.0f}→{target.military:.0f} [-{mil_damage:.0f}]）",
            involved_countries=[alien_name, target_name, "global"]
        )

        # システムログ（詳細）
        self.sys_logs_this_turn.append(
            f"[{alien_name} シティ・デストロイヤー → {target_name}] "
            f"経済: {old_econ:.0f}→{target.economy:.0f} (-{CITY_DESTROYER_ECON_DAMAGE:.0%}), "
            f"人口: {old_pop:.1f}M→{target.population:.1f}M (-{CITY_DESTROYER_POP_DAMAGE:.0%}), "
            f"軍事: {old_mil:.0f}→{target.military:.0f} (-{CITY_DESTROYER_MIL_DAMAGE:.0%}), "
            f"支持率: {old_approval:.1f}%→{target.approval_rating:.1f}% (-{CITY_DESTROYER_APPROVAL_PENALTY}%)"
        )
