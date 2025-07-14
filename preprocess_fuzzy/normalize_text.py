#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 表記ゆれ（ゆらぎ）統一スクリプト

import json
import re
from pathlib import Path

def load_patterns(json_path):
    with open(json_path, encoding='utf-8') as f:
        patterns = json.load(f)
    return patterns

def normalize_text(text, patterns):
    for standard, variants in patterns.items():
        for variant in variants:
            text = re.sub(re.escape(variant), standard, text)
    return text

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', required=True, help='入力テキストファイル')
    parser.add_argument('--outfile', required=True, help='出力先ファイル')
    parser.add_argument('--patterns', default='fuzzy_patterns.json', help='パターン定義ファイル')
    args = parser.parse_args()

    patterns = load_patterns(args.patterns)

    with open(args.infile, encoding='utf-8') as f:
        content = f.read()

    normalized = normalize_text(content, patterns)

    with open(args.outfile, 'w', encoding='utf-8') as f:
        f.write(normalized)

    print(f"変換完了: {args.outfile}")

if __name__ == '__main__':
    main()
