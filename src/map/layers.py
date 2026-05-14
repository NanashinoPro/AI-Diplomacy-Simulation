"""
領土カラーリングレイヤー
GeoJSONから参加国/非参加国を塗り分ける。
国家分裂時のポリゴン機械分割とランタイムキャッシュを含む。
"""

import colorsys
import json
import math
import os
import random as _random

import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, MultiPolygon, Polygon, GeometryCollection
from shapely.ops import split
from typing import Dict, List, Optional, Tuple

from map.styles import (
    NON_PARTICIPANT_COLOR, COUNTRY_BORDER_COLOR,
    PARTICIPANT_BORDER_COLOR, OCEAN_COLOR
)

# ---------------------------------------------------------
# GeoJSON ローダー & キャッシュ
# ---------------------------------------------------------

_geo_data_cache: Optional[gpd.GeoDataFrame] = None
_color_data_cache: Optional[Dict] = None

# 分裂国家のポリゴンキャッシュ
# key: 国名, value: gpd.GeoDataFrame (1行のGeoDataFrame)
_split_polygon_cache: Dict[str, gpd.GeoDataFrame] = {}


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


# ---------------------------------------------------------
# ランダムカラー生成（HSLベース）
# ---------------------------------------------------------

def _hex_to_hsl(hex_color: str) -> Tuple[float, float, float]:
    """HEXカラー → HSL (H: 0-360, S: 0-1, L: 0-1)"""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360.0, s, l


def _hsl_to_hex(h: float, s: float, l: float) -> str:
    """HSL (H: 0-360, S: 0-1, L: 0-1) → HEXカラー"""
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def _get_existing_hues() -> List[float]:
    """既存の全カラー定義から色相(H)のリストを取得"""
    colors = _load_colors()
    hues = []
    for name, color_dict in colors.items():
        if name.startswith("_"):
            continue
        primary = color_dict.get("primary", "")
        if primary and len(primary) == 7:
            try:
                h, _, _ = _hex_to_hsl(primary)
                hues.append(h)
            except (ValueError, IndexError):
                pass
    return hues


def _assign_dynamic_color(country_name: str) -> Dict:
    """
    分裂で生まれた新国家にHSLランダムでユニークなカラーを割り当てる。
    既存色の色相と最低30°離れた色を選定する。
    """
    global _color_data_cache
    
    colors = _load_colors()
    
    # 既に色が割り当てられていればスキップ
    if country_name in colors:
        return colors[country_name]
    
    existing_hues = _get_existing_hues()
    min_hue_distance = 30.0  # 既存色との最小色相差
    
    # 最大100回試行して十分離れた色相を見つける
    best_hue = 0.0
    best_min_dist = 0.0
    
    for _ in range(100):
        candidate_hue = _random.uniform(0, 360)
        
        if not existing_hues:
            best_hue = candidate_hue
            break
        
        # 全既存色との最小色相距離を計算（円環距離）
        min_dist = min(
            min(abs(candidate_hue - eh), 360 - abs(candidate_hue - eh))
            for eh in existing_hues
        )
        
        if min_dist >= min_hue_distance:
            best_hue = candidate_hue
            break
        
        # 最も離れた候補を記録（フォールバック用）
        if min_dist > best_min_dist:
            best_min_dist = min_dist
            best_hue = candidate_hue
    
    # primary: S=65%, L=50% / secondary: S=60%, L=65% / accent: S=70%, L=45%
    primary = _hsl_to_hex(best_hue, 0.65, 0.50)
    secondary = _hsl_to_hex(best_hue, 0.60, 0.65)
    military_accent = _hsl_to_hex(best_hue, 0.70, 0.45)
    
    color_entry = {
        "primary": primary,
        "secondary": secondary,
        "military_accent": military_accent,
    }
    
    # キャッシュに追加（ファイルは変更しない — ランタイムのみ）
    colors[country_name] = color_entry
    
    return color_entry


# ---------------------------------------------------------
# ポリゴン取得（統一API）
# ---------------------------------------------------------

def get_country_polygon(iso_code: str) -> Optional[gpd.GeoDataFrame]:
    """ISO コードから国のポリゴンを取得（GeoJSON原本から）"""
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


def get_display_polygon(country_name: str, iso_code: str) -> Optional[gpd.GeoDataFrame]:
    """
    国の表示用ポリゴンを取得する統一API。
    分割キャッシュを優先し、なければGeoJSON原本にフォールバック。
    
    Args:
        country_name: 国名（分裂国家のキャッシュキーとして使用）
        iso_code: ISO 3166-1 alpha-3 コード
    
    Returns:
        GeoDataFrame（1行）またはNone
    """
    # 分割キャッシュを優先
    if country_name in _split_polygon_cache:
        return _split_polygon_cache[country_name]
    
    # GeoJSON原本にフォールバック
    return get_country_polygon(iso_code)


