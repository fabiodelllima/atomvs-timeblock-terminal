#!/bin/bash
# Demo completa do TimeBlock Organizer
# Demonstra todas as funcionalidades do sistema

set -e
DB_TEMP=$(mktemp -d)/demo.db
export TIMEBLOCK_DB_PATH="$DB_TEMP"

# Cores para output
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

section() {
    echo ""
    echo -e "${YELLOW}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  $1${NC}"
    echo -e "${YELLOW}════════════════════════════════════════${NC}"
    echo ""
    sleep 1
}

cmd() {
    echo -e "${CYAN}\$ $1${NC}"
    eval "$1"
    sleep 0.5
}

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║       TimeBlock Organizer - Demo Completa                 ║"
echo "║       Sistema de Gerenciamento de Tempo via CLI           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
sleep 2

# ══════════════════════════════════════
section "1. INICIALIZACAO"
# ══════════════════════════════════════

cmd "timeblock init"
cmd "timeblock version"

# ══════════════════════════════════════
section "2. TAGS - Categorização"
# ══════════════════════════════════════

cmd "timeblock tag create 'Saúde' -c '#00FF00'"
cmd "timeblock tag create 'Trabalho' -c '#0000FF'"
cmd "timeblock tag create 'Estudo' -c '#FF0000'"
cmd "timeblock tag list"

# ══════════════════════════════════════
section "3. ROUTINES - Rotinas"
# ══════════════════════════════════════

cmd "timeblock routine create 'Dias Úteis'"
cmd "timeblock routine create 'Fim de Semana'"
cmd "timeblock routine list"
cmd "timeblock routine activate 1"
cmd "timeblock routine list"

# ══════════════════════════════════════
section "4. HABITS - Hábitos Recorrentes"
# ══════════════════════════════════════

cmd "timeblock habit create --routine 1 --title 'Meditação' --start 06:00 --end 06:30 --repeat EVERYDAY --generate 1"
cmd "timeblock habit create --routine 1 --title 'Exercício' --start 06:30 --end 07:30 --repeat EVERYDAY --generate 1"
cmd "timeblock habit create --routine 1 --title 'Leitura' --start 21:00 --end 22:00 --repeat WEEKDAYS --generate 1"
cmd "timeblock habit list"
cmd "timeblock habit list --routine 1"

# ══════════════════════════════════════
section "5. TASKS - Tarefas Pontuais"
# ══════════════════════════════════════

DT_1H=$(date -d "+1 hour" "+%Y-%m-%d %H:%M")
DT_2H=$(date -d "+2 hours" "+%Y-%m-%d %H:%M")
DT_TOMORROW=$(date -d "+1 day 10:00" "+%Y-%m-%d %H:%M")

cmd "timeblock task create -t 'Revisar PR #123' -D '$DT_1H' --desc 'Code review do backend'"
cmd "timeblock task create -t 'Reunião com cliente' -D '$DT_2H'"
cmd "timeblock task create -t 'Dentista' -D '$DT_TOMORROW' --desc 'Consulta de rotina'"
cmd "timeblock task list"

# ══════════════════════════════════════
section "6. LIST - Visualização Geral"
# ══════════════════════════════════════

cmd "timeblock list --day 0"
cmd "timeblock list --week 0"

# ══════════════════════════════════════
section "7. TIMER - Tracking de Tempo"
# ══════════════════════════════════════

echo -e "${CYAN}# Iniciando timer para primeira instância de hábito${NC}"
cmd "timeblock timer start --schedule 1 -b"
cmd "timeblock timer status"
sleep 2
cmd "timeblock timer pause"
cmd "timeblock timer status"
sleep 1
cmd "timeblock timer resume -b"
sleep 1
cmd "timeblock timer stop"

# ══════════════════════════════════════
section "8. HABIT SKIP - Pular Hábito"
# ══════════════════════════════════════

echo -e "${CYAN}# Pulando instância com justificativa${NC}"
cmd "timeblock habit skip 2 --category HEALTH --note 'Dor de cabeça'"

# ══════════════════════════════════════
section "9. TASK CHECK - Completar Tarefa"
# ══════════════════════════════════════

cmd "timeblock task check 1"
cmd "timeblock task list"
cmd "timeblock task list"

# ══════════════════════════════════════
section "10. UPDATE - Atualizações"
# ══════════════════════════════════════

cmd "timeblock task update 2 --title 'Reunião com cliente - URGENTE'"
cmd "timeblock habit update 1 --title 'Meditação Guiada'"
cmd "timeblock tag update 1 --name 'Bem-estar'"

# ══════════════════════════════════════
section "11. RESCHEDULE - Conflitos"
# ══════════════════════════════════════

cmd "timeblock reschedule conflicts --date $(date +%Y-%m-%d)"

# ══════════════════════════════════════
section "12. DELETE - Limpeza"
# ══════════════════════════════════════

cmd "timeblock task delete 3 --force"
cmd "timeblock task list"

# ══════════════════════════════════════
section "13. ROUTINE MANAGEMENT"
# ══════════════════════════════════════

cmd "timeblock routine deactivate 1"
cmd "timeblock routine activate 2"
cmd "timeblock routine list"

# ══════════════════════════════════════
echo ""
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              Demo Concluída com Sucesso!                  ║"
echo "╠═══════════════════════════════════════════════════════════╣"
echo "║  Comandos demonstrados:                                   ║"
echo "║  - init, version                                          ║"
echo "║  - tag: create, list, update                              ║"
echo "║  - routine: create, list, activate, deactivate            ║"
echo "║  - habit: create, list, update, skip                      ║"
echo "║  - task: create, list, check, update, delete              ║"
echo "║  - timer: start, status, pause, resume, stop              ║"
echo "║  - list: --day, --week                                    ║"
echo "║  - reschedule: conflicts                                  ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Limpeza
rm -rf "$(dirname $DB_TEMP)"
