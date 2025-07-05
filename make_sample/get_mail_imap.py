#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Gmail IMAP接続 & メール取得（件名と本文）+ 自動フォーマット処理

import os
import email
import re
from email.header import decode_header
from imapclient import IMAPClient
from datetime import datetime
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

def decode_subject(encoded_subject):
    """
    エンコードされた件名をデコードして日本語化する
    """
    try:
        # 複数行にわたるエンコードされた件名を1行にまとめる
        subject_line = re.sub(r'\n\s+', '', encoded_subject)
        
        # decode_headerを使用してデコード
        decoded_parts = decode_header(subject_line)
        decoded_subject = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded_subject += part.decode(encoding)
                else:
                    # エンコーディングが不明な場合はUTF-8で試す
                    try:
                        decoded_subject += part.decode('utf-8')
                    except UnicodeDecodeError:
                        decoded_subject += part.decode('iso-2022-jp', errors='ignore')
            else:
                decoded_subject += part
        
        return decoded_subject
    except Exception as e:
        print(f"Error: Subject decode failed - {e}")
        return encoded_subject

def normalize_line_endings(text):
    """
    改行コードをLF(\n)に統一する
    """
    # CRLF(\r\n)とCR(\r)をLF(\n)に変換
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    return text

def format_mail_content(subject, body):
    """
    メール内容をフォーマットする
    - 件名をデコード
    - 件名と本文の間に2行の空行を追加
    - 本文の前に区切り線を追加
    - 改行コードを統一
    """
    # 件名をデコード
    decoded_subject = decode_subject(subject)
    
    # 本文の改行コードを統一
    formatted_body = normalize_line_endings(body)
    
    # フォーマットされた内容を作成
    formatted_content = f"Subject: {decoded_subject}\n\n\nMailBody----\n{formatted_body}"
    
    return formatted_content

# 設定読み込み（key=value形式）
def load_config(path="config"):
    cfg = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.strip().startswith("#"):
                key, value = line.strip().split("=", 1)
                cfg[key.strip()] = value.strip()
    return cfg

def main():
    """
    メイン処理
    """
    print("=== Gmail IMAP Mail Fetcher & Processor ===")
    
    # 設定ロード
    try:
        config = load_config()
        print("OK: Config file loaded")
    except Exception as e:
        print(f"Error: Failed to load config file - {e}")
        print("Please ensure 'config' file exists and has correct format")
        return
    
    EMAIL_ADDRESS  = config["EMAIL_ADDRESS"]
    EMAIL_PASSWORD = config["EMAIL_PASSWORD"]
    DATE_SINCE     = config.get("DATE_SINCE", "01-Jul-2025")
    MAX_MAILS      = int(config.get("MAX_MAILS", 10))
    SAVE_DIR       = Path(config.get("SAVE_DIR", "./mails"))
    LABEL_NAME     = config.get("LABEL_NAME", "")  # ラベル指定（空の場合はINBOX）
    
    # 保存ディレクトリ作成
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Email Address: {EMAIL_ADDRESS}")
    print(f"Date Since: {DATE_SINCE}")
    print(f"Max Mails: {MAX_MAILS}")
    print(f"Save Directory: {SAVE_DIR.resolve()}")
    print(f"Target Label: {LABEL_NAME if LABEL_NAME else 'INBOX'}")
    
    try:
        # IMAP接続
        print("\nConnecting to Gmail IMAP server...")
        server = IMAPClient('imap.gmail.com', ssl=True)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print("OK: Login successful")
        
        # フォルダ選択（ラベル指定がある場合はそのラベル、なければINBOX）
        if LABEL_NAME:
            try:
                server.select_folder(LABEL_NAME)
                print(f"OK: Selected label '{LABEL_NAME}'")
            except Exception as e:
                print(f"Warning: Label '{LABEL_NAME}' not found. Using INBOX instead")
                print(f"Available folders/labels: {list(server.list_folders())}")
                server.select_folder('INBOX')
        else:
            server.select_folder('INBOX')
            print("OK: Selected INBOX")
        
        # メール取得
        print(f"\nSearching for mails since {DATE_SINCE}...")
        messages = server.search(['SINCE', DATE_SINCE])
        
        if not messages:
            print("Warning: No mails found matching the criteria")
            server.logout()
            return
        
        uids = messages[-MAX_MAILS:]  # 最新のMAX_MAILS件を取得
        print(f"OK: Found {len(uids)} mails to process")
        
        fetched = server.fetch(uids, ['RFC822'])
        
        for i, (uid, data) in enumerate(fetched.items()):
            raw_email = data[b'RFC822']
            msg = email.message_from_bytes(raw_email)
            subject = msg.get("Subject", f"no-subject-{i}")
            filename = SAVE_DIR / f"mail_{i+1:03}.txt"
            
            # 本文抽出（簡略化）
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode(
                                part.get_content_charset() or "utf-8", errors="ignore"
                            )
                            break
                        except Exception:
                            continue
            else:
                try:
                    body = msg.get_payload(decode=True).decode(
                        msg.get_content_charset() or "utf-8", errors="ignore"
                    )
                except Exception:
                    body = str(msg.get_payload())
            
            # メール内容をフォーマット（件名デコード + 構造化）
            formatted_content = format_mail_content(subject, body)
            
            # 保存（UTF-8、LF改行で保存）
            with open(filename, "w", encoding="utf-8", newline='\n') as f:
                f.write(formatted_content)
        
        server.logout()
        print(f"\nCompleted: {len(fetched)} mails saved")
        
    except Exception as e:
        print(f"Error: Processing failed - {e}")
        print("Details:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