# ---------------------------------------------------------
# ポリゴン機械分割エンジン
# ---------------------------------------------------------

def _make_cutting_line(centroid_x: float, centroid_y: float,
                       angle: float, offset: float,
                       extent: float) -> LineString:
    """
    切断線を生成する。
    
    Args:
        centroid_x, centroid_y: ポリゴン重心
        angle: 分割方向の角度（ラジアン）
        offset: angle方向への平行移動距離
        extent: 線の長さ（バウンディングボックスの対角線長 × 3）
    
    Returns:
        切断用LineString
    """
    # offset分だけangle方向に平行移動した点を基準にする
    px = centroid_x + offset * math.cos(angle)
    py = centroid_y + offset * math.sin(angle)
    
    # 切断線はangleに垂直な方向
    perp_angle = angle + math.pi / 2
    dx = math.cos(perp_angle) * extent
    dy = math.sin(perp_angle) * extent
    
    return LineString([(px - dx, py - dy), (px + dx, py + dy)])


def _classify_split_result(geoms, angle: float,
                           centroid_x: float,
                           centroid_y: float) -> Tuple[list, list]:
    """
    分割結果のジオメトリを「angle側」と「反angle側」の2グループに分類する。
    各ジオメトリの重心がangle方向のどちら側にあるかで判定。
    
    Returns:
        (positive_side, negative_side) — 各要素はShapelyジオメトリのリスト
    """
    positive_side = []  # angle方向（新国家側）
    negative_side = []  # 反angle方向（旧国家側）
    
    dir_x = math.cos(angle)
    dir_y = math.sin(angle)
    
    for geom in geoms:
        if geom.is_empty:
            continue
        gc = geom.centroid
        # 重心からのangle方向への射影
        proj = (gc.x - centroid_x) * dir_x + (gc.y - centroid_y) * dir_y
        if proj >= 0:
            positive_side.append(geom)
        else:
            negative_side.append(geom)
    
    return positive_side, negative_side


def _geom_list_to_geometry(geom_list: list):
    """ジオメトリリストを1つのPolygon/MultiPolygonにまとめる"""
    if not geom_list:
        return Polygon()
    
    # ネストされたGeometryCollectionを展開
    flat = []
    for g in geom_list:
        if isinstance(g, GeometryCollection):
            flat.extend(g.geoms)
        else:
            flat.append(g)
    
    # Polygonのみ抽出（LineStringやPointを除外）
    polygons = [g for g in flat if isinstance(g, (Polygon, MultiPolygon))]
    if not polygons:
        return Polygon()
    
    if len(polygons) == 1:
        return polygons[0]
    
    # MultiPolygonを展開して1つのMultiPolygonにまとめる
    all_polys = []
    for p in polygons:
        if isinstance(p, MultiPolygon):
            all_polys.extend(p.geoms)
        else:
            all_polys.append(p)
    
    return MultiPolygon(all_polys) if len(all_polys) > 1 else all_polys[0]


def _geometry_to_gdf(geometry) -> gpd.GeoDataFrame:
    """Shapelyジオメトリを1行のGeoDataFrameに変換"""
    return gpd.GeoDataFrame(geometry=[geometry], crs="EPSG:4326")


