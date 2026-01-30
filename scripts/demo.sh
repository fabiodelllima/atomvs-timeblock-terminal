#!/bin/bash
# Demo interativa do TimeBlock Organizer

set -e
DB_TEMP=$(mktemp -d)/demo.db
export TIMEBLOCK_DB_PATH="$DB_TEMP"

echo "=== TimeBlock Organizer Demo ==="
echo ""

echo '$ timeblock init'
timeblock init
sleep 1

echo ""
echo '$ timeblock routine create "Manhã Produtiva"'
timeblock routine create "Manhã Produtiva"
sleep 1

echo ""
echo '$ timeblock habit create --routine 1 --title "Exercício" --start 06:00 --end 07:00 --repeat EVERYDAY --generate 1'
timeblock habit create --routine 1 --title "Exercício" --start 06:00 --end 07:00 --repeat EVERYDAY --generate 1
sleep 1

echo ""
echo '$ timeblock list --day 0'
timeblock list --day 0
sleep 1

echo ""
echo '$ timeblock task create -t "Revisar código" -d "PR #123"'
timeblock task create -t "Revisar código" -d "PR #123"
sleep 1

echo ""
echo '$ timeblock task list'
timeblock task list

echo ""
echo "=== Demo concluída ==="
rm -rf "$(dirname $DB_TEMP)"
