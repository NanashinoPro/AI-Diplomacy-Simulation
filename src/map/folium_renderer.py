"""
Folium ベースのインタラクティブ戦略マップレンダラー
Google Map 風のズーム＆パン操作が可能な HTML マップを出力する。
Playwright による AI 自動スクリーンショット抽出に対応。
"""

import os
import json
import numpy as np
from typing import Dict, Optional, List
from collections import defaultdict

import folium
from folium import DivIcon, GeoJson, Marker, PolyLine
from folium.features import CustomIcon
from branca.element import MacroElement, Template

from models import WorldState, CountryState

from map.layers import _load_geodata, _load_colors, get_country_polygon
from map.military_units import (
    calc_army_position, calc_navy_position, calc_air_position,
    POSTURE_COLORS, NAVAL_MISSION_COLORS, AIR_MISSION_COLORS,
)
from map.styles import (
    BG_COLOR, PANEL_COLOR, BORDER_COLOR,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_ACCENT,
    OCEAN_COLOR, NON_PARTICIPANT_COLOR, COUNTRY_BORDER_COLOR,
    PARTICIPANT_BORDER_COLOR,
    ACCENT_GREEN, ACCENT_RED, ACCENT_YELLOW, ACCENT_CYAN, ACCENT_ORANGE,
)

# ワールドラッピング用の経度オフセット
WORLD_WRAP_OFFSETS = [0, 360, -360]


# ---------------------------------------------------------
# ユニットマーカーの HTML テンプレート
# ---------------------------------------------------------

_UNIT_HTML_TEMPLATE = """
<div style="
    display:flex; align-items:center; justify-content:center;
    width:{size}px; height:{size}px;
    background:{bg_color};
    border:2px solid {border_color};
    border-radius:{border_radius};
    color:#fff; font-size:{font_size}px; font-weight:bold;
    font-family:'Noto Sans JP',sans-serif;
    box-shadow:0 0 6px rgba(0,0,0,0.6);
    opacity:0.92;
    {extra_style}
">{label}</div>
"""

_POPUP_HTML_TEMPLATE = """
<div style="font-family:'Noto Sans JP',sans-serif;font-size:12px;min-width:160px;color:#c9d1d9;background:#161b22;padding:8px;border-radius:6px;">
    <div style="font-weight:bold;font-size:14px;margin-bottom:4px;color:{accent_color};">{unit_type_label}</div>
    <table style="width:100%;border-collapse:collapse;">
        <tr><td style="color:#8b949e;padding:2px 6px 2px 0;">配備元</td><td>{owner}</td></tr>
        <tr><td style="color:#8b949e;padding:2px 6px 2px 0;">対象</td><td>{target}</td></tr>
        <tr><td style="color:#8b949e;padding:2px 6px 2px 0;">数量</td><td>{quantity}</td></tr>
        <tr><td style="color:#8b949e;padding:2px 6px 2px 0;">任務/態勢</td><td style="color:{mission_color};">{mission}</td></tr>
    </table>
</div>
"""


# ---------------------------------------------------------
# 公開 API
# ---------------------------------------------------------

def render_turn_map_html(world_state: WorldState, output_dir: str = "output/maps",
                         bbox: Optional[tuple] = None) -> str:
    """
    1ターン分のインタラクティブ地図を HTML として出力する。

    Args:
        world_state: 現在の WorldState
        output_dir:  出力ディレクトリ
        bbox:        表示範囲 (minx, miny, maxx, maxy)

    Returns:
        出力された HTML のファイルパス
    """
    os.makedirs(output_dir, exist_ok=True)

    # 参加国情報
    participant_iso_codes: Dict[str, str] = {}
    for name, country in world_state.countries.items():
        if country.iso_code:
            participant_iso_codes[name] = country.iso_code

    # ---- ベースマップ ----
    center, zoom = _calc_initial_view(participant_iso_codes, bbox)
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="CartoDB dark_matter",
        attr='&copy; <a href="https://carto.com/">CARTO</a>',
        control_scale=True,
        prefer_canvas=True,
        world_copy_jump=False,
    )

    # ---- 領土レイヤー ----
    _add_territory_layer(m, participant_iso_codes)

    # ---- 軍事ユニットレイヤー ----
    _add_military_layer(m, world_state, participant_iso_codes)

    # ---- 戦争矢印レイヤー ----
    _add_war_arrows(m, world_state, participant_iso_codes)

    # ---- UI オーバーレイ（MacroElement で安全に注入） ----
    _add_overlays(m, world_state)

    # ---- 保存 ----
    output_path = os.path.join(output_dir, f"turn_{world_state.turn:03d}.html")
    m.save(output_path)
    return output_path


