#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# メール本文のマスキング処理（氏名、メールアドレス、企業名など）

import re
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

# 設定ファイルの読み込み
def load_config(path="config"):
    cfg = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.strip().startswith("#"):
                key, value = line.strip().split("=", 1)
                cfg[key.strip()] = value.strip()
    return cfg

def mask_text(text):
    # 氏名 → [NAME]
    text = re.sub(r'[一-龥]{2,3}(さん|様)?', '[NAME]', text)
    # メールアドレス → [EMAIL]
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+', '[EMAIL]', text)
    # 企業名 → [COMPANY]
    text = re.sub(r'株式会社[^\s\n　]+', '[COMPANY]', text)
    # URL → [URL]
    text = re.sub(r'https?://[^\s]+', '[URL]', text)
    # 年齢/性別/国籍など → [PROFILE]
    text = re.sub(r'\d+歳/[男女]/[一-龥]+', '[PROFILE]', text)
    return text

def main():
    config = load_config()
    SRC_DIR = Path(config.get("SAVE_DIR", "./mail_data"))
    DST_DIR = Path(config.get("MASK_DIR", "./mail_mask"))
    
    # DST_DIRを削除して初期化
    if DST_DIR.exists():
        shutil.rmtree(DST_DIR)
        print(f"既存の {DST_DIR} を削除しました")
    
    DST_DIR.mkdir(exist_ok=True)
    print(f"{DST_DIR} を作成しました")

    dir_name = DST_DIR.name  # 保存ファイルのprefixに使用

    for path in sorted(SRC_DIR.glob("mail_data_*.txt")):
        with open(path, encoding="utf-8") as f:
            content = f.read()

        masked = mask_text(content)

        # 元ファイルの連番を抽出
        match = re.search(r'mail_data_(\d{3})\.txt$', path.name)
        if match:
            number = match.group(1)
            masked_filename = DST_DIR / f"{dir_name}_{number}.txt"
        else:
            masked_filename = DST_DIR / f"{dir_name}_unknown.txt"

        with open(masked_filename, "w", encoding="utf-8") as f:
            f.write(masked)

    print(f"Success. : {DST_DIR.resolve()} に {dir_name}_NNN.txt 形式で保存しました")

if __name__ == "__main__":
    main()
