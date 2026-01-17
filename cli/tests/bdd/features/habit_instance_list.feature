# language: pt
Funcionalidade: Listagem de Instâncias de Hábitos (BR-HABITINSTANCE-006)
  Como usuário do TimeBlock
  Quero listar instâncias de hábitos com filtros
  Para visualizar minha agenda de forma flexível

  Contexto:
    Dado que existe uma rotina ativa "Rotina Teste"
    E que existe um hábito "Academia" na rotina com horário 07:00-08:00
    E que existem instâncias geradas para o período de 7 dias

  Cenário: Listar todas as instâncias sem filtros
    Quando eu listo instâncias sem filtros
    Então devo receber uma lista com 7 instâncias

  Cenário: Filtrar instâncias por hábito
    Dado que existe outro hábito "Meditação" na rotina
    E que existem instâncias de "Meditação" para 7 dias
    Quando eu listo instâncias filtrando por hábito "Academia"
    Então devo receber apenas instâncias de "Academia"

  Cenário: Filtrar instâncias por período
    Quando eu listo instâncias com data_start de hoje e data_end de hoje+2
    Então devo receber uma lista com 3 instâncias

  Cenário: Retornar lista vazia quando não há resultados
    Quando eu listo instâncias com data_start no futuro distante
    Então devo receber uma lista vazia
    E a lista não deve ser None
