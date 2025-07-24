#!/bin/bash

file="labels.csv"

echo "クラスごとの件数:"
cat "$file" | cut -d',' -f2 | sort | uniq -c | sort -nr

echo "--------------------------"
total=$(cat "$file" | wc -l)
echo "$total : 合計"
