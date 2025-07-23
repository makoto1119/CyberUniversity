#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# メール本文のマスキング処理（氏名、メールアドレス、企業名など）

import re
import json
import shutil
from pathlib import Path

### for debug
import traceback
from inspect import currentframe

### for log
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

### functions
def chkprint(*args):
    names = {id(v):k for k,v in currentframe().f_back.f_locals.items()}
    print(', '.join(names.get(id(arg),'???')+' : '+str(type(arg))+' = '+repr(arg) for arg in args))

# JSON設定ファイルの読み込み
def load_config(path="rule_config.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def mask_text(text, filters):
    """
    テキストをマスク処理する
    filters: マスク処理の有効/無効を制御する辞書
    """
    stats = {
        'NAME': 0,
        'EMAIL': 0, 
        'COMPANY': 0,
        'URL': 0,
        'PROFILE': 0
    }
    
    # 氏名 → [NAME]
    if filters.get('name', True):
        text, count = re.subn(r'[一-龥]{2,3}(さん|様)?', '[NAME]', text)
        stats['NAME'] = count
    
    # メールアドレス → [EMAIL]
    if filters.get('email', True):
        text, count = re.subn(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+', '[EMAIL]', text)
        stats['EMAIL'] = count
    
    # 企業名 → [COMPANY]
    if filters.get('company', True):
        text, count = re.subn(r'株式会社[^\s\n　]+', '[COMPANY]', text)
        stats['COMPANY'] = count
    
    # URL → [URL]
    if filters.get('url', True):
        text, count = re.subn(r'https?://[^\s]+', '[URL]', text)
        stats['URL'] = count
    
    # 年齢/性別/国籍など → [PROFILE]
    if filters.get('profile', True):
        text, count = re.subn(r'\d+歳/[男女]/[一-龥]+', '[PROFILE]', text)
        stats['PROFILE'] = count
    
    return text, stats

def main():
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
    
    # DST_DIRを削除して初期化
    if DST_DIR.exists():
        shutil.rmtree(DST_DIR)
        print(f"既存の {DST_DIR} を削除しました")
    
    DST_DIR.mkdir(exist_ok=True)
    print(f"{DST_DIR} を作成しました")

    dir_name = DST_DIR.name  # 保存ファイルのprefixに使用
    process_count = 0
    
    # ログファイルの初期化
    log_file = Path("masked.log")
    with open(log_file, "w", encoding="utf-8") as log:
        log.write("元ファイル名,マスク後ファイル名,NAME,EMAIL,COMPANY,URL,PROFILE\n")

    for path in sorted(SRC_DIR.glob("mail_data_*.txt")):
        with open(path, encoding="utf-8") as f:
            content = f.read()

        masked_text, stats = mask_text(content, mask_filters)

        # 元ファイルの連番を抽出
        match = re.search(r'mail_data_(\d{3})\.txt$', path.name)
        if match:
            number = match.group(1)
            masked_filename = DST_DIR / f"{dir_name}_{number}.txt"
        else:
            masked_filename = DST_DIR / f"{dir_name}_unknown.txt"

        with open(masked_filename, "w", encoding="utf-8") as f:
            f.write(masked_text)
            process_count += 1
        
        # ログ出力
        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"{path.name},{masked_filename.name},{stats['NAME']},{stats['EMAIL']},{stats['COMPANY']},{stats['URL']},{stats['PROFILE']}\n")

    print(f"Completed: {process_count} files saved to '{DST_DIR}' に {dir_name}_NNN.txt 形式で保存しました")
    print(f"ログファイル : {log_file.resolve()} に処理結果を保存しました")

if __name__ == "__main__":
    main()
