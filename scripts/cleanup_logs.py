import os
import glob
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
    """system_*.logファイル内の '(ターン N)' から最大ターン数を取得する"""
    max_turn = 0
    try:
        content = Path(file_path).read_text(encoding='utf-8')
        # '(ターン 9)' や '│ 🌍 Turn 1 (2025年 Q1) │' などのパターンを探す
        turns = re.findall(r'\(ターン (\d+)\)', content)
        turns += re.findall(r'Turn (\d+)', content)
        if turns:
            max_turn = max(int(t) for t in turns)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return max_turn

def cleanup_logs(threshold=3, days=None):
    """指定した条件以下のログファイルを削除する"""
    print(f"--- ログのクリーンアップを開始します ---")
    if threshold is not None:
        print(f" - 閾値(ターン): {threshold} ターン以下")
    if days is not None:
        print(f" - 閾値(日数): {days} 日以上経過")
    
    deleted_files = []
    
    current_time = time.time()
    
    def should_delete(file_path, max_turn):
        # 両方の条件が指定されている場合は AND
        turn_condition = threshold is None or max_turn <= threshold
        
        days_condition = True
        if days is not None and os.path.exists(file_path):
            file_age_days = (current_time - os.path.getmtime(file_path)) / 86400
            days_condition = file_age_days >= days
            
        return turn_condition and days_condition

    # 1. シミュレーションログ (.jsonl, .summary.json)
    jsonl_files = glob.glob("logs/simulations/sim_*.jsonl")
    for jsonl_path in jsonl_files:
        max_turn = get_max_turn_from_jsonl(jsonl_path)
        if should_delete(jsonl_path, max_turn):
            # 関連するファイルを特定
            base_path = jsonl_path.replace(".jsonl", "")
            summary_path = base_path + ".summary.json"
            
            # 削除
            for p in [jsonl_path, summary_path]:
                if os.path.exists(p):
                    os.remove(p)
                    deleted_files.append(p)
                    print(f"Deleted: {p} (Max Turn: {max_turn})")
            
            # DBディレクトリの削除
            session_id = os.path.basename(jsonl_path).replace("sim_", "").replace(".jsonl", "")
            db_dir = f"db/collection/diplomacy_events_{session_id}"
            if os.path.exists(db_dir):
                shutil.rmtree(db_dir)
                deleted_files.append(db_dir)
                print(f"Deleted DB: {db_dir}")
                    
    # 2. システムログ (logs/system/system_*.log)
    system_logs = glob.glob("logs/system/system_*.log")
    for log_path in system_logs:
        max_turn = get_max_turn_from_system_log(log_path)
        if should_delete(log_path, max_turn):
            if os.path.exists(log_path):
                os.remove(log_path)
                deleted_files.append(log_path)
                print(f"Deleted: {log_path} (Max Turn: {max_turn})")
            
            # DBディレクトリの削除 (シミュレーションログ削除で漏れた場合)
            session_id = os.path.basename(log_path).replace("system_", "").replace(".log", "")
            db_dir = f"db/collection/diplomacy_events_{session_id}"
            if os.path.exists(db_dir):
                shutil.rmtree(db_dir)
                deleted_files.append(db_dir)
                print(f"Deleted DB: {db_dir}")

    if not deleted_files:
        print("削除対象のファイルは見つかりませんでした。")
    else:
        print(f"\n合計 {len(deleted_files)} 個のファイルを削除しました。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="指定したターン数や日数以下のログファイルを削除します。")
    parser.add_argument("-t", "--threshold", type=int, default=None, help="削除するターン数の閾値 (例: 3ターン以下のログを削除。デフォルトは制限なし)")
    parser.add_argument("-d", "--days", type=int, default=None, help="削除する経過日数の閾値 (例: 7日以上前のログを削除。デフォルトは制限なし)")
    args = parser.parse_args()
    
    # 引数がどちらも指定されていない場合は、デフォルトで3ターン以下の削除を実行（後方互換性のため）
    if args.threshold is None and args.days is None:
        args.threshold = 3

    cleanup_logs(threshold=args.threshold, days=args.days)