# ---------------------------------------------------------
# 初期ビュー算出
# ---------------------------------------------------------

def _calc_initial_view(participant_iso_codes: Dict[str, str],
                       bbox: Optional[tuple] = None) -> tuple:
    """参加国の地理的広がりから初期ビューを自動計算"""
    if bbox:
        center_lat = (bbox[1] + bbox[3]) / 2
        center_lon = (bbox[0] + bbox[2]) / 2
        span = max(bbox[2] - bbox[0], bbox[3] - bbox[1])
        zoom = max(2, int(8 - np.log2(max(span, 1))))
        return [center_lat, center_lon], zoom

    all_bounds = []
    for iso in participant_iso_codes.values():
        gdf = get_country_polygon(iso)
        if gdf is not None:
            all_bounds.append(gdf.total_bounds)

    if not all_bounds:
        return [35.0, 120.0], 4

    arr = np.array(all_bounds)
    minx, miny = arr[:, 0].min(), arr[:, 1].min()
    maxx, maxy = arr[:, 2].max(), arr[:, 3].max()

    center_lat = (miny + maxy) / 2
    center_lon = (minx + maxx) / 2
    span = max(maxx - minx, maxy - miny)
    zoom = max(2, min(10, int(8 - np.log2(max(span, 1)))))

    return [center_lat, center_lon], zoom


# ---------------------------------------------------------
# 領土レイヤー
# ---------------------------------------------------------

def _add_territory_layer(m: folium.Map, participant_iso_codes: Dict[str, str]):
    """GeoJSON で参加国の領土を描画（非参加国はタイルマップで表示）"""
    colors = _load_colors()

    # 参加国のみ描画（非参加国はCartoDB dark_matterタイルで自然に表示される）
    for country_name, iso in participant_iso_codes.items():
        country_gdf = get_country_polygon(iso)
        if country_gdf is None:
            continue

        # ポリゴン簡素化（HTMLサイズ削減 — 視覚的影響なし）
        simplified = country_gdf.copy()
        simplified["geometry"] = simplified.geometry.simplify(0.01)

        primary_color = colors.get(country_name, {}).get("primary", "#4a7a4a")

        # ワールドラッピング: 元の位置 + lon±360 に複製
        for lon_offset in WORLD_WRAP_OFFSETS:
            if lon_offset != 0:
                offset_gdf = simplified.copy()
                from shapely.affinity import translate
                offset_gdf["geometry"] = offset_gdf.geometry.apply(
                    lambda g: translate(g, xoff=lon_offset)
                )
                geo_data = offset_gdf.__geo_interface__
            else:
                geo_data = simplified.__geo_interface__

            GeoJson(
                geo_data,
                style_function=lambda _, c=primary_color: {
                    "fillColor": c,
                    "color": PARTICIPANT_BORDER_COLOR,
                    "weight": 1.0,
                    "fillOpacity": 0.65,
                },
                tooltip=folium.Tooltip(
                    f"<b>{country_name}</b>",
                    style="background:#161b22;color:#c9d1d9;border:1px solid #30363d;"
                          "border-radius:4px;padding:4px 8px;font-family:'Noto Sans JP',sans-serif;",
                ),
                name=f"{country_name}_off{lon_offset}",
            ).add_to(m)


# ---------------------------------------------------------
# 軍事ユニットレイヤー
# ---------------------------------------------------------

def _add_military_layer(m: folium.Map, world_state: WorldState,
                        participant_iso_codes: Dict[str, str]):
    """軍事ユニットマーカーを描画"""
    # ポリゴンキャッシュ
    polygons = {}
    for name, iso in participant_iso_codes.items():
        gdf = get_country_polygon(iso)
        if gdf is not None:
            poly = (gdf.geometry.union_all()
                    if hasattr(gdf.geometry, 'union_all')
                    else gdf.geometry.unary_union)
            polygons[name] = poly

    fg = folium.FeatureGroup(name="軍事ユニット")

    for country_name, country in world_state.countries.items():
        if country_name not in polygons:
            continue

        deployments = country.military_deployment.deployments
        if not deployments:
            continue

        self_poly = polygons[country_name]
        _add_country_units(fg, deployments, self_poly, polygons, country_name)

    fg.add_to(m)


