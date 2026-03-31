"""
軍事ユニットマーカー描画モジュール
師団・艦隊・飛行隊・要塞のマーカーを地図上に描画する
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from shapely.ops import nearest_points
from shapely.geometry import Point

from map.styles import (
    UNIT_BORDER_COLOR, WAR_ARROW_COLOR, FORTRESS_COLOR,
    BOMBARDMENT_LINE_COLOR, UNIT_LABEL_FONT_SIZE,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_RED, ACCENT_ORANGE,
    ACCENT_PURPLE, ACCENT_YELLOW
)

# ---------------------------------------------------------
# ユニットマーカーの形状とサイズ
# ---------------------------------------------------------

ARMY_MARKER = "s"       # 四角（陸軍）
NAVY_MARKER = "D"       # ダイヤモンド（海軍）
AIR_MARKER = "^"        # 三角（空軍）
FORTRESS_MARKER = "p"   # 五角形（要塞）

MARKER_SIZE_BASE = 40
MARKER_ALPHA = 0.85

# 態勢/ミッションごとのカラー
POSTURE_COLORS = {
    "offensive": ACCENT_RED,
    "defensive": ACCENT_GREEN,
    "intimidation": ACCENT_ORANGE,
}

NAVAL_MISSION_COLORS = {
    "patrol": ACCENT_CYAN,
    "show_of_force": ACCENT_ORANGE,
    "blockade": ACCENT_RED,
    "naval_engagement": ACCENT_RED,
    "amphibious_support": ACCENT_PURPLE,
    "shore_bombardment": ACCENT_ORANGE,
}

AIR_MISSION_COLORS = {
    "air_superiority": ACCENT_CYAN,
    "ground_support": ACCENT_GREEN,
    "strategic_bombing": ACCENT_RED,
    "recon_flight": ACCENT_YELLOW,
}


# ---------------------------------------------------------
# 座標算出
# ---------------------------------------------------------

def calc_army_position(self_poly, target_poly, unit_index: int, total_units: int) -> Tuple[float, float]:
    """
    陸軍の配備座標を算出する。
    """
    p_self, p_target = nearest_points(self_poly, target_poly)
    
    # 共有国境の検出
    shared_border = self_poly.boundary.intersection(target_poly.boundary)
    
    if not shared_border.is_empty and shared_border.length > 0:
        # 共有国境がある場合：国境線に沿って等間隔配置
        if total_units == 1:
            fraction = 0.5
        else:
            fraction = unit_index / (total_units - 1)
        
        border_point = shared_border.interpolate(fraction, normalized=True)
        centroid = self_poly.centroid
        dx = centroid.x - border_point.x
        dy = centroid.y - border_point.y
        offset_ratio = 0.10
        
        final_x = border_point.x + dx * offset_ratio
        final_y = border_point.y + dy * offset_ratio
    else:
        # 共有国境がない場合（海を挟んだ国）
        centroid = self_poly.centroid
        dx = centroid.x - p_self.x
        dy = centroid.y - p_self.y
        offset_ratio = 0.25
        
        base_x = p_self.x + dx * offset_ratio
        base_y = p_self.y + dy * offset_ratio
        
        dist = max(1e-6, np.sqrt(dx**2 + dy**2))
        perp_dx = -dy / dist
        perp_dy = dx / dist
        spread = (unit_index - total_units / 2) * 0.5
        
        final_x = base_x + perp_dx * spread
        final_y = base_y + perp_dy * spread
    
    # ポリゴン内に収まることを保証
    point = Point(final_x, final_y)
    if not self_poly.contains(point):
        final_point = self_poly.boundary.interpolate(
            self_poly.boundary.project(point)
        )
        final_x, final_y = final_point.x, final_point.y
    
    return (final_x, final_y)


def calc_navy_position(self_poly, target_poly, unit_index: int, total_fleets: int, 
                       mission: str = "patrol") -> Tuple[float, float]:
    """海軍の配備座標を算出"""
    p_self, p_target = nearest_points(self_poly, target_poly)
    
    mid_x = (p_self.x + p_target.x) / 2
    mid_y = (p_self.y + p_target.y) / 2
    
    # ミッションに応じた位置調整
    dx = p_target.x - p_self.x
    dy = p_target.y - p_self.y
    
    if mission in ("patrol",):
        # 自国寄り
        mid_x = p_self.x + dx * 0.3
        mid_y = p_self.y + dy * 0.3
    elif mission in ("show_of_force", "blockade", "shore_bombardment"):
        # 相手国寄り
        mid_x = p_self.x + dx * 0.7
        mid_y = p_self.y + dy * 0.7
    
    # 複数艦隊の分散
    dist = max(1e-6, np.sqrt(dx**2 + dy**2))
    perp_dx = -dy / dist
    perp_dy = dx / dist
    spread = (unit_index - total_fleets / 2) * 0.4
    
    final_x = mid_x + perp_dx * spread
    final_y = mid_y + perp_dy * spread
    
    # 陸地に配置されないことを保証
    point = Point(final_x, final_y)
    if self_poly.contains(point) or target_poly.contains(point):
        final_x = (p_self.x + p_target.x) / 2
        final_y = (p_self.y + p_target.y) / 2
    
    return (final_x, final_y)


def calc_air_position(self_poly, target_poly, mission: str, unit_index: int) -> Tuple[float, float]:
    """空軍の配備座標を算出"""
    centroid = self_poly.centroid
    
    if mission in ("air_superiority", "ground_support"):
        return (centroid.x + unit_index * 0.3, centroid.y + 0.5)
    elif mission in ("strategic_bombing", "recon_flight"):
        target_centroid = target_poly.centroid
        dx = target_centroid.x - centroid.x
        dy = target_centroid.y - centroid.y
        return (centroid.x + dx * 0.2 + unit_index * 0.2,
                centroid.y + dy * 0.2)
    return (centroid.x, centroid.y)


# ---------------------------------------------------------
# ユニット描画
# ---------------------------------------------------------

def draw_military_units(ax, deployments: list, self_polygon, target_polygons: Dict,
                        country_name: str):
    """
    軍事ユニットを地図上に描画する。
    
    Args:
        ax: matplotlib Axes
        deployments: MilitaryDeploymentOrder のリスト
        self_polygon: 自国のShapelyポリゴン
        target_polygons: {"国名": Shapelyポリゴン} のマッピング
        country_name: 自国名
    """
    if not deployments:
        return
    
    # target_country ごとにグルーピング
    from collections import defaultdict
    army_by_target = defaultdict(list)
    navy_by_target = defaultdict(list)
    air_by_target = defaultdict(list)
    
    for d in deployments:
        d_type = d.type if hasattr(d, 'type') else d.get('type', '')
        d_type_val = d_type.value if hasattr(d_type, 'value') else str(d_type)
        target = d.target_country if hasattr(d, 'target_country') else d.get('target_country', '')
        
        if d_type_val == "army":
            army_by_target[target].append(d)
        elif d_type_val == "navy":
            navy_by_target[target].append(d)
        elif d_type_val == "air":
            air_by_target[target].append(d)
    
    # 陸軍描画
    for target_name, army_list in army_by_target.items():
        target_poly = target_polygons.get(target_name)
        if target_poly is None:
            continue
        
        total_divs = sum(
            (d.divisions if hasattr(d, 'divisions') else d.get('divisions', 0))
            for d in army_list
        )
        if total_divs == 0:
            continue
        
        # 代表点を1つ計算（全師団を1つのマーカーで表現）
        x, y = calc_army_position(self_polygon, target_poly, 0, 1)
        
        posture = army_list[0].posture if hasattr(army_list[0], 'posture') else army_list[0].get('posture', 'defensive')
        posture_val = posture.value if hasattr(posture, 'value') else str(posture) if posture else 'defensive'
        color = POSTURE_COLORS.get(posture_val, ACCENT_GREEN)
        
        # 師団数に応じたマーカーサイズ
        size = MARKER_SIZE_BASE + total_divs * 8
        
        ax.scatter(x, y, marker=ARMY_MARKER, c=color, s=size,
                   edgecolors=UNIT_BORDER_COLOR, linewidth=0.5,
                   alpha=MARKER_ALPHA, zorder=10)
        ax.annotate(f"{total_divs}", (x, y), fontsize=UNIT_LABEL_FONT_SIZE,
                    color='white', ha='center', va='center',
                    fontweight='bold', zorder=11)
    
    # 海軍描画
    for target_name, navy_list in navy_by_target.items():
        target_poly = target_polygons.get(target_name)
        if target_poly is None:
            continue
        
        total_fleets = sum(
            (d.fleets if hasattr(d, 'fleets') else d.get('fleets', 0))
            for d in navy_list
        )
        if total_fleets == 0:
            continue
        
        mission = navy_list[0].naval_mission if hasattr(navy_list[0], 'naval_mission') else navy_list[0].get('naval_mission', 'patrol')
        mission_val = mission.value if hasattr(mission, 'value') else str(mission) if mission else 'patrol'
        
        x, y = calc_navy_position(self_polygon, target_poly, 0, 1, mission_val)
        color = NAVAL_MISSION_COLORS.get(mission_val, ACCENT_CYAN)
        size = MARKER_SIZE_BASE + total_fleets * 10
        
        ax.scatter(x, y, marker=NAVY_MARKER, c=color, s=size,
                   edgecolors=UNIT_BORDER_COLOR, linewidth=0.5,
                   alpha=MARKER_ALPHA, zorder=10)
        ax.annotate(f"{total_fleets}", (x, y), fontsize=UNIT_LABEL_FONT_SIZE,
                    color='white', ha='center', va='center',
                    fontweight='bold', zorder=11)
    
    # 空軍描画
    for target_name, air_list in air_by_target.items():
        target_poly = target_polygons.get(target_name)
        if target_poly is None:
            continue
        
        total_sq = sum(
            (d.squadrons if hasattr(d, 'squadrons') else d.get('squadrons', 0))
            for d in air_list
        )
        if total_sq == 0:
            continue
        
        mission = air_list[0].air_mission if hasattr(air_list[0], 'air_mission') else air_list[0].get('air_mission', 'air_superiority')
        mission_val = mission.value if hasattr(mission, 'value') else str(mission) if mission else 'air_superiority'
        
        x, y = calc_air_position(self_polygon, target_poly, mission_val, 0)
        color = AIR_MISSION_COLORS.get(mission_val, ACCENT_CYAN)
        size = MARKER_SIZE_BASE + total_sq * 8
        
        ax.scatter(x, y, marker=AIR_MARKER, c=color, s=size,
                   edgecolors=UNIT_BORDER_COLOR, linewidth=0.5,
                   alpha=MARKER_ALPHA, zorder=10)
        ax.annotate(f"{total_sq}", (x, y), fontsize=UNIT_LABEL_FONT_SIZE,
                    color='white', ha='center', va='center',
                    fontweight='bold', zorder=11)
        
        # 爆撃/偵察任務の場合は矢印を描画
        if mission_val in ("strategic_bombing", "recon_flight"):
            target_centroid = target_poly.centroid
            ax.annotate("", xy=(target_centroid.x, target_centroid.y),
                        xytext=(x, y),
                        arrowprops=dict(
                            arrowstyle="->",
                            color=BOMBARDMENT_LINE_COLOR if mission_val == "strategic_bombing" else ACCENT_YELLOW,
                            linestyle="--",
                            linewidth=1.0,
                            alpha=0.7
                        ),
                        zorder=9)