def split_polygon_for_fragmentation(old_name: str, new_name: str,
                                     iso_code: str, split_ratio: float,
                                     max_iter: int = 30,
                                     tolerance: float = 0.05) -> bool:
    """
    国家分裂時にポリゴンを機械的に分割する。
    
    ランダムな方角から切断線を引き、二分探索で面積比をsplit_ratioに収束させる。
    結果は _split_polygon_cache に保存される。
    
    Args:
        old_name: 旧国家名
        new_name: 新国家名
        iso_code: 旧国家のISO_A3コード
        split_ratio: 新国家が取得する面積比 (0.0-1.0)
        max_iter: 二分探索の最大反復回数
        tolerance: 面積比の許容誤差
    
    Returns:
        分割に成功したかどうか
    """
    # ソースポリゴンの取得（キャッシュ優先 → GeoJSON原本）
    source_gdf = get_display_polygon(old_name, iso_code)
    if source_gdf is None:
        return False
    
    # ジオメトリの統合
    source_poly = (source_gdf.geometry.union_all()
                   if hasattr(source_gdf.geometry, 'union_all')
                   else source_gdf.geometry.unary_union)
    
    if source_poly.is_empty:
        return False
    
    total_area = source_poly.area
    target_new_area = total_area * split_ratio
    
    # ランダムな分割角度を生成
    angle = _random.uniform(0, 2 * math.pi)
    
    centroid = source_poly.centroid
    cx, cy = centroid.x, centroid.y
    
    # バウンディングボックスから切断線の長さと探索範囲を決定
    minx, miny, maxx, maxy = source_poly.bounds
    extent = math.sqrt((maxx - minx)**2 + (maxy - miny)**2) * 3
    
    # angle方向の探索範囲: 重心から±extent
    search_range = extent / 2
    lo = -search_range
    hi = search_range
    
    best_new_geom = None
    best_old_geom = None
    best_error = float('inf')
    
    for iteration in range(max_iter):
        offset = (lo + hi) / 2
        
        line = _make_cutting_line(cx, cy, angle, offset, extent)
        
        try:
            result = split(source_poly, line)
        except Exception:
            # splitが失敗した場合（トポロジーエラー等）、offsetをずらす
            lo = offset
            continue
        
        if len(result.geoms) < 2:
            # 切断線がポリゴンを横切らなかった場合
            # offset方向を調整
            # ポリゴン全体がpositive側にある → loを上げる
            positive, negative = _classify_split_result(
                [source_poly], angle, cx, cy
            )
            if positive:
                hi = offset
            else:
                lo = offset
            continue
        
        # 分割結果を2グループに分類
        positive_geoms, negative_geoms = _classify_split_result(
            result.geoms, angle, cx, cy
        )
        
        new_geom = _geom_list_to_geometry(positive_geoms)
        old_geom = _geom_list_to_geometry(negative_geoms)
        
        # いずれかが空の場合のフォールバック
        if new_geom.is_empty or old_geom.is_empty:
            if new_geom.is_empty:
                lo = offset
            else:
                hi = offset
            continue
        
        current_ratio = new_geom.area / total_area
        error = abs(current_ratio - split_ratio)
        
        if error < best_error:
            best_error = error
            best_new_geom = new_geom
            best_old_geom = old_geom
        
        if error <= tolerance:
            break
        
        # 二分探索: offsetを増やすとpositive側面積が減る
        # 新国家の面積が大きすぎる → offset を増やして面積を減らす
        if current_ratio > split_ratio:
            lo = offset
        else:
            hi = offset
    
    # 分割結果の保存
    if best_new_geom is not None and best_old_geom is not None:
        _split_polygon_cache[new_name] = _geometry_to_gdf(best_new_geom)
        _split_polygon_cache[old_name] = _geometry_to_gdf(best_old_geom)
        return True
    
    return False


def transfer_polygon_on_defeat(defeated_name: str, victor_name: str):
    """
    国家消滅時にポリゴンを勝者に移管する。
    敗者のポリゴンを勝者に統合し、敗者をキャッシュから削除する。
    """
    defeated_poly = _split_polygon_cache.pop(defeated_name, None)
    if defeated_poly is None:
        return
    
    victor_gdf = _split_polygon_cache.get(victor_name)
    if victor_gdf is None:
        # 勝者がキャッシュにない場合、敗者のポリゴンをそのまま引き継ぐ
        _split_polygon_cache[victor_name] = defeated_poly
        return
    
    # 勝者と敗者のポリゴンを統合
    victor_poly = (victor_gdf.geometry.union_all()
                   if hasattr(victor_gdf.geometry, 'union_all')
                   else victor_gdf.geometry.unary_union)
    defeated_geometry = (defeated_poly.geometry.union_all()
                         if hasattr(defeated_poly.geometry, 'union_all')
                         else defeated_poly.geometry.unary_union)
    
    merged = victor_poly.union(defeated_geometry)
    _split_polygon_cache[victor_name] = _geometry_to_gdf(merged)


# ---------------------------------------------------------
# 領土描画
# ---------------------------------------------------------

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
    
    # 参加国の描画（国ごとに色を変える — 分割ポリゴン対応）
    for country_name, iso_code in participant_iso_codes.items():
        country_gdf = get_display_polygon(country_name, iso_code)
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
    # 参加国のバウンディングボックスを算出
    all_bounds = []
    for country_name, iso_code in participant_iso_codes.items():
        country = get_display_polygon(country_name, iso_code)
        if country is not None:
            bounds = country.total_bounds  # [minx, miny, maxx, maxy]
            all_bounds.append(bounds)
    
    if not all_bounds:
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        return
    
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
