"""
領土カラーリングレイヤー
GeoJSONから参加国/非参加国を塗り分ける
"""

import json
import os
import geopandas as gpd
from shapely.geometry import box
from typing import Dict, Optional

from map.styles import (
    NON_PARTICIPANT_COLOR, COUNTRY_BORDER_COLOR,
    PARTICIPANT_BORDER_COLOR, OCEAN_COLOR
)

# ---------------------------------------------------------
# GeoJSON ローダー & キャッシュ
# ---------------------------------------------------------

_geo_data_cache: Optional[gpd.GeoDataFrame] = None
_color_data_cache: Optional[Dict] = None


def _load_geodata() -> gpd.GeoDataFrame:
    """10m GeoJSON をロードしてキャッシュ"""
    global _geo_data_cache
    if _geo_data_cache is not None:
        return _geo_data_cache
    
    geojson_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "geo",
        "ne_10m_admin_0_countries.geojson"
    )
    gdf = gpd.read_file(geojson_path)
    
    # パフォーマンス: 頂点数を削減（tolerance=0.01度 ≈ 1km）
    gdf["geometry"] = gdf["geometry"].simplify(0.01, preserve_topology=True)
    
    _geo_data_cache = gdf
    return gdf


def _load_colors() -> Dict:
    """country_colors.json を読み込みキャッシュ"""
    global _color_data_cache
    if _color_data_cache is not None:
        return _color_data_cache
    
    colors_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "country_colors.json"
    )
    with open(colors_path, "r", encoding="utf-8") as f:
        _color_data_cache = json.load(f)
    return _color_data_cache


def get_country_polygon(iso_code: str) -> Optional[gpd.GeoDataFrame]:
    """ISO コードから国のポリゴンを取得"""
    gdf = _load_geodata()
    # Natural EarthではISO_A3カラムを使用
    # 台湾は特殊ケース（ISP_A3_EH = "TWN" の場合がある）
    match = gdf[gdf["ISO_A3"] == iso_code]
    if match.empty:
        # フォールバック: ISO_A3_EH を検索
        match = gdf[gdf["ISO_A3_EH"] == iso_code]
    if match.empty:
        # フォールバック2: ADM0_A3 を検索
        match = gdf[gdf["ADM0_A3"] == iso_code]
    return match if not match.empty else None


def draw_territories(ax, participant_iso_codes: Dict[str, str], 
                     country_colors_override: Optional[Dict] = None,
                     bbox: Optional[tuple] = None):
    """
    地図上に領土を描画する。
    
    Args:
        ax: matplotlib Axes
        participant_iso_codes: {"国名": "ISO_A3"} のマッピング
        country_colors_override: カラー上書き（オプション）
        bbox: 表示範囲 (minx, miny, maxx, maxy)。Noneなら東アジア〜太平洋
    """
    gdf = _load_geodata()
    colors = country_colors_override or _load_colors()
    
    # 参加国のISOコード一覧
    participant_codes = set(participant_iso_codes.values())
    
    # 非参加国の描画
    non_participant = gdf[
        ~gdf["ISO_A3"].isin(participant_codes) & 
        ~gdf["ISO_A3_EH"].isin(participant_codes) &
        ~gdf["ADM0_A3"].isin(participant_codes)
    ]
    non_participant.plot(
        ax=ax,
        color=NON_PARTICIPANT_COLOR,
        edgecolor=COUNTRY_BORDER_COLOR,
        linewidth=0.3,
        zorder=1
    )
    
    # 参加国の描画（国ごとに色を変える）
    for country_name, iso_code in participant_iso_codes.items():
        country_gdf = get_country_polygon(iso_code)
        if country_gdf is not None:
            color = colors.get(country_name, {}).get("primary", "#4a7a4a")
            country_gdf.plot(
                ax=ax,
                color=color,
                edgecolor=PARTICIPANT_BORDER_COLOR,
                linewidth=0.6,
                zorder=2,
                label=country_name
            )
    
    # 表示範囲の設定
    if bbox:
        ax.set_xlim(bbox[0], bbox[2])
        ax.set_ylim(bbox[1], bbox[3])
    else:
        # デフォルト: 東アジア〜太平洋 (自動計算)
        _auto_set_bounds(ax, participant_iso_codes)


def _auto_set_bounds(ax, participant_iso_codes: Dict[str, str]):
    """参加国のポリゴンに基づいて表示範囲を自動計算"""
    gdf = _load_geodata()
    participant_codes = set(participant_iso_codes.values())
    
    # 参加国のバウンディングボックスを算出
    all_bounds = []
    for iso_code in participant_codes:
        country = get_country_polygon(iso_code)
        if country is not None:
            bounds = country.total_bounds  # [minx, miny, maxx, maxy]
            all_bounds.append(bounds)
    
    if not all_bounds:
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        return
    
    import numpy as np
    all_bounds = np.array(all_bounds)
    minx = all_bounds[:, 0].min()
    miny = all_bounds[:, 1].min()
    maxx = all_bounds[:, 2].max()
    maxy = all_bounds[:, 3].max()
    
    # パディング（幅/高さの15%）
    pad_x = (maxx - minx) * 0.15
    pad_y = (maxy - miny) * 0.15
    
    # 最小表示範囲を保証（極端に小さい国のみの場合）
    min_span = 20.0
    if (maxx - minx) < min_span:
        center_x = (maxx + minx) / 2
        minx = center_x - min_span / 2
        maxx = center_x + min_span / 2
    if (maxy - miny) < min_span:
        center_y = (maxy + miny) / 2
        miny = center_y - min_span / 2
        maxy = center_y + min_span / 2
    
    ax.set_xlim(minx - pad_x, maxx + pad_x)
    ax.set_ylim(miny - pad_y, maxy + pad_y)
