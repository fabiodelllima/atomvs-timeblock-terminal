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
        "start_minutes": 360,
        "end_minutes": 420,
        "status": "done",
        "substatus": "full",
        "actual_minutes": 60,
    },
    {
        "name": "Academia",
        "start_minutes": 420,
        "end_minutes": 480,
        "status": "done",
        "substatus": "partial",
        "actual_minutes": 45,
    },
    {
        "name": "Trabalho",
        "start_minutes": 540,
        "end_minutes": 720,
        "status": "running",
        "substatus": None,
        "actual_minutes": 47,
    },
    {
        "name": "Almoço",
        "start_minutes": 720,
        "end_minutes": 780,
        "status": "done",
        "substatus": "overdone",
        "actual_minutes": 75,
    },
    {
        "name": "Estudo",
        "start_minutes": 840,
        "end_minutes": 960,
        "status": "paused",
        "substatus": None,
        "actual_minutes": 12,
    },
    {
        "name": "Café da Tarde",
        "start_minutes": 960,
        "end_minutes": 1020,
        "status": "done",
        "substatus": "excessive",
        "actual_minutes": 50,
    },
    {
        "name": "Organização",
        "start_minutes": 1020,
        "end_minutes": 1080,
        "status": "not_done",
        "substatus": "unjustified",
        "actual_minutes": None,
    },
    {
        "name": "Jantar",
        "start_minutes": 1140,
        "end_minutes": 1200,
        "status": "not_done",
        "substatus": "ignored",
        "actual_minutes": None,
    },
    {
        "name": "Leitura",
        "start_minutes": 1260,
        "end_minutes": 1320,
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