def _add_country_units(fg: folium.FeatureGroup, deployments: list,
                       self_poly, target_polygons: Dict, country_name: str):
    """1カ国分の軍事ユニットマーカーを追加"""
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

    # ---- 陸軍 ----
    for target_name, army_list in army_by_target.items():
        target_poly = target_polygons.get(target_name)
        if target_poly is None:
            continue

        total_budget = sum(
            (d.budget_amount if hasattr(d, 'budget_amount') else d.get('budget_amount', 0.0))
            for d in army_list
        )
        if total_budget <= 0:
            continue

        x, y = calc_army_position(self_poly, target_poly, 0, 1)

        posture = army_list[0].posture if hasattr(army_list[0], 'posture') else 'defensive'
        posture_val = posture.value if hasattr(posture, 'value') else str(posture) if posture else 'defensive'
        color = POSTURE_COLORS.get(posture_val, ACCENT_GREEN)

        size = max(20, min(100, 20 + int(np.sqrt(total_budget) * 4.3)))
        icon_html = _UNIT_HTML_TEMPLATE.format(
            size=size, bg_color=color, border_color="#fff",
            border_radius="3px", font_size=max(9, size // 2),
            label=str(int(total_budget)), extra_style="",
        )

        popup_html = _POPUP_HTML_TEMPLATE.format(
            unit_type_label=f"🟩 陸軍",
            accent_color=color, owner=country_name,
            target=target_name, quantity=f"${total_budget:.1f}B",
            mission=posture_val.upper(), mission_color=color,
        )

        # ワールドラップ: 3箇所に複製
        for lon_offset in WORLD_WRAP_OFFSETS:
            Marker(
                location=[y, x + lon_offset],
                icon=DivIcon(html=icon_html, icon_size=(size, size),
                             icon_anchor=(size // 2, size // 2)),
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{country_name} 陸軍 ${total_budget:.1f}B",
            ).add_to(fg)

    # ---- 海軍 ----
    for target_name, navy_list in navy_by_target.items():
        target_poly = target_polygons.get(target_name)
        if target_poly is None:
            continue

        total_budget = sum(
            (d.budget_amount if hasattr(d, 'budget_amount') else d.get('budget_amount', 0.0))
            for d in navy_list
        )
        if total_budget <= 0:
            continue

        mission = navy_list[0].naval_mission if hasattr(navy_list[0], 'naval_mission') else 'patrol'
        mission_val = mission.value if hasattr(mission, 'value') else str(mission) if mission else 'patrol'

        x, y = calc_navy_position(self_poly, target_poly, 0, 1, mission_val)
        color = NAVAL_MISSION_COLORS.get(mission_val, ACCENT_CYAN)
        size = max(20, min(100, 20 + int(np.sqrt(total_budget) * 4.3)))

        icon_html = _UNIT_HTML_TEMPLATE.format(
            size=size, bg_color=color, border_color="#fff",
            border_radius="50%", font_size=max(9, size // 2),
            label=str(int(total_budget)),
            extra_style="transform:rotate(45deg);",
        )

        popup_html = _POPUP_HTML_TEMPLATE.format(
            unit_type_label=f"🔷 海軍",
            accent_color=color, owner=country_name,
            target=target_name, quantity=f"${total_budget:.1f}B",
            mission=mission_val.upper().replace("_", " "), mission_color=color,
        )

        # ワールドラップ: 3箇所に複製
        for lon_offset in WORLD_WRAP_OFFSETS:
            Marker(
                location=[y, x + lon_offset],
                icon=DivIcon(html=icon_html, icon_size=(size, size),
                             icon_anchor=(size // 2, size // 2)),
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{country_name} 海軍 ${total_budget:.1f}B",
            ).add_to(fg)

    # ---- 空軍 ----
    for target_name, air_list in air_by_target.items():
        target_poly = target_polygons.get(target_name)
        if target_poly is None:
            continue

        total_budget = sum(
            (d.budget_amount if hasattr(d, 'budget_amount') else d.get('budget_amount', 0.0))
            for d in air_list
        )
        if total_budget <= 0:
            continue

        mission = air_list[0].air_mission if hasattr(air_list[0], 'air_mission') else 'air_superiority'
        mission_val = mission.value if hasattr(mission, 'value') else str(mission) if mission else 'air_superiority'

        x, y = calc_air_position(self_poly, target_poly, mission_val, 0)
        color = AIR_MISSION_COLORS.get(mission_val, ACCENT_CYAN)
        size = max(20, min(100, 20 + int(np.sqrt(total_budget) * 4.3)))

        # 三角形のCSS
        icon_html = _UNIT_HTML_TEMPLATE.format(
            size=size, bg_color=color, border_color="#fff",
            border_radius="3px 3px 50% 50%", font_size=max(9, size // 2),
            label=str(int(total_budget)), extra_style="",
        )

        popup_html = _POPUP_HTML_TEMPLATE.format(
            unit_type_label=f"🔺 空軍",
            accent_color=color, owner=country_name,
            target=target_name, quantity=f"${total_budget:.1f}B",
            mission=mission_val.upper().replace("_", " "), mission_color=color,
        )

        # ワールドラップ: 3箇所に複製
        for lon_offset in WORLD_WRAP_OFFSETS:
            Marker(
                location=[y, x + lon_offset],
                icon=DivIcon(html=icon_html, icon_size=(size, size),
                             icon_anchor=(size // 2, size // 2)),
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{country_name} 空軍 ${total_budget:.1f}B",
            ).add_to(fg)


# ---------------------------------------------------------
# 戦争矢印
# ---------------------------------------------------------

def _add_war_arrows(m: folium.Map, world_state: WorldState,
                    participant_iso_codes: Dict[str, str]):
    """交戦国間に進軍ラインを描画"""
    if not world_state.active_wars:
        return

    fg = folium.FeatureGroup(name="戦争")

    for war in world_state.active_wars:
        agg_iso = participant_iso_codes.get(war.aggressor)
        def_iso = participant_iso_codes.get(war.defender)
        if not agg_iso or not def_iso:
            continue

        agg_gdf = get_country_polygon(agg_iso)
        def_gdf = get_country_polygon(def_iso)
        if agg_gdf is None or def_gdf is None:
            continue

        agg_c = (agg_gdf.geometry.union_all().centroid
                 if hasattr(agg_gdf.geometry, 'union_all')
                 else agg_gdf.geometry.unary_union.centroid)
        def_c = (def_gdf.geometry.union_all().centroid
                 if hasattr(def_gdf.geometry, 'union_all')
                 else def_gdf.geometry.unary_union.centroid)

        progress = war.target_occupation_progress
        weight = 2 + (progress / 100.0) * 4

        # ワールドラップ: 戦争矢印も3箇所に複製
        for lon_offset in WORLD_WRAP_OFFSETS:
            PolyLine(
                locations=[[agg_c.y, agg_c.x + lon_offset],
                           [def_c.y, def_c.x + lon_offset]],
                color=ACCENT_RED,
                weight=weight,
                opacity=0.7,
                dash_array="10 6",
                tooltip=f"⚔ {war.aggressor} → {war.defender} (占領 {progress:.0f}%)",
            ).add_to(fg)

    fg.add_to(m)


# ---------------------------------------------------------
# オーバーレイ（MacroElement で安全に注入）
# ---------------------------------------------------------

def _add_overlays(m: folium.Map, world_state: WorldState):
    """ヘッダー・テーブル・Playwright hookをJavaScriptで安全に注入"""
    header_html = _build_header_html(world_state)
    table_html = _build_country_table_html(world_state)

    # HTMLをエスケープしてJSの文字列として注入
    import html as html_mod
    combined_html = header_html + table_html

    # JavaScript経由でDOMに注入（Foliumの初期化後に実行される）
    # Note: script.add_child は自動的に<script>タグ内に配置されるため、
    # 内側に<script>タグを入れてはいけない
    js_code = f"""
    (function() {{
        var overlayHTML = {repr(combined_html)};
        var container = document.createElement('div');
        container.innerHTML = overlayHTML;
        document.body.appendChild(container);

        // Playwright用: Leaflet mapインスタンスをグローバルに公開
        setTimeout(function() {{
            for (var k in window) {{
                try {{
                    if (window[k] instanceof L.Map) {{
                        window.__map = window[k];
                        break;
                    }}
                }} catch(e) {{}}
            }}
        }}, 500);
    }})();
    """
    m.get_root().script.add_child(folium.Element(js_code))


def _build_header_html(world_state: WorldState) -> str:
    """ターン情報のヘッダー HTML を生成"""
    n_wars = len(world_state.active_wars)
    n_countries = len(world_state.countries)

    war_badge = ""
    if n_wars > 0:
        war_badge = (
            f'<span style="margin-left:12px;color:{ACCENT_RED};font-size:13px;">'
            f'⚔ CONFLICTS: {n_wars}</span>'
        )

    return f"""
    <div style="
        position:fixed; top:10px; left:60px; z-index:9999;
        background:{PANEL_COLOR}ee; border:1px solid {BORDER_COLOR};
        border-radius:8px; padding:8px 16px;
        font-family:'Noto Sans JP',monospace,sans-serif;
        box-shadow:0 2px 12px rgba(0,0,0,0.5);
        display:flex; align-items:center; gap:12px;
        pointer-events:none;
    ">
        <span style="color:{TEXT_ACCENT};font-size:18px;font-weight:bold;">
            TURN {world_state.turn}
        </span>
        <span style="color:{BORDER_COLOR};font-size:16px;">│</span>
        <span style="color:{TEXT_PRIMARY};font-size:14px;">
            Q{world_state.quarter} {world_state.year}
        </span>
        <span style="color:{BORDER_COLOR};font-size:16px;">│</span>
        <span style="color:{TEXT_SECONDARY};font-size:12px;">
            AI DIPLOMACY SIMULATION
        </span>
        <span style="color:{BORDER_COLOR};font-size:16px;">│</span>
        <span style="color:{ACCENT_GREEN};font-size:13px;">
            NATIONS: {n_countries}
        </span>
        {war_badge}
    </div>
    """


def _build_country_table_html(world_state: WorldState) -> str:
    """国家一覧テーブルの HTML を生成"""
    colors = _load_colors()

    rows_html = ""
    for name, country in world_state.countries.items():
        color = colors.get(name, {}).get("primary", "#4a7a4a")

        approval = country.approval_rating
        if approval >= 50:
            ap_color = ACCENT_GREEN
        elif approval >= 30:
            ap_color = ACCENT_YELLOW
        else:
            ap_color = ACCENT_RED

        gov = "DEM" if country.government_type.value == "democracy" else "AUT"
        gov_color = ACCENT_CYAN if gov == "DEM" else ACCENT_ORANGE

        status = _get_country_status(name, world_state)
        if "WAR" in status:
            st_color = ACCENT_RED
        elif "TENSION" in status:
            st_color = ACCENT_YELLOW
        else:
            st_color = ACCENT_GREEN

        rows_html += f"""
        <tr>
            <td><span style="display:inline-block;width:10px;height:10px;
                background:{color};border-radius:2px;"></span></td>
            <td>{name}</td>
            <td>{country.economy:,.0f}</td>
            <td>{country.military:,.0f}</td>
            <td style="color:{ap_color};">{approval:.0f}%</td>
            <td>{country.population:.1f}</td>
            <td style="color:{gov_color};font-weight:bold;">{gov}</td>
            <td style="color:{st_color};">{status}</td>
        </tr>
        """

    return f"""
    <div id="country-table-panel" style="
        position:fixed; bottom:10px; right:10px; z-index:9999;
        background:{PANEL_COLOR}ee; border:1px solid {BORDER_COLOR};
        border-radius:8px; padding:10px 14px;
        font-family:'Noto Sans JP',monospace,sans-serif;
        box-shadow:0 2px 12px rgba(0,0,0,0.5);
        max-height:300px; overflow-y:auto;
        font-size:11px; color:{TEXT_PRIMARY};
    ">
        <table style="border-collapse:collapse;width:100%;">
            <thead>
                <tr style="color:{TEXT_SECONDARY};font-size:10px;border-bottom:1px solid {BORDER_COLOR};">
                    <th></th><th style="text-align:left;padding:2px 6px;">NAME</th>
                    <th style="text-align:right;padding:2px 6px;">GDP</th>
                    <th style="text-align:right;padding:2px 6px;">MIL</th>
                    <th style="text-align:right;padding:2px 6px;">APPR</th>
                    <th style="text-align:right;padding:2px 6px;">POP</th>
                    <th style="text-align:center;padding:2px 6px;">GOV</th>
                    <th style="text-align:left;padding:2px 6px;">STATUS</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """


# ---------------------------------------------------------
# ユーティリティ
# ---------------------------------------------------------

def _get_country_status(country_name: str, world_state: WorldState) -> str:
    """国の現在のステータス文字列を返す"""
    for war in world_state.active_wars:
        if war.aggressor == country_name:
            return "WAR(ATK)"
        if war.defender == country_name:
            return "WAR(DEF)"
    return "PEACE"

