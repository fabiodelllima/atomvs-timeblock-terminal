"""Mock data para desenvolvimento e testes do dashboard (BR-TUI-003-R28).

Rotina Demo com 9 hábitos (todos status/substatus), 9 tasks (todos estados)
e timer ativo. Usado em fixtures de teste e no futuro comando `atomvs demo`.
"""

DEMO_ROUTINE_NAME = "Rotina Demo"

WEEKDAYS_PT = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
MONTHS_PT = [
    "",
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]

MOCK_INSTANCES = [
    {
        "name": "Despertar",
        "start_hour": 6,
        "end_hour": 7,
        "status": "done",
        "substatus": "full",
        "actual_minutes": 60,
    },
    {
        "name": "Academia",
        "start_hour": 7,
        "end_hour": 8,
        "status": "done",
        "substatus": "partial",
        "actual_minutes": 45,
    },
    {
        "name": "Trabalho",
        "start_hour": 9,
        "end_hour": 12,
        "status": "running",
        "substatus": None,
        "actual_minutes": 47,
    },
    {
        "name": "Almoço",
        "start_hour": 12,
        "end_hour": 13,
        "status": "done",
        "substatus": "overdone",
        "actual_minutes": 75,
    },
    {
        "name": "Estudo",
        "start_hour": 14,
        "end_hour": 16,
        "status": "paused",
        "substatus": None,
        "actual_minutes": 12,
    },
    {
        "name": "Café da Tarde",
        "start_hour": 16,
        "end_hour": 17,
        "status": "done",
        "substatus": "excessive",
        "actual_minutes": 50,
    },
    {
        "name": "Organização",
        "start_hour": 17,
        "end_hour": 18,
        "status": "not_done",
        "substatus": "unjustified",
        "actual_minutes": None,
    },
    {
        "name": "Jantar",
        "start_hour": 19,
        "end_hour": 20,
        "status": "not_done",
        "substatus": "ignored",
        "actual_minutes": None,
    },
    {
        "name": "Leitura",
        "start_hour": 21,
        "end_hour": 22,
        "status": "pending",
        "substatus": None,
        "actual_minutes": None,
    },
]

MOCK_TASKS: list[dict] = [
    {
        "name": "Dentista",
        "proximity": "Hoje",
        "date": "23 Feb",
        "time": "15:00",
        "status": "pending",
        "days": 0,
    },
    {
        "name": "Email cliente",
        "proximity": "Amanhã",
        "date": "24 Feb",
        "time": "09:00",
        "status": "pending",
        "days": 1,
    },
    {
        "name": "Deploy staging",
        "proximity": "3 dias",
        "date": "26 Feb",
        "time": "10:00",
        "status": "pending",
        "days": 3,
    },
    {
        "name": "Code review",
        "proximity": "5 dias",
        "date": "28 Feb",
        "time": "14:00",
        "status": "pending",
        "days": 5,
    },
    {
        "name": "Retrospectiva",
        "proximity": "2 mês",
        "date": "25 Apr",
        "time": "--:--",
        "status": "pending",
        "days": 61,
    },
    {
        "name": "Comprar domínio",
        "proximity": "Hoje",
        "date": "23 Feb",
        "time": "09:30",
        "status": "completed",
    },
    {
        "name": "Evento cancelado",
        "proximity": "--",
        "date": "20 Feb",
        "time": "16:00",
        "status": "cancelled",
    },
    {
        "name": "Enviar relatório",
        "proximity": "1 sem",
        "date": "16 Feb",
        "time": "--:--",
        "status": "overdue",
    },
    {
        "name": "Revisar PR #142",
        "proximity": "3 dias",
        "date": "20 Feb",
        "time": "14:00",
        "status": "overdue",
    },
]

MOCK_TIMER: dict = {"elapsed": "47:23", "name": "Trabalho", "status": "running"}
