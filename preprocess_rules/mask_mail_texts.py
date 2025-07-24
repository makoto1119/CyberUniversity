#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メール本文のマスキング処理（氏名、メールアドレス、企業名など）
改善版：より精度の高いパターンマッチングを実装
"""

import re
import json
import shutil
from pathlib import Path
from mask_patterns import get_all_patterns

### for log
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def load_config(path="rule_config.json"):
    """JSON設定ファイルの読み込み"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def mask_text(text, filters):
    """
    テキストをマスク処理する
    Args:
        text (str): マスク対象のテキスト
        filters (dict): マスク処理の有効/無効を制御する辞書
    Returns:
        tuple: (マスク後のテキスト, 統計情報)
    """
    patterns = get_all_patterns()
    stats = {key: 0 for key in patterns.keys()}
    
    for mask_type, pattern_list in patterns.items():
        if filters.get(mask_type.lower(), True):
            for pattern in pattern_list:
                try:
                    text, count = re.subn(pattern, f'[{mask_type}]', text)
                    stats[mask_type] += count
                except re.error as e:
                    logger.error(f"正規表現エラー - パターン: {pattern}, エラー: {str(e)}")
                    continue
    
    return text, stats

def process_file(src_path, dst_path, mask_filters):
    """
    1つのファイルに対してマスク処理を実行
    Args:
        src_path (Path): 入力ファイルのパス
        dst_path (Path): 出力ファイルのパス
        mask_filters (dict): マスクフィルターの設定
    Returns:
        dict: 処理結果の統計情報
    """
    try:
        with open(src_path, encoding="utf-8") as f:
            content = f.read()
        
        masked_text, stats = mask_text(content, mask_filters)
        
        with open(dst_path, "w", encoding="utf-8") as f:
            f.write(masked_text)
        
        return {
            'src': src_path.name,
            'dst': dst_path.name,
            'stats': stats,
            'status': 'success'
        }
    except Exception as e:
        logger.error(f"ファイル処理エラー - ファイル: {src_path}, エラー: {str(e)}")
        return {
            'src': src_path.name,
            'dst': dst_path.name,
            'stats': {},
            'status': 'error',
            'error': str(e)
        }

def write_log(results, log_file):
    """
    処理結果をログファイルに書き込む
    Args:
        results (list): 処理結果のリスト
        log_file (Path): ログファイルのパス
    """
    with open(log_file, "w", encoding="utf-8") as log:
        # ヘッダー行
        log.write("元ファイル名,マスク後ファイル名,処理状態,NAME,EMAIL,COMPANY,URL,PROFILE\n")
        
        # 結果の書き込み
        for result in results:
            stats = result['stats']
            status = result['status']
            log.write(f"{result['src']},{result['dst']},{status}," + 
                     f"{stats.get('NAME', 0)},{stats.get('EMAIL', 0)}," +
                     f"{stats.get('COMPANY', 0)},{stats.get('URL', 0)}," +
                     f"{stats.get('PROFILE', 0)}\n")

def main():
    """メイン処理"""
    # 設定の読み込み
    config = load_config()
    SRC_DIR = Path(config["directories"]["save_dir"])
    DST_DIR = Path(config["directories"]["masked_dir"])
    
    # マスクフィルターの設定を取得
    mask_filters = config.get("mask_filters", {
        "name": True,
        "email": True,
        "company": True,
        "url": True,
        "profile": True
    })
    
    # 有効なフィルターの表示
    print("Active filters:")
    for filter_name, enabled in mask_filters.items():
        print(f"- {filter_name}: {'enabled' if enabled else 'disabled'}")
    
    # DST_DIRの初期化
    if DST_DIR.exists():
        shutil.rmtree(DST_DIR)
        print(f"既存の {DST_DIR} を削除しました")
    
    DST_DIR.mkdir(exist_ok=True)
    print(f"{DST_DIR} を作成しました")

    # ファイル処理
    results = []
    for src_path in sorted(SRC_DIR.glob("mail_data_*.txt")):
        # 出力ファイル名の生成
        match = re.search(r'mail_data_(\d+)\.txt$', src_path.name)
        number = match.group(1) if match else "unknown"
        # 数字の桁数を3桁に揃える（4桁以上の場合はそのまま）
        if number != "unknown":
            number = number.zfill(3) if len(number) <= 3 else number
        dst_path = DST_DIR / f"{DST_DIR.name}_{number}.txt"
        
        # ファイル処理の実行
        result = process_file(src_path, dst_path, mask_filters)
        results.append(result)
    
    # ログの出力
    log_file = Path("masked.log")
    write_log(results, log_file)
    
    # 処理結果のサマリー表示
    success_count = sum(1 for r in results if r['status'] == 'success')
    total_count = len(results)
    print(f"\n処理完了:")
    print(f"- 成功: {success_count}/{total_count} ファイル")
    print(f"- 保存先: '{DST_DIR}' ({DST_DIR.name}_NNN.txt 形式)")
    print(f"- ログファイル: {log_file.resolve()}")

if __name__ == "__main__":
    main()
