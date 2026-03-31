"""
HoI4/Grafana インスパイアのダークテーマ定義
地図レンダリング全体で使用するカラーパレットとスタイル設定
"""

# ---------------------------------------------------------
# カラーパレット
# ---------------------------------------------------------

# 背景・パネル
BG_COLOR = "#0d1117"           # メイン背景（GitHub Dark）
PANEL_COLOR = "#161b22"        # パネル背景
BORDER_COLOR = "#30363d"       # パネルボーダー・グリッドライン

# テキスト
TEXT_PRIMARY = "#c9d1d9"       # メインテキスト
TEXT_SECONDARY = "#8b949e"     # サブテキスト
TEXT_ACCENT = "#58a6ff"        # アクセントテキスト（リンク等）

# 地図
OCEAN_COLOR = "#1a1a2e"        # 海洋
NON_PARTICIPANT_COLOR = "#2d2d2d"  # 非参加国（チャコール）
COUNTRY_BORDER_COLOR = "#444c56"   # 国境線
PARTICIPANT_BORDER_COLOR = "#8b949e"  # 参加国間の国境線

# アクセント
ACCENT_CYAN = "#58a6ff"
ACCENT_ORANGE = "#f0883e"
ACCENT_GREEN = "#3fb950"
ACCENT_RED = "#f85149"
ACCENT_YELLOW = "#d29922"
ACCENT_PURPLE = "#bc8cff"

# 戦争関連
WAR_ARROW_COLOR = "#f85149"        # 進軍矢印
FORTRESS_COLOR = "#d29922"         # 要塞マーカー
BOMBARDMENT_LINE_COLOR = "#f0883e" # 艦砲射撃・爆撃線
TENSION_HIGH_COLOR = "#f85149"     # 高緊張度の国境ハイライト

# ユニットマーカー
UNIT_BORDER_COLOR = "#ffffff"      # ユニットマーカーの縁取り


# ---------------------------------------------------------
# フォント設定
# ---------------------------------------------------------

FONT_FAMILY = "sans-serif"  # Inter/Noto Sans JP にフォールバック
HEADER_FONT_SIZE = 16
SUBHEADER_FONT_SIZE = 11
LABEL_FONT_SIZE = 7
TABLE_FONT_SIZE = 8
UNIT_LABEL_FONT_SIZE = 5


# ---------------------------------------------------------
# レイアウト設定
# ---------------------------------------------------------

# 出力サイズ
FIGURE_WIDTH = 19.20    # インチ
FIGURE_HEIGHT = 10.80   # インチ
FIGURE_DPI = 100        # Full HD (1920x1080)

# GridSpec比率
HEADER_HEIGHT_RATIO = 0.5
MAP_HEIGHT_RATIO = 8.0
FOOTER_HEIGHT_RATIO = 1.5

# マージン
GRID_HSPACE = 0.05
GRID_WSPACE = 0.05
