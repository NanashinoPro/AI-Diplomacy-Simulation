import os
import json
import re
import time
from pathlib import Path
import argparse
import shutil

def get_max_turn_from_jsonl(file_path):
    """.jsonlファイルの最終行からターン数を取得する"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines:
                return 0
            last_line = lines[-1]
            data = json.loads(last_line)
            return data.get('turn', 0)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

def get_max_turn_from_system_log(file_path):
    """system.logファイル内の '(ターン N)' や 'Turn N' から最大ターン数を取得する"""
    max_turn = 0
    try:
        content = Path(file_path).read_text(encoding='utf-8')
        # '(ターン 9)' や 'Turn 1' などのパターンを探す
        turns = re.findall(r'\(ターン (\d+)\)', content)
        turns += re.findall(r'Turn (\d+)', content)
        if turns:
            max_turn = max(int(t) for t in turns)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return max_turn

def cleanup_logs(threshold=3, days=None, dry_run=False):
    """指定した条件以下のセッションディレクトリを削除する
    
    新形式: logs/{session_id}/ 以下に simulation.jsonl, system.log, html/, png/ が格納される
    """
    print(f"--- ログのクリーンアップを開始します ---")
    if threshold is not None:
        print(f" - 閾値(ターン): {threshold} ターン以下")
    if days is not None:
        print(f" - 閾値(日数): {days} 日以上経過")
    
    deleted_items = []
    
    current_time = time.time()
    logs_dir = Path("logs")
    
    if not logs_dir.exists():
        print("logs/ ディレクトリが存在しません。")
        return

    def should_delete(ref_path, max_turn):
        """削除条件を判定する"""
        # ターン条件
        turn_condition = threshold is None or max_turn <= threshold
        
        # 日数条件
        days_condition = True
        if days is not None and os.path.exists(ref_path):
            file_age_days = (current_time - os.path.getmtime(ref_path)) / 86400
            days_condition = file_age_days >= days
            
        return turn_condition and days_condition

    # セッションディレクトリを走査
    for session_dir in sorted(logs_dir.iterdir()):
        if not session_dir.is_dir():
            continue
        
        session_id = session_dir.name
        
        # 隠しディレクトリやその他の非セッションディレクトリをスキップ
        if session_id.startswith('.'):
            continue
            
        jsonl_path = session_dir / "simulation.jsonl"
        system_log_path = session_dir / "system.log"
        
        # どちらかのログファイルが存在しなければスキップ
        if not jsonl_path.exists() and not system_log_path.exists():
            continue
        
        # ターン数の判定: jsonl優先、なければsystem.logから取得
        max_turn = 0
        if jsonl_path.exists():
            max_turn = get_max_turn_from_jsonl(str(jsonl_path))
        if max_turn == 0 and system_log_path.exists():
            max_turn = get_max_turn_from_system_log(str(system_log_path))
        
        # 日数判定用の参照パス（ディレクトリの更新日時を使用）
        ref_path = str(session_dir)
        
        if should_delete(ref_path, max_turn):
            if dry_run:
                # DRY RUN: 表示のみ
                print(f"[DRY RUN] 削除対象: {session_dir} (Max Turn: {max_turn})")
                deleted_items.append(str(session_dir))
                db_dir = Path(f"db/collection/diplomacy_events_{session_id}")
                if db_dir.exists():
                    print(f"[DRY RUN] 削除対象 DB: {db_dir}")
                    deleted_items.append(str(db_dir))
            else:
                # セッションディレクトリ全体を削除
                shutil.rmtree(str(session_dir))
                deleted_items.append(str(session_dir))
                print(f"Deleted: {session_dir} (Max Turn: {max_turn})")
                
                # 関連するDBディレクトリの削除
                db_dir = Path(f"db/collection/diplomacy_events_{session_id}")
                if db_dir.exists():
                    shutil.rmtree(str(db_dir))
                    deleted_items.append(str(db_dir))
                    print(f"Deleted DB: {db_dir}")

    if not deleted_items:
        print("削除対象のファイルは見つかりませんでした。")
    else:
        print(f"\n合計 {len(deleted_items)} 個のディレクトリを削除しました。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="指定したターン数や日数以下のログセッションを削除します。")
    parser.add_argument("-t", "--threshold", type=int, default=None, help="削除するターン数の閾値 (例: 3ターン以下のログを削除。デフォルトは制限なし)")
    parser.add_argument("-d", "--days", type=int, default=None, help="削除する経過日数の閾値 (例: 7日以上前のログを削除。デフォルトは制限なし)")
    parser.add_argument("--dry-run", action="store_true", help="実際には削除せず、削除対象のみ表示する")
    args = parser.parse_args()
    
    # 引数がどちらも指定されていない場合は、デフォルトで3ターン以下の削除を実行（後方互換性のため）
    if args.threshold is None and args.days is None:
        args.threshold = 3

    if args.dry_run:
        print("[DRY RUN モード] 実際の削除は行いません。")
    
    cleanup_logs(threshold=args.threshold, days=args.days, dry_run=args.dry_run)
