#!/bin/bash

# ZIPファイル名の生成（例：mails_20250706_1430.zip）
TIMESTAMP=$(date +"%Y%m%d_%H%M")
ZIP_NAME="mail_mask_${TIMESTAMP}.zip"


# === 設定ファイルの読み込み（key=value形式） ===
CONFIG_FILE="./config"

# configファイルの存在チェック
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: config ファイルが見つかりません"
  exit 1
fi

# configから MASK_DIR の読み込み
MASK_DIR=$(grep '^MASK_DIR=' "$CONFIG_FILE" | cut -d '=' -f2)

# ディレクトリ存在チェック
if [ ! -d "$MASK_DIR" ]; then
  echo "Error: MASK_DIR ディレクトリが存在しません: $MASK_DIR"
  exit 1
fi

# mail_*.txt をまとめて ZIP 化
zip -j "$ZIP_NAME" "$MASK_DIR"/mail_*.txt

# 結果表示
if [ $? -eq 0 ]; then
  echo "OK: ZIP作成成功: $ZIP_NAME"
  mv ./${ZIP_NAME} ~/Desktop/
else
  echo "NG: ZIP作成に失敗しました"
  exit 1
fi

