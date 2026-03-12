import math
from models import GovernmentType, RelationType

from .constants import (
    AUTHORITARIAN_BASE_SAVING_RATE, DEMOCRACY_BASE_SAVING_RATE,
    GOVERNMENT_CROWD_IN_MULTIPLIER, TRADE_GRAVITY_FRICTION_ALLIANCE, TRADE_GRAVITY_FRICTION_NEUTRAL
)

class EconomyMixin:
    def _process_trade_and_sanctions(self):
        # 期限切れ提案のクリア（1ターンのみ有効）
        self.state.pending_summits = [s for s in self.state.pending_summits if s not in self.summits_to_run_this_turn]
        
        # 同盟提案の期限切れクリア（同ターン内で双方合意が成立しなかった提案を除去）
        # ※同ターン内で双方がpropose_allianceした場合は _process_diplomacy_and_espionage 内で既に処理済み
        # 残った提案は次ターンまで保持し、次ターンの _process_diplomacy_and_espionage で再度チェックされる
        # 2ターン以上放置された提案はここでクリアする（pending_alliances は翌ターンの処理前にリセット）
        
        # 当期のNXをリセット
        for c_name, country in self.state.countries.items():
            country.last_turn_nx = 0.0

        # Trade (IS Balance / Trade Deficit Model)
        # まず全国家のISバランス(貯蓄・投資バランス)を算出
        macro_balances = {}
        
        for c_name, country in self.state.countries.items():
            dom = self.turn_domestic_factors.get(c_name, {})
            inv_welfare = dom.get("inv_wel", 0.0)
            inv_economy = dom.get("inv_econ", 0.0)
            # engine.py内での統一を図るため、ここでは新モデルに合わせて再度S, I, G, Tを推定
            
            # 1. 貯蓄率 (S) ※_process_domestic と同一の式を使用（ARCHITECTURE.md §2.2 準拠）
            base_s_rate = AUTHORITARIAN_BASE_SAVING_RATE if country.government_type == GovernmentType.AUTHORITARIAN else DEMOCRACY_BASE_SAVING_RATE
            s_rate = max(0.15, base_s_rate - (inv_welfare * 0.15))
            
            # 簡略化のため、ISバランスの評価式に用いる名目上の算出
            # (S - I) + (T - G) = NX
            T = country.economy * country.tax_rate
            # G は前ターンの投資合計割合を予算に掛けたものと推定する
            G = country.government_budget * dom.get("total_inv", 1.0)
            
            C = (country.economy - T) * (1.0 - s_rate)
            S_private = max(0.0, (country.economy - T) - C) # 民間貯蓄
            
            # I は民間貯蓄の85% + インフラ投資により誘発されると仮定
            I = max(0.0, S_private * 0.85 + (G * inv_economy * GOVERNMENT_CROWD_IN_MULTIPLIER))
            
            # IS方程式に基づく経常収支(NX)理論値
            nx_theoretical = (S_private - I) + (T - G)
            macro_balances[c_name] = nx_theoretical

        for trade in self.state.active_trades:
            if trade.country_a not in self.state.countries or trade.country_b not in self.state.countries:
                continue
            ca = self.state.countries[trade.country_a]
            cb = self.state.countries[trade.country_b]
            rel = self._get_relation(trade.country_a, trade.country_b)
            friction = TRADE_GRAVITY_FRICTION_ALLIANCE if rel == RelationType.ALLIANCE else TRADE_GRAVITY_FRICTION_NEUTRAL
            
            # 重力モデルに基づくベース取引量: 経済規模の平方根に比例、摩擦に反比例
            base_volume = math.sqrt(ca.economy * cb.economy) / friction
            
            # 制裁によるGravity Modelハイブリッド介入
            sanctions_exist = any(s for s in self.state.active_sanctions if 
                                 (s.imposer == trade.country_a and s.target == trade.country_b) or
                                 (s.imposer == trade.country_b and s.target == trade.country_a))
            if sanctions_exist:
                base_volume *= 0.05 # 制裁中は貿易額が95%減少
            
            nx_a = macro_balances[trade.country_a]
            nx_b = macro_balances[trade.country_b]
            
            # 【SNA基準への改修】絶対額の差分ではなく、GDPに対する収支比率の差分を用いる（スケール・バイアスの解消）
            nx_ratio_a = nx_a / max(1.0, ca.economy)
            nx_ratio_b = nx_b / max(1.0, cb.economy)
            diff_ratio = nx_ratio_a - nx_ratio_b
            
            # 【学術的適正化】係数を15.0から0.5へ大幅に下方修正。
            # 貯蓄・投資バランスの差が二国間不均衡に与える影響度（弾力性）を現実的な範囲に収める。
            raw_transfer = diff_ratio * base_volume * 0.5
            
            # 物理的限界のガードレール: 赤字転移額は二国間の貿易総量(base_volume)を超えない
            transfer_capped_by_volume = max(-base_volume, min(base_volume, raw_transfer))
            
            # マクロ経済的ガードレール (サドン・ストップ防止): 1ターンの流出は相手国/自国のGDPの3%を上限とする
            # (IMF等の5%ルールに基づき、四半期ベースで3%＝年率約12%を「歴史的最大級のショック」として設定)
            limit_a = ca.economy * 0.03
            limit_b = cb.economy * 0.03
            deficit_transfer = max(-limit_a, min(limit_b, transfer_capped_by_volume))
            
            mutual_bonus = base_volume * 0.005 # 貿易による共通の経済効率化ボーナス
            
            # 【SNA基準への改修】GDP(economy)からの直接減算を廃止。
            # 純輸出(NX)を記録し、赤字分は国家債務に追加
            ca_nx = mutual_bonus + deficit_transfer
            cb_nx = mutual_bonus - deficit_transfer
            
            ca.last_turn_nx += ca_nx
            cb.last_turn_nx += cb_nx
            
            # 赤字国は資金不足を海外からの借入（対外債務）で補う
            if ca_nx < 0:
                ca.national_debt += abs(ca_nx)
            if cb_nx < 0:
                cb.national_debt += abs(cb_nx)
            
            # 支持率の基礎ボーナス（貿易による相互利益）
            ca_support = 0.5
            cb_support = 0.5
            if deficit_transfer > 0:
                # Bが赤字（安い輸入品の恩恵）
                cb_support = 1.0
            else:
                # Aが赤字
                ca_support = 1.0
                
            if trade.country_a in self.turn_domestic_factors:
                self.turn_domestic_factors[trade.country_a]["trade_support_bonus"] += ca_support
            if trade.country_b in self.turn_domestic_factors:
                self.turn_domestic_factors[trade.country_b]["trade_support_bonus"] += cb_support
                
            self.sys_logs_this_turn.append(
                f"[Trade IS Balance] {trade.country_a} vs {trade.country_b} | "
                f"Volume:{base_volume:.1f}, NX_Ratio Diff(A-B):{diff_ratio:+.2%} -> "
                f"{trade.country_a} ({ca_nx:+.1f} GDP_NX, Debt {ca.national_debt:.1f}, {ca_support:+.1f}% Support), "
                f"{trade.country_b} ({cb_nx:+.1f} GDP_NX, Debt {cb.national_debt:.1f}, {cb_support:+.1f}% Support)"
            )
            
        # 各国の総貿易収支(NX)による支持率ペナルティ評価
        for c_name, country in self.state.countries.items():
            if country.last_turn_nx < 0:
                # 国全体で赤字
                country.trade_deficit_counter += 1
                if country.trade_deficit_counter > 3:
                    # ペナルティ上限を3%に緩和
                    penalty = min(3.0, (country.trade_deficit_counter - 3) * 1.0)
                    if c_name in self.turn_domestic_factors:
                        self.turn_domestic_factors[c_name]["trade_support_bonus"] -= penalty
                    self.sys_logs_this_turn.append(f"[Trade Penalty] {c_name} は全体的な貿易赤字による国内産業空洞化で支持率低下(-{penalty:.1f}%)")
            else:
                # 単年度黒字ならカウンターを減少（またはリセット）
                country.trade_deficit_counter = max(0, country.trade_deficit_counter - 1)
            
        # Sanctions (Damage Model)
        for sanction in self.state.active_sanctions:
            if sanction.imposer not in self.state.countries or sanction.target not in self.state.countries:
                continue
            imposer = self.state.countries[sanction.imposer]
            target = self.state.countries[sanction.target]
            
            # 制裁ダメージ: max 10%デバフ。2.0 * (imposer / target)
            ratio = imposer.economy / max(1.0, target.economy)
            damage_percent = min(10.0, 2.0 * ratio)
            
            target.economy *= (1.0 - damage_percent / 100.0)
            imposer.economy *= 0.99 # 発動国も1%の経済遅滞ダメージを受ける
            
            # 制裁による支持率ペナルティ（ARCHITECTURE.md §2.3 準拠）
            target_approval_penalty = min(5.0, 1.0 * ratio)  # 対象国: GDP比率に応じて最大5%低下
            imposer_approval_penalty = 0.5  # 発動国: 常に0.5%低下
            target.approval_rating = max(0.0, target.approval_rating - target_approval_penalty)
            imposer.approval_rating = max(0.0, imposer.approval_rating - imposer_approval_penalty)
            self.sys_logs_this_turn.append(
                f"[制裁ダメージ] {sanction.imposer} -> {sanction.target} | "
                f"経済デバフ: -{damage_percent:.1f}% (発動国: -1.0%) | "
                f"支持率ペナルティ: 対象国 -{target_approval_penalty:.1f}%, 発動国 -{imposer_approval_penalty:.1f}%"
            )
