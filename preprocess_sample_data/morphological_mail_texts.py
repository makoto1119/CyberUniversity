#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# マスク済みメール → 形態素解析・ストップワード除去 → 最終ファイル出力

import os
import re
import shutil
from pathlib import Path
from janome.tokenizer import Tokenizer

# ストップワードの読み込み
def load_stopwords(path):
    if not path.exists():
        return set()
    with open(path, encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

# configファイル読み込み
def load_config(path="config"):
    cfg = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.strip().startswith("#"):
                key, value = line.strip().split("=", 1)
                cfg[key.strip()] = value.strip()
    return cfg

def main():
    config = load_config()
    MASKED_DIR = Path(config.get("MASKED_DIR", "./mail_mask"))
    OUTPUT_DIR = Path(config.get("MORPHOLOGICAL_DIR", "./mail_mask"))
    STOPWORDS_PATH = Path(config.get("STOPWORDS_PATH", "./sample_program/stopwords.txt"))

    tokenizer = Tokenizer()
    stopwords = load_stopwords(STOPWORDS_PATH)

    # OUTPUT_DIRを削除して初期化
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
        print(f"既存の {OUTPUT_DIR} を削除しました")

    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"{OUTPUT_DIR} を作成しました")

    dir_name = OUTPUT_DIR.name  # 保存ファイルのprefixに使用
    process_count = 0

    for i, file in enumerate(sorted(MASKED_DIR.glob("*.txt")), 1):
        with open(file, encoding="utf-8") as f:
            text = f.read()

        # Subject 部と本文の分離
        if "MailBody----\n" in text:
            subject_part, body_part = text.split("MailBody----\n", 1)
        else:
            subject_part, body_part = "", text

        tokens = []
        for token in tokenizer.tokenize(body_part):
            base = token.base_form
            if base in stopwords or re.fullmatch(r"\W+", base):
                continue
            tokens.append(base)

        tokenized_body = " ".join(tokens)
        result = f"{subject_part.strip()}\n\nMailBody----\n{tokenized_body}\n"

        # 元ファイルの連番を抽出
        match = re.search(r'mail_mask_(\d{3})\.txt$', file.name)
        if match:
            number = match.group(1)
            output_file = OUTPUT_DIR / f"{dir_name}_{number}.txt"
        else:
            output_file = OUTPUT_DIR / f"{dir_name}_unknown.txt"

        with open(output_file, "w", encoding="utf-8", newline="\n") as out:
            out.write(result)
            process_count += 1

    print(f"Completed: {process_count} files saved to '{OUTPUT_DIR}' に {dir_name}_NNN.txt 形式で保存しました")
    #print(f"[OK] {len(list(MASKED_DIR.glob('*.txt')))} 件を処理しました。")

if __name__ == "__main__":
    main()

