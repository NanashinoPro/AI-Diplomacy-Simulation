"""
3段レイアウト・ダッシュボードレンダラー
ヘッダー（ターン情報） → メイン（地図） → フッター（国家一覧テーブル）
"""

import os
import matplotlib
matplotlib.use("Agg")  # GUIなし
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 日本語フォントの設定（macOS: Hiragino Sans）
plt.rcParams["font.family"] = ["Hiragino Sans", "Hiragino Kaku Gothic Pro", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch
import numpy as np

from typing import Dict, Optional
from models import WorldState, CountryState

from map.styles import (
    BG_COLOR, PANEL_COLOR, BORDER_COLOR,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_ACCENT,
    OCEAN_COLOR, ACCENT_GREEN, ACCENT_RED, ACCENT_YELLOW, ACCENT_CYAN, ACCENT_ORANGE,
    FIGURE_WIDTH, FIGURE_HEIGHT, FIGURE_DPI,
    HEADER_HEIGHT_RATIO, MAP_HEIGHT_RATIO, FOOTER_HEIGHT_RATIO,
    HEADER_FONT_SIZE, SUBHEADER_FONT_SIZE, TABLE_FONT_SIZE, LABEL_FONT_SIZE
)
from map.layers import draw_territories, get_country_polygon
from map.military_units import draw_military_units


def render_turn_map(world_state: WorldState, output_dir: str = "output/maps",
                    bbox: Optional[tuple] = None) -> str:
    """
    1ターン分のダッシュボード地図をPNGとして出力する。
    
    Args:
        world_state: 現在のWorldState
        output_dir: 出力ディレクトリ
        bbox: 表示範囲 (minx, miny, maxx, maxy)
    
    Returns:
        出力されたPNGのファイルパス
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 参加国情報の収集
    participant_iso_codes = {}
    for name, country in world_state.countries.items():
        if country.iso_code:
            participant_iso_codes[name] = country.iso_code
    
    # ----- Figure作成 -----
    fig = plt.figure(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT), dpi=FIGURE_DPI,
                     facecolor=BG_COLOR)
    
    gs = GridSpec(3, 1, figure=fig,
                  height_ratios=[HEADER_HEIGHT_RATIO, MAP_HEIGHT_RATIO, FOOTER_HEIGHT_RATIO],
                  hspace=0.03)
    
    # =================== ヘッダー ===================
    ax_header = fig.add_subplot(gs[0])
    ax_header.set_facecolor(PANEL_COLOR)
    ax_header.set_xlim(0, 1)
    ax_header.set_ylim(0, 1)
    ax_header.axis("off")
    
    # ターン情報
    turn_text = f"TURN {world_state.turn}"
    time_text = f"Q{world_state.quarter} {world_state.year}"
    title_text = "AI DIPLOMACY SIMULATION MONITOR"
    
    ax_header.text(0.02, 0.5, turn_text, fontsize=HEADER_FONT_SIZE + 4,
                   color=TEXT_ACCENT, fontweight="bold",
                   va="center", family="monospace")
    ax_header.text(0.15, 0.5, f"│  {time_text}", fontsize=HEADER_FONT_SIZE,
                   color=TEXT_PRIMARY, va="center", family="monospace")
    ax_header.text(0.35, 0.5, f"│  {title_text}", fontsize=HEADER_FONT_SIZE - 2,
                   color=TEXT_SECONDARY, va="center", family="monospace")
    
    # アクティブな戦争の数
    n_wars = len(world_state.active_wars)
    n_countries = len(world_state.countries)
    status_text = f"NATIONS: {n_countries}"
    if n_wars > 0:
        status_text += f"  │  ⚔ ACTIVE CONFLICTS: {n_wars}"
    ax_header.text(0.98, 0.5, status_text, fontsize=SUBHEADER_FONT_SIZE,
                   color=ACCENT_RED if n_wars > 0 else ACCENT_GREEN,
                   va="center", ha="right", family="monospace")
    
    # ヘッダー下のボーダーライン
    ax_header.axhline(y=0, color=BORDER_COLOR, linewidth=1.0)
    
    # =================== 地図 ===================
    ax_map = fig.add_subplot(gs[1])
    ax_map.set_facecolor(OCEAN_COLOR)
    ax_map.axis("off")
    
    # 領土描画
    draw_territories(ax_map, participant_iso_codes, bbox=bbox)
    
    # 軍事ユニット描画
    _draw_all_military_units(ax_map, world_state, participant_iso_codes)
    
    # 戦争の進軍矢印
    _draw_war_arrows(ax_map, world_state, participant_iso_codes)
    
    # =================== フッター（国家一覧テーブル） ===================
    ax_footer = fig.add_subplot(gs[2])
    ax_footer.set_facecolor(PANEL_COLOR)
    ax_footer.axis("off")
    
    _draw_country_table(ax_footer, world_state)
    
    # ----- 保存 -----
    output_path = os.path.join(output_dir, f"turn_{world_state.turn:03d}.png")
    fig.savefig(output_path, dpi=FIGURE_DPI, bbox_inches="tight",
                facecolor=BG_COLOR, edgecolor="none",
                pad_inches=0.1)
    plt.close(fig)
    
    return output_path


def _draw_all_military_units(ax, world_state: WorldState, 
                             participant_iso_codes: Dict[str, str]):
    """全国の軍事ユニットを描画"""
    # 各国のポリゴンをキャッシュ
    polygons = {}
    for name, iso in participant_iso_codes.items():
        gdf = get_country_polygon(iso)
        if gdf is not None:
            # MultiPolygon の場合は union で1つにまとめる
            poly = gdf.geometry.union_all() if hasattr(gdf.geometry, 'union_all') else gdf.geometry.unary_union
            polygons[name] = poly
    
    for name, country in world_state.countries.items():
        if name not in polygons:
            continue
        
        deployments = country.military_deployment.deployments
        if not deployments:
            continue
        
        draw_military_units(
            ax=ax,
            deployments=deployments,
            self_polygon=polygons[name],
            target_polygons=polygons,
            country_name=name
        )


def _draw_war_arrows(ax, world_state: WorldState, participant_iso_codes: Dict[str, str]):
    """交戦中の国家間に進軍矢印を描画"""
    for war in world_state.active_wars:
        agg_iso = participant_iso_codes.get(war.aggressor)
        def_iso = participant_iso_codes.get(war.defender)
        
        if not agg_iso or not def_iso:
            continue
        
        agg_gdf = get_country_polygon(agg_iso)
        def_gdf = get_country_polygon(def_iso)
        
        if agg_gdf is None or def_gdf is None:
            continue
        
        agg_centroid = agg_gdf.geometry.union_all().centroid if hasattr(agg_gdf.geometry, 'union_all') else agg_gdf.geometry.unary_union.centroid
        def_centroid = def_gdf.geometry.union_all().centroid if hasattr(def_gdf.geometry, 'union_all') else def_gdf.geometry.unary_union.centroid
        
        # 占領進捗に応じた矢印の太さ
        progress = war.target_occupation_progress / 100.0
        lw = 1.0 + progress * 3.0
        
        ax.annotate("", xy=(def_centroid.x, def_centroid.y),
                     xytext=(agg_centroid.x, agg_centroid.y),
                     arrowprops=dict(
                         arrowstyle="-|>",
                         color=ACCENT_RED,
                         linewidth=lw,
                         alpha=0.6 + progress * 0.3
                     ),
                     zorder=8)
        
        # 占領進捗率のラベル
        mid_x = (agg_centroid.x + def_centroid.x) / 2
        mid_y = (agg_centroid.y + def_centroid.y) / 2
        ax.text(mid_x, mid_y + 0.5, f"{war.target_occupation_progress:.0f}%",
                fontsize=LABEL_FONT_SIZE, color=ACCENT_RED,
                ha='center', va='center', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor=BG_COLOR, 
                          edgecolor=ACCENT_RED, alpha=0.8),
                zorder=12)


def _draw_country_table(ax, world_state: WorldState):
    """フッターに国家一覧テーブルを描画"""
    countries = list(world_state.countries.items())
    n = len(countries)
    if n == 0:
        return
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # ヘッダー行
    headers = ["", "NAME", "GDP", "MILITARY", "APPROVAL", "POP(M)", "GOV", "STATUS"]
    col_x = [0.01, 0.04, 0.22, 0.35, 0.50, 0.62, 0.72, 0.83]
    
    header_y = 0.90
    for i, h in enumerate(headers):
        ax.text(col_x[i], header_y, h, fontsize=TABLE_FONT_SIZE,
                color=TEXT_SECONDARY, fontweight="bold", va="center")
    
    # データ行
    row_height = min(0.15, 0.75 / max(1, n))
    
    from map.layers import _load_colors
    colors = _load_colors()
    
    for idx, (name, country) in enumerate(countries):
        y = header_y - (idx + 1) * row_height
        
        # カラーインジケーター
        color = colors.get(name, {}).get("primary", "#4a7a4a")
        ax.scatter(col_x[0] + 0.01, y, marker="s", c=color, s=60,
                   edgecolors=BORDER_COLOR, linewidth=0.5, zorder=5)
        
        # 国名
        ax.text(col_x[1], y, name, fontsize=TABLE_FONT_SIZE,
                color=TEXT_PRIMARY, va="center")
        
        # GDP
        gdp_str = f"{country.economy:,.0f}"
        ax.text(col_x[2], y, gdp_str, fontsize=TABLE_FONT_SIZE,
                color=TEXT_PRIMARY, va="center")
        
        # 軍事力
        mil_str = f"{country.military:,.0f}"
        ax.text(col_x[3], y, mil_str, fontsize=TABLE_FONT_SIZE,
                color=TEXT_PRIMARY, va="center")
        
        # 支持率
        approval = country.approval_rating
        approval_color = ACCENT_GREEN if approval >= 50 else (ACCENT_YELLOW if approval >= 30 else ACCENT_RED)
        ax.text(col_x[4], y, f"{approval:.0f}%", fontsize=TABLE_FONT_SIZE,
                color=approval_color, va="center")
        
        # 人口
        ax.text(col_x[5], y, f"{country.population:.1f}", fontsize=TABLE_FONT_SIZE,
                color=TEXT_PRIMARY, va="center")
        
        # 体制
        gov = "DEM" if country.government_type.value == "democracy" else "AUT"
        gov_color = ACCENT_CYAN if gov == "DEM" else ACCENT_ORANGE
        ax.text(col_x[6], y, gov, fontsize=TABLE_FONT_SIZE,
                color=gov_color, va="center", fontweight="bold")
        
        # 状態
        status = _get_country_status(name, world_state)
        status_color = ACCENT_RED if "WAR" in status else (ACCENT_YELLOW if "TENSION" in status else ACCENT_GREEN)
        ax.text(col_x[7], y, status, fontsize=TABLE_FONT_SIZE,
                color=status_color, va="center")


def _get_country_status(country_name: str, world_state: WorldState) -> str:
    """国の現在のステータス文字列を返す"""
    for war in world_state.active_wars:
        if war.aggressor == country_name:
            return f"WAR(ATK)"
        if war.defender == country_name:
            return f"WAR(DEF)"
    return "PEACE"
