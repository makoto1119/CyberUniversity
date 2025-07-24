#!/bin/bash


### ここを変更して再開ポイントを指定
from="mail_data_151.txt"


mail_dir="../shared_mail_data"
label_output="labels.csv_sav"

#echo "filename,label" > "$label_output"

skip=true  # 再開フラグ

for mail_file in $(ls $mail_dir/mail_data_*.txt | sort -V); do
    filename=$(basename "$mail_file")

    # 再開判定
    if $skip; then
        if [[ "$filename" == "$from" ]]; then
            skip=false
        else
            continue
        fi
    fi

    num=$(echo "$filename" | grep -o '[0-9]\+' | tail -1)
    num_padded=$(echo "$filename" | sed -E 's/^mail_data_([0-9]+)\.txt$/\1/')
    paired_text="texts_fuzzy_${num_padded}.txt"

    echo "=============================="
    echo "元ファイル: $filename"
    echo "対応テキスト: $paired_text"
    echo "------------------------------"
    less "$mail_file"

    echo
    echo "この文書のカテゴリは？"
    echo "  [1] project_info"
    echo "  [2] engineer_info"
    echo "  [3] other_info"
    echo -n "番号を選んでください [1〜3, s=スキップ, q=終了]: "
    read -r answer

    case "$answer" in
        1)
            echo "$paired_text,project_info" >> "$label_output"
            ;;
        2)
            echo "$paired_text,engineer_info" >> "$label_output"
            ;;
        3)
            echo "$paired_text,other_info" >> "$label_output"
            ;;
        s|S)
            echo "スキップ: $filename"
            ;;
        q|Q)
            echo "中断します"
            break
            ;;
        *)
            echo "無効な入力。スキップします。"
            ;;
    esac
done

