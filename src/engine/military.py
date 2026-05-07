import random

from .constants import (
    DEFENDER_ADVANTAGE_MULTIPLIER,
    MIN_COMMITMENT_RATIO,
    COMMITMENT_ECONOMIC_DRAIN
)

class MilitaryMixin:
    def _process_wars(self):
        surviving_wars = []
        
        # === 合計投入率キャップ（前処理）===
        # 1国が複数の戦争に参加している場合、各戦争の投入率の合計が1.0を超えないよう
        # 比例配分でスケールダウンする。全軍の100%以上を投入するのは物理的に不可能。
        country_total_commitment = {}  # {国名: 合計投入率}
        for war in self.state.active_wars:
            # 攻撃側
            agg_name = war.aggressor
            agg_commit = max(MIN_COMMITMENT_RATIO, war.aggressor_commitment_ratio)
            country_total_commitment[agg_name] = country_total_commitment.get(agg_name, 0.0) + agg_commit
            # 防衛側
            def_name = war.defender
            def_commit = max(MIN_COMMITMENT_RATIO, war.defender_commitment_ratio)
            country_total_commitment[def_name] = country_total_commitment.get(def_name, 0.0) + def_commit
            # 防衛支援国
            for sup_name, sup_commit in war.defender_supporters.items():
                country_total_commitment[sup_name] = country_total_commitment.get(sup_name, 0.0) + sup_commit
        
        # 合計が1.0を超える国のスケールダウン
        for country_name, total in country_total_commitment.items():
            if total > 1.0:
                scale_factor = 1.0 / total
                self.sys_logs_this_turn.append(
                    f"[⚠️ 投入率キャップ] {country_name}: 合計投入率{total:.0%}が100%超過。"
                    f"各戦争の投入率を{scale_factor:.2f}倍にスケールダウン"
                )
                for war in self.state.active_wars:
                    if war.aggressor == country_name:
                        old = war.aggressor_commitment_ratio
                        war.aggressor_commitment_ratio = max(MIN_COMMITMENT_RATIO, old * scale_factor)
                        self.sys_logs_this_turn.append(
                            f"  └ 対{war.defender}戦（攻撃側）: {old:.0%} → {war.aggressor_commitment_ratio:.0%}"
                        )
                    if war.defender == country_name:
                        old = war.defender_commitment_ratio
                        war.defender_commitment_ratio = max(MIN_COMMITMENT_RATIO, old * scale_factor)
                        self.sys_logs_this_turn.append(
                            f"  └ 対{war.aggressor}戦（防衛側）: {old:.0%} → {war.defender_commitment_ratio:.0%}"
                        )
        
        for war in self.state.active_wars:
            aggressor = self.state.countries.get(war.aggressor)
            defender = self.state.countries.get(war.defender)
            
            if not aggressor or not defender:
                continue # 国が既に滅亡している等
            
            # 投入比率の適用（最小値を保証）
            agg_commit = max(MIN_COMMITMENT_RATIO, war.aggressor_commitment_ratio)
            def_commit = max(MIN_COMMITMENT_RATIO, war.defender_commitment_ratio)
                
            # ダメージ計算（投入分の軍事力のみで戦闘）
            agg_committed = aggressor.military * agg_commit
            def_committed = defender.military * def_commit
            
            # === 共同防衛メカニズム: 防衛支援国の戦力を加算 ===
            supporter_committed = {}  # {国名: 投入戦力}
            total_supporter_power = 0.0
            supporter_info_parts = []
            for sup_name, sup_commit in war.defender_supporters.items():
                sup_country = self.state.countries.get(sup_name)
                if sup_country and sup_country.military > 0:
                    sup_power = sup_country.military * sup_commit
                    supporter_committed[sup_name] = sup_power
                    total_supporter_power += sup_power
                    supporter_info_parts.append(f"{sup_name}({sup_commit:.0%}={sup_power:.0f})")
            
            # 防衛側ボーナス（防衛国+支援国の合計に適用）
            def_power = (def_committed + total_supporter_power) * DEFENDER_ADVANTAGE_MULTIPLIER
            agg_power = agg_committed
            
            agg_damage_raw = def_power * random.uniform(0.05, 0.15)
            def_damage_raw = agg_power * random.uniform(0.05, 0.15)
            
            # === 電磁バリアシステム: Alienへの通常攻撃を無効化 ===
            # 防衛側がAlienでバリア有効 → 攻撃側の通常ダメージを無効化
            if getattr(defender, 'is_alien', False) and getattr(defender, 'alien_barrier_hp', 0) > 0:
                def_damage_raw = 0.0
                self.sys_logs_this_turn.append(
                    f"[電磁バリア] {defender.name}の電磁バリアにより{aggressor.name}の通常攻撃が無効化 "
                    f"(バリアHP: {defender.alien_barrier_hp})"
                )
                self.log_event(
                    f"🛡️ 【電磁バリア作動】{defender.name}の電磁バリアが{aggressor.name}の"
                    f"通常兵器による攻撃を完全に遮断しました！",
                    involved_countries=[aggressor.name, defender.name, "global"]
                )
            # 攻撃側がAlienでバリア有効 → 反撃ダメージを無効化（一方的攻撃）
            if getattr(aggressor, 'is_alien', False) and getattr(aggressor, 'alien_barrier_hp', 0) > 0:
                agg_damage_raw = 0.0
                self.sys_logs_this_turn.append(
                    f"[電磁バリア] {aggressor.name}の電磁バリアにより反撃が無効化"
                )
            
            # 損害は投入分のみに適用（後方予備軍は温存）
            agg_damage = min(agg_damage_raw, agg_committed)
            
            # 防衛側ダメージの分配（防衛国+支援国に投入戦力比率で按分）
            total_def_committed = def_committed + total_supporter_power
            def_damage = min(def_damage_raw, total_def_committed)
            
            if total_def_committed > 0:
                # 防衛国本体のダメージ分
                def_damage_share = def_damage * (def_committed / total_def_committed)
                defender.military = max(0.0, defender.military - def_damage_share)
                
                # 支援国へのダメージ分配
                for sup_name, sup_power in supporter_committed.items():
                    sup_country = self.state.countries.get(sup_name)
                    if sup_country:
                        sup_damage = def_damage * (sup_power / total_def_committed)
                        sup_country.military = max(0.0, sup_country.military - sup_damage)
                        # 支援国の経済デバフ（投入比率に応じた戦時負担）
                        sup_commit_ratio = war.defender_supporters.get(sup_name, 0.1)
                        sup_war_drain = 1.0 - (COMMITMENT_ECONOMIC_DRAIN * sup_commit_ratio * 0.5)  # 本国より軽い
                        sup_country.economy *= max(0.95, 0.99 * sup_war_drain)
            else:
                def_damage_share = def_damage
                defender.military = max(0.0, defender.military - def_damage)
            
            aggressor.military = max(0.0, aggressor.military - agg_damage)
            
            # 人口減少計算（軍事ダメージ割合に比例。防衛側は戦場となるため民間人被害が大きい）
            # ※係数を実態に即して修正（元の1/100スケール）
            agg_pop_loss = aggressor.population * (agg_damage / max(1.0, agg_committed)) * 0.0005
            def_pop_loss = defender.population * (def_damage_share / max(1.0, def_committed)) * 0.0015
            
            aggressor.population = max(0.1, aggressor.population - agg_pop_loss)
            defender.population = max(0.1, defender.population - def_pop_loss)
            
            # 累積損害の記録（講和時の賠償金計算用）
            war.aggressor_cumulative_military_loss += agg_damage
            war.defender_cumulative_military_loss += def_damage
            agg_gdp_per_capita = aggressor.economy / max(0.1, aggressor.population)
            def_gdp_per_capita = defender.economy / max(0.1, defender.population)
            war.aggressor_cumulative_civilian_gdp_loss += agg_pop_loss * agg_gdp_per_capita
            war.defender_cumulative_civilian_gdp_loss += def_pop_loss * def_gdp_per_capita
            
            # 経済デバフ（戦争状態による疲弊 + 投入比率に応じた追加負担）
            agg_war_drain = 1.0 - (COMMITMENT_ECONOMIC_DRAIN * agg_commit)
            def_war_drain = 1.0 - (COMMITMENT_ECONOMIC_DRAIN * def_commit)
            aggressor.economy *= max(0.90, 0.98 * agg_war_drain)
            defender.economy *= max(0.90, 0.98 * def_war_drain)
            
            # 支持率デバフ/ボーナス
            # 攻撃側: 長引く戦争の不満
            aggressor.approval_rating -= 1.0
            
            # 防衛側: Rally 'round the flag 効果 (Mueller 1970, 1973)
            war_turns = war.war_turns_elapsed
            if war_turns <= 4:
                rally_bonus = max(0.0, 10.0 - (war_turns * 2.5))
                defender.approval_rating = min(100.0, defender.approval_rating + rally_bonus)
                if rally_bonus > 0:
                    self.sys_logs_this_turn.append(
                        f"[Rally効果] {defender.name}: 国民の結束により支持率 +{rally_bonus:.1f}% "
                        f"(Mueller 1970, 経過{war_turns}ターン)"
                    )
            else:
                defender.approval_rating -= 1.5
            
            # 戦争経過ターンのカウントアップ
            war.war_turns_elapsed = war_turns + 1
            
            # 占領進捗率の更新（投入済み戦力の差による）
            # 攻撃側優勢 → 進捗が増加（攻め込む）
            # 防衛側優勢 → 進捗が減少し、0を下回ると守り側が逆占領（攻め側の領土を奪う）
            power_diff = agg_power - def_power
            progress_change = power_diff / max(1, max(agg_power, def_power)) * 5.0

            new_progress = war.target_occupation_progress + progress_change

            if new_progress < 0.0:
                # 守り側が戦力逆転して反攻 → 攻め側の領土を逆占領
                counter_occupation = abs(new_progress)  # 逆占領進捗（0〜100）
                war.target_occupation_progress = 0.0
                war.counter_occupation_progress = min(100.0, war.counter_occupation_progress + counter_occupation)
                self.sys_logs_this_turn.append(
                    f"[反攻進行] {war.defender}が戦力逆転により{war.aggressor}領土への反攻を開始。"
                    f"逆占領進捗: {war.counter_occupation_progress:.1f}%"
                )
            else:
                war.target_occupation_progress = min(100.0, new_progress)
                # 攻め側が優勢に戻ったら逆占領進捗を減衰
                if war.counter_occupation_progress > 0:
                    war.counter_occupation_progress = max(0.0, war.counter_occupation_progress - abs(progress_change))
            
            # 支援国情報のログ文字列
            supporter_log = ""
            if supporter_info_parts:
                supporter_log = f" | 支援国: {', '.join(supporter_info_parts)}"
            
            self.log_event(
                f"🔥 【戦況報告】{war.aggressor} vs {war.defender}{supporter_log} | "
                f"占領進捗: {war.target_occupation_progress:.1f}% | "
                f"投入率: {war.aggressor}={agg_commit:.0%}, {war.defender}={def_commit:.0%} | "
                f"(両軍損害: {aggressor.name}軍残{aggressor.military:.0f} / {defender.name}軍残{defender.military:.0f} | "
                f"民間人犠牲: {aggressor.name} {agg_pop_loss:.2f}M, {defender.name} {def_pop_loss:.2f}M)",
                involved_countries=[war.aggressor, war.defender, "global"]
            )
            
            self.sys_logs_this_turn.append(
                f"[戦争ダメージ] {war.aggressor}(投入率{agg_commit:.0%}, 投入戦力{agg_committed:.0f}) vs "
                f"{war.defender}(投入率{def_commit:.0%}, 投入戦力{def_committed:.0f}+支援{total_supporter_power:.0f}, 防衛ボーナス込み{def_power:.0f}). "
                f"経済負担: {war.aggressor} x{agg_war_drain:.3f}, {war.defender} x{def_war_drain:.3f}"
            )
            
            # 敗北判定
            war_ended = False
            if war.target_occupation_progress >= 100.0 or defender.military < 1.0:
                # 攻め側が完全占領 or 防衛側の軍事力が尽きた → 防衛側の敗北
                self._handle_defeat(defender.name, aggressor.name)
                war_ended = True
            elif aggressor.military < 1.0:
                # 防衛側が反撃で攻め側の軍事力を壊滅させた → 攻め側の敗北
                self._handle_defeat(aggressor.name, defender.name)
                war_ended = True
            elif war.counter_occupation_progress >= 100.0:
                # 防衛側が逆占領を完成させた → 攻め側の領土を奪取して勝利
                self.log_event(
                    f"🔄 【戦局逆転・反攻成功】{war.defender}が{war.aggressor}の領土を完全占領しました！"
                    f"守りを突破した{war.defender}軍が攻め側の首都を制圧します。",
                    involved_countries=[war.aggressor, war.defender, "global"]
                )
                self._handle_defeat(aggressor.name, defender.name)
                war_ended = True
                
            if not war_ended:
                surviving_wars.append(war)
                
        self.state.active_wars = surviving_wars

    def _handle_defeat(self, loser_name: str, winner_name: str):
        loser = self.state.countries[loser_name]
        winner = self.state.countries[winner_name]
        
        self.log_event(f"💀 【国家崩壊】{loser_name}の政府は崩壊し、{winner_name}に対して無条件降伏しました！", involved_countries=[loser_name, winner_name, "global"])
        
        # 併合ボーナス (経済力の吸収)
        winner.economy += loser.economy * 0.5
        winner.military += loser.military * 0.2
        winner.population += loser.population
        winner.initial_population += loser.initial_population
        self.log_event(f"📈 {winner_name}は{loser_name}の領土と人口({loser.population:.1f}M)を併合しました。", involved_countries=[loser_name, winner_name, "global"])
        
        # 敗戦国を世界から削除
        del self.state.countries[loser_name]
        
        # 共通クリーンアップ関数で関連データを一括削除
        self._cleanup_eliminated_country(loser_name)
        
        # 技術革新の原産国が敗北した場合（必要に応じて）
        for bt in self.state.active_breakthroughs:
            if bt.origin_country == loser_name:
                pass
