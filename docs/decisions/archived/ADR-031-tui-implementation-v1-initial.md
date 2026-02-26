# ADR-031: Implementação TUI com Textual

**Status**: Aceito

**Data**: 2026-02-05

**Atualizado**: 2026-02-18

**Supersedes**: ADR-006 (expande decisão original com detalhes de implementação)

## Contexto

O ATOMVS TimeBlock v1.6.0 possui CLI funcional com 95% dos comandos operacionais, 87% de cobertura e 778 testes. A interface CLI atende automação e uso pontual, mas a experiência interativa diária (consultar agenda, marcar hábitos, operar timer) requer navegação repetitiva entre comandos. O custo cognitivo de digitar `habit list`, depois `habit done 3`, depois `timer start 3` para uma sequência trivial de ações motivou a decisão de oferecer uma interface visual complementar.

A v1.7.0 introduz a TUI como interface interativa complementar. O repositório já foi reestruturado (flatten) e renomeado para `atomvs-timeblock-terminal` seguindo o namespace ATOMVS definido em ADR-032. ADR-006 propôs Textual como framework; este ADR detalha a implementação concreta, incluindo decisões de layout, navegação, visualização de timeblocks e estratégia de testes.

Requisitos:

- Experiência interativa fluida para uso diário
- Coexistência CLI/TUI sem duplicação de lógica
- Visual moderno (Material-like) com timeblocks proporcionais e paleta consistente
- Testabilidade automatizada da TUI
- Textual como dependência opcional (CLI funciona sem ela)

## Decisão

A implementação da TUI se organiza em doze decisões técnicas que cobrem desde o entry point até a estratégia de testes. Cada decisão foi tomada priorizando coexistência com a CLI, compartilhamento total da service layer e manutenção da testabilidade automatizada. As decisões estão ordenadas da mais visível ao usuário (entry point, layout) até as mais internas (session management, dependências).

### 1. Entry Point: Detecção Automática

O entry point do aplicativo determina automaticamente qual interface iniciar com base na presença ou ausência de argumentos de linha de comando. Essa abordagem elimina a necessidade de um subcomando separado para a TUI, tornando a interação mais natural para o uso diário enquanto preserva a CLI para automação e scripts.

```python
import sys

def main():
    if len(sys.argv) <= 1:
        try:
            from timeblock.tui.app import TimeBlockApp
            TimeBlockApp().run()
        except ImportError:
            print("[WARN] TUI requer 'textual'.")
            print("       Instale: pip install atomvs-timeblock-terminal[tui]")
            print("       Uso CLI: timeblock --help")
    else:
        app()  # Typer CLI
```

**Justificativa:** O uso mais frequente será interativo (abrir, consultar, operar). Automação via CLI permanece idêntica. `timeblock --help` continua funcionando pois tem argumento.

### 2. Framework: Textual

Textual foi escolhido na ADR-006 por sua integração nativa com Rich (já dependência do projeto), CSS-like styling via TCSS, e Pilot para testes automatizados. A dependência é mantida como opcional para que a CLI permaneça funcional sem instalação adicional. Essa separação garante que ambientes headless ou de CI possam executar a CLI sem carregar dependências gráficas desnecessárias.

- **Versão mínima:** textual >= 0.89.0
- **Dependência:** Opcional (grupo `[tui]` no pyproject.toml)

```toml
[project.optional-dependencies]
tui = ["textual>=0.89.0"]
```

### 3. Package Structure

A estrutura de pacotes segue o princípio de separação clara entre as duas interfaces. O diretório `tui/` é adicionado como irmão de `commands/`, ambos consumindo a mesma camada de services. Widgets reutilizáveis ficam isolados de screens específicas, permitindo composição flexível e testes unitários independentes.

```
src/timeblock/
├── commands/           # CLI (existente, inalterado)
├── tui/                # TUI (novo)
│   ├── __init__.py
│   ├── app.py          # TimeBlockApp (classe principal)
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── routines.py
│   │   ├── habits.py
│   │   ├── tasks.py
│   │   └── timer.py
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── timeblock_grid.py  # Grade temporal proporcional
│   │   ├── nav_bar.py         # Barra de navegação horizontal
│   │   ├── command_bar.py     # Barra de comandos contextual
│   │   ├── card.py
│   │   └── confirm_dialog.py
│   └── styles/
│       └── theme.tcss
├── services/           # Compartilhado (existente)
├── models/             # Compartilhado (existente)
├── database/           # Compartilhado (existente)
├── utils/              # Compartilhado (existente)
├── config.py
└── main.py             # Entry point unificado
```

### 4. Layout: Navegação Horizontal

A TUI utiliza navegação horizontal no rodapé em vez de sidebar lateral, maximizando a área de conteúdo disponível. Em um terminal padrão de 80 colunas, uma sidebar de 22 caracteres reduziria a área útil para 58 colunas -- insuficiente para os timeblocks proporcionais que são a peça central do dashboard. O layout é composto por três zonas fixas: header (identidade + hora), content area (variável por screen), e footer duplo (nav bar + command bar).

```
┌─────────────────────────────────────────────────────────────────┐
│  ATOMVS                             Terça-feira, 18/02   14:30  │  ← Header
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                       Content Area                              │  ← Variável
│                    (depende da screen)                          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [D]Dashboard  [R]Rotinas  [H]Hábitos  [T]Tasks  [M]Timer       │  ← Nav Bar
├─────────────────────────────────────────────────────────────────┤
│       q:Sair  ?:Ajuda  <contextuais>             ▶ Timer: 05:23 │  ← Command Bar
└─────────────────────────────────────────────────────────────────┘
```

**Header:** Nome do app (esquerda), dia da semana por extenso + data + hora atual (direita). A hora atualiza a cada minuto.

**Nav Bar:** Navegação entre screens. Keybindings numéricos (1-5) e mnemônicos (d/r/h/t/m). Screen ativa destacada visualmente com cor `$primary`.

**Command Bar:** Keybindings contextuais por screen (esquerda), timer ativo se houver (direita). Muda conforme a screen ativa, servindo como guia de referência rápida para as ações disponíveis no contexto atual.

### 5. Arquitetura de Screens

A TUI é organizada em screens que mapeiam diretamente os domínios do sistema. Cada screen é um widget Textual independente com seu próprio conjunto de keybindings locais, enquanto o header, nav bar e command bar fornecem navegação e contexto global persistentes. Cinco screens compõem a v1.7.0; duas telas adicionais de analytics e drill-down estão planejadas para a Fase 4, permitindo visualizações ricas sem comprometer o escopo do lançamento inicial.

| Screen       | Funcionalidade                         | Keybinding | Fase   |
| ------------ | -------------------------------------- | ---------- | ------ |
| Dashboard    | Timeblocks do dia + tasks pendentes    | `1` ou `d` | Fase 1 |
| Routines     | CRUD rotinas, ativar/desativar         | `2` ou `r` | Fase 2 |
| Habits       | Hábitos + instâncias, marcar done/skip | `3` ou `h` | Fase 2 |
| Tasks        | CRUD tarefas, filtros, marcar completa | `4` ou `t` | Fase 2 |
| Timer        | Display live, start/pause/resume/stop  | `5` ou `m` | Fase 3 |
| Analytics    | Gráficos, heatmap, streaks, tendências | `a`        | Fase 4 |
| Habit Detail | Drill-down com histórico e métricas    | via enter  | Fase 4 |

### 6. Dashboard: Timeblocks Proporcionais

O Dashboard é a tela inicial e o coração da experiência TUI. Inspirado em calendários modernos como Google Calendar, exibe o dia corrente como uma grade temporal onde cada hábito da rotina ativa ocupa um bloco visual proporcional à sua duração. A tela é dividida em duas colunas: timeblocks da rotina ativa (esquerda, ~70%) e tasks pendentes (direita, ~30%). Essa disposição permite ao usuário ver, de relance, o que já foi feito, o que está pendente e o que vem a seguir, sem navegar entre múltiplos comandos.

#### Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  ATOMVS                              Terça-feira, 18/02    14:30 │
├───────────────────────────────────────────┬──────────────────────┤
│  Rotina Matinal                           │ Tasks                │
│───────────────────────────────────────────│                      │
│ 07:00 ┌─ Academia ──────────────── 1h30 ─┐│  Dentista        [>] │
│       │  ✓ DONE (FULL)           #saúde  ││  Comprar cabo    [>] │
│ 07:30 │                                  ││  Revisar PR      [>] │
│ 08:00 │                                  ││  Pagar conta     [>] │
│ 08:30 └──────────────────────────────────┘│                      │
│ 09:00 ┌─ Meditação ────────────── 30min ─┐│                      │
│       │  ○ PENDING                       ││                      │
│ 09:30 └──────────────────────────────────┘│                      │
│                                           │                      │
│ 10:00 ┌─ Estudo Python ───────────── 2h ─┐│                      │
│       │  ○ PENDING                 #dev  ││                      │
│ 10:30 │                                  ││                      │
│ 11:00 │                                  ││                      │
│ 11:30 │                                  ││                      │
│ 12:00 └──────────────────────────────────┘│                      │
│  ...              (vazio)                 │                      │
│ 18:00 ┌─ Leitura ─────────────────── 1h ─┐│                      │
│       │  ○ PENDING                       ││                      │
│ 18:30 │                                  ││                      │
│ 19:00 └──────────────────────────────────┘│                      │
├──────────────────────────────────────────────────────────────────┤
│  [D]Dashboard  [R]Rotinas  [H]Hábitos  [T]Tasks  [M]Timer        │
├──────────────────────────────────────────────────────────────────┤
│       q:Sair  ?:Ajuda  enter:Detalhes            ▶ Timer: 05:23 │
└──────────────────────────────────────────────────────────────────┘
```

#### Grade Temporal Proporcional

Cada slot de 30 minutos corresponde a 1 linha de terminal. Blocos de hábito ocupam altura proporcional à sua duração: um hábito de 1h30 ocupa 3 linhas, um de 30min ocupa 1 linha. Essa proporcionalidade dá ao usuário uma percepção visual imediata de quanto tempo cada atividade consome no dia. A coluna de timeblocks rola verticalmente quando o conteúdo excede a altura visível.

#### Bordas e Cores

Os blocos utilizam caracteres box drawing com cores semânticas que comunicam status e categorização por tag. A borda lateral funciona como uma faixa colorida contínua, semelhante ao indicador visual que o Google Calendar usa em cada evento, permitindo identificação rápida por categoria mesmo em uma lista longa.

- **Header do bloco** (`┌─ Título ── duração ─┐`): cor da tag se existir, senão `$primary`
- **Borda lateral** (`│`): mesma cor do header (faixa visual contínua)
- **Base do bloco** (`└──────────────────────┘`): mesma cor, fecha o bloco
- **Status text**: `$success` (verde) para DONE, `$warning` (amarelo) para PENDING, `$error` (vermelho) para NOT_DONE
- **Slots vazios**: cor `$muted`
- **Gaps grandes** (>2h) entre blocos são colapsados com indicador `...`

#### Coluna Tasks

A coluna direita apresenta uma lista compacta de tasks pendentes ordenadas por data. Cada task exibe apenas o título e um botão `[>]` para expandir detalhes (data, horário, descrição, tag). O design compacto prioriza a visão geral: o usuário sabe quantas tasks tem pendentes sem poluição visual, e pode expandir individualmente quando necessário.

### 7. Screens Adicionais

As screens de CRUD (Routines, Habits, Tasks) seguem o padrão consistente definido em BR-TUI-005: formulários inline para create/edit, confirmação explícita para delete, e refresh automático após operações. A screen Timer centra o display numérico para máxima legibilidade durante sessões de foco. As telas de Analytics e Habit Detail são planejadas para a Fase 4, quando o sistema terá dados históricos suficientes para visualizações significativas.

#### Routines

```
┌─────────────────────────────────────────────────────────────────┐
│  Rotinas                                                        │
│                                                                 │
│  > Rotina Matinal                              ● ATIVA          │
│    Rotina Noturna                              ○                │
│    Rotina Fim de Semana                        ○                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│   n:Nova  e:Editar  x:Deletar  enter:Ativar           ▶ --:--  │
└─────────────────────────────────────────────────────────────────┘
```

#### Habits

```
┌─────────────────────────────────────────────────────────────────┐
│  Hábitos ─ Rotina Matinal                                       │
│                                                                 │
│  > Academia          07:00-08:30  WEEKDAYS  #saude              │
│    ├─ 18/02 Ter      ✓ DONE (FULL)                              │
│    ├─ 19/02 Qua      ○ PENDING                                  │
│    └─ 20/02 Qui      ○ PENDING                                  │
│                                                                 │
│    Meditação         09:00-09:30  EVERYDAY                      │
│    ├─ 18/02 Ter      ○ PENDING                                  │
│    └─ 19/02 Qua      ○ PENDING                                  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  n:Novo  e:Editar  x:Del  enter:Done/Skip  s:Timer     ▶ --:-- │
└─────────────────────────────────────────────────────────────────┘
```

#### Tasks

```
┌─────────────────────────────────────────────────────────────────┐
│  Tasks                            [Pendentes] Hoje  Concluídas  │
│                                                                 │
│  > Dentista              15/02 14:30  #saude                    │
│    Comprar cabo USB      16/02                                  │
│    Revisar PR #42        17/02  #dev                            │
│    Enviar relatório      20/02                                  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  n:Nova  e:Editar  x:Del  enter:Concluir  tab:Filtro   ▶ --:-- │
└─────────────────────────────────────────────────────────────────┘
```

#### Timer

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                      ▶ RUNNING                                  │
│                                                                 │
│                        25:43                                    │
│                      / 01:30:00                                 │
│                                                                 │
│                   Academia #saude                               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│          p:Pausar  enter:Parar  c:Cancelar          ▶ 25:43    │
└─────────────────────────────────────────────────────────────────┘
```

#### Analytics (Fase 4 - Futura)

A tela de Analytics traz visualizações inspiradas em ferramentas como D3.js, adaptadas para o terminal usando blocos Unicode e box drawing. Gráficos de barras horizontais mostram consistência semanal e distribuição de tempo por categoria, enquanto um heatmap anual permite identificar padrões sazonais. Streaks de hábitos incentivam a manutenção de sequências, alinhando-se com os princípios de Atomic Habits que fundamentam o projeto.

```
┌─────────────────────────────────────────────────────────────────┐
│  Analytics ─ Fevereiro 2026                                     │
│                                                                 │
│  Consistência Semanal          Tempo por Categoria              │
│  ┌────────────────────────┐    ┌──────────────────────────┐     │
│  │ SEG ████████████   95% │    │ #saude   ████████░░  12h │     │
│  │ TER ██████████░░   80% │    │ #dev     ██████░░░░   8h │     │
│  │ QUA ████████████  100% │    │ #leitura ████░░░░░░   5h │     │
│  │ QUI ██████░░░░░░   60% │    │ outros   ██░░░░░░░░   3h │     │
│  │ SEX ████████░░░░   75% │    └──────────────────────────┘     │
│  └────────────────────────┘                                     │
│                                Streak Atual                     │
│  Heatmap Anual                 ┌──────────────────────────┐     │
│  ┌────────────────────────┐    │ Academia        14 dias  │     │
│  │ JAN ░░▓▓██▓▓░░▓▓██▓▓░░ │    │ Meditação        8 dias  │     │
│  │ FEV ▓▓██▓▓░░▓▓██▓▓     │    │ Leitura          3 dias  │     │
│  └────────────────────────┘    └──────────────────────────┘     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│    tab:Período  ←→:Navegar                           ▶ --:--   │
└─────────────────────────────────────────────────────────────────┘
```

#### Habit Detail (Fase 4 - Futura)

O drill-down de hábito individual apresenta métricas detalhadas e histórico visual dos últimos 30 dias. A visualização combina um calendário compacto com indicadores de completion rate e tempo médio real, permitindo ao usuário identificar tendências e ajustar sua rotina com base em dados concretos.

```
┌─────────────────────────────────────────────────────────────────┐
│  Academia ─ Detalhes                                    #saude  │
│  ─────────────────────────────────────────────────────────────  │
│  Horário: 07:00-08:30 (1h30)             Recorrência: WEEKDAYS  │
│  Rotina: Rotina Matinal                       Streak:  14 dias  │
│                                                                 │
│  Últimos 30 dias                                                │
│  ┌────────────────────────────────────────────────────┐         │
│  │ ██ ██ ██ ░░ ██ ░░ ░░ ██ ██ ██ ██ ██ ░░ ░░ ██ ██ ██ │         │
│  │ 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 │         │
│  └────────────────────────────────────────────────────┘         │
│   ██ DONE  ░░ Sem agenda  ▒▒ PARTIAL  ── NOT_DONE               │
│                                                                 │
│  Completion Rate        Tempo Médio Real                        │
│  ┌────────────────┐     ┌────────────────┐                      │
│  │  87%    ▲ +5%  │     │  1:25   ▼ -3m  │                      │
│  └────────────────┘     └────────────────┘                      │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│       esc:Voltar  s:Timer  e:Editar                  ▶ --:--   │
└─────────────────────────────────────────────────────────────────┘
```

### 8. Gerenciamento de Session

Services recebem `Session` no construtor. A TUI tem lifecycle longo (minutos a horas), diferente da CLI (segundos). Manter uma session aberta durante toda a execução da TUI causaria problemas de dados stale e conflitos transacionais. A estratégia session-per-action resolve isso criando uma session atômica para cada operação do usuário, garantindo que cada ação veja dados frescos do banco e seja isolada transacionalmente.

```python
from contextlib import contextmanager
from sqlmodel import Session
from timeblock.database.engine import get_engine

@contextmanager
def get_session():
    """Cria session para uma operação atômica."""
    engine = get_engine()
    with Session(engine) as session:
        yield session
        session.commit()
```

### 9. Fluxo de Dados

O fluxo de dados na TUI segue direção unidirecional: input do usuário aciona um handler de screen, que abre uma session atômica, invoca o service apropriado, e ao retornar, atualiza os widgets da screen. Este padrão garante que a TUI nunca manipula dados diretamente e que cada operação é isolada transacionalmente. É o mesmo padrão que a CLI usa, apenas com a diferença de que o "output" vai para widgets em vez de stdout.

```
User Input (keybinding/click)
    │
    v
Screen Handler (método on_*)
    │
    v
get_session() context manager
    │
    v
Service.method(session, args)
    │
    v
Model/ORM operation
    │
    v
Session commit/rollback
    │
    v
Screen.refresh_data() → atualiza widgets
```

### 10. Design Visual: Material-like

O design visual segue princípios Material Design adaptados para terminal: superfícies com elevação via cores distintas, hierarquia tipográfica (bold, normal, dim) e cores semânticas consistentes para status. A paleta é definida inteiramente em `theme.tcss` como single source of truth, evitando cores hardcoded nos widgets. A escolha de deep purple como cor primária diferencia visualmente a aplicação de outros tools de terminal enquanto mantém boa legibilidade sobre superfícies escuras.

**Paleta de cores (TCSS):**

```
$primary:       #7C4DFF   (deep purple)
$primary-light: #B388FF   (light purple)
$surface:       #1E1E2E   (dark surface)
$surface-alt:   #2A2A3E   (elevated surface)
$on-surface:    #CDD6F4   (texto sobre dark)
$success:       #A6E3A1   (verde - done)
$warning:       #F9E2AF   (amarelo - pending)
$error:         #F38BA8   (vermelho - missed/overdue)
$muted:         #6C7086   (texto secundário)
```

**Timeblock widget:** Bordas box drawing (┌─ │ └─), cor da tag na borda lateral, altura proporcional à duração. Padding 1x2. Status text com cor semântica.

**Card widget:** Borda arredondada (`border: round $primary`), padding 1x2, margin 1, título em bold, conteúdo muted.

**Spacing:** Padding padrão 1 (vertical) e 2 (horizontal), margin entre cards 1, content area fluid.

### 11. Estratégia de Testes

A TUI é testada com Textual Pilot, framework de testes assíncronos embutido no Textual que permite simular interações de usuário (keypresses, clicks) e inspecionar estado de widgets programaticamente. A distribuição de testes segue a pirâmide do projeto, com ênfase em testes unitários de widgets isolados. Testes de integração validam a comunicação entre screens e services, enquanto testes E2E cobrem flows completos de navegação.

**Framework:** Textual Pilot (built-in testing)

```python
async def test_dashboard_shows_active_routine():
    async with TimeBlockApp().run_test() as pilot:
        assert pilot.app.query_one("#routine-name").renderable == "Rotina Matinal"
```

**Distribuição:**

| Tipo        | Escopo                                | Meta |
| ----------- | ------------------------------------- | ---- |
| Unit        | Widgets isolados, lógica de rendering | 60%  |
| Integration | Screen + Service (com DB)             | 30%  |
| E2E         | Navegação completa, flows de usuário  | 10%  |

**Naming:** `test_br_tui_xxx_cenário`

### 12. Gerenciamento de Dependências

Textual e suas ferramentas de desenvolvimento são gerenciadas como dependency groups opcionais no `pyproject.toml`. O grupo `[tui]` instala apenas o runtime necessário para o usuário final, enquanto `[dev]` inclui `textual-dev` para inspeção de widgets e `pytest-asyncio` para testes assíncronos. Esta separação garante que ambientes de produção CLI permaneçam enxutos e que o CI possa rodar testes TUI apenas quando necessário.

```toml
[project.optional-dependencies]
tui = ["textual>=0.89.0"]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.1.0",
    "mypy>=1.8.0",
    "textual-dev>=1.0.0",
]
```

## Alternativas Consideradas

Quatro alternativas foram avaliadas nas dimensões de UX, complexidade de manutenção e consistência com a arquitetura existente. Cada uma oferecia vantagens pontuais, mas nenhuma equilibrava todos os requisitos tão bem quanto a abordagem escolhida.

### Sidebar lateral (layout original)

- **Prós:** Convenção comum em TUIs, navegação sempre visível
- **Contras:** Consome ~22 caracteres de largura, reduz área de conteúdo. Em terminal 80 colunas, sobram apenas 58 para conteúdo -- insuficiente para timeblocks proporcionais.

### Textual sem detecção automática (subcomando `timeblock tui`)

- **Prós:** Explícito, sem ambiguidade
- **Contras:** Mais digitação para uso mais frequente, UX inferior

### Prompt Toolkit para TUI

- **Prós:** Maduro, menos opinionado
- **Contras:** Low-level, requer mais código para visual Material-like, não aproveita Rich

### Session-per-screen (em vez de session-per-action)

- **Prós:** Menos overhead de conexão
- **Contras:** Sessions stale em TUI longa, risco de dados desatualizados, inconsistência com CLI

## Consequências

A introdução da TUI impacta o projeto em três dimensões: amplia significativamente a experiência do usuário com uma interface visual rica, introduz complexidade de manutenção de duas interfaces, e estabelece as bases para visualizações analíticas futuras. O balanço é positivo desde que a service layer compartilhada previna duplicação de lógica.

### Positivas

- Experiência interativa rica para uso diário
- Timeblocks proporcionais com estilo calendário moderno
- Navegação horizontal maximiza área de conteúdo
- Compartilha 100% da lógica de negócios com CLI (service layer)
- Textual usa Rich internamente (já é dependência)
- Testes automatizados com Pilot
- CLI permanece funcional e independente
- Telas futuras de analytics com visualizações ricas

### Negativas

- Nova dependência (textual ~15MB)
- Complexidade de manutenção em duas interfaces
- Testes TUI são assíncronos (pytest-asyncio necessário)
- TCSS é específico do Textual (vendor lock-in para styling)

### Neutras

- CLI permanece interface primária para automação
- TUI é opcional via dependency group
- Repositório segue namespace ATOMVS (ADR-032)

## Validação

Consideramos acertada se:

- TUI abre em < 500ms
- Navegação entre screens < 100ms
- 80%+ cobertura no pacote tui/
- Zero regressão na CLI existente
- Timer display atualiza a cada segundo sem flicker
- Timeblocks visualmente proporcionais à duração

## Implementação

O plano de implementação divide a TUI em quatro fases incrementais. Cada fase entrega valor funcional completo e pode ser validada independentemente. A Fase 1 estabelece a fundação (estrutura, navegação, dashboard); as Fases 2 e 3 completam as screens operacionais; a Fase 4 adiciona analytics quando houver dados históricos suficientes para visualizações significativas.

### Fase 1: Foundation (Sprint 1)

1. Criar estrutura de pacotes tui/
2. Implementar TimeBlockApp com nav bar horizontal
3. Definir theme.tcss com paleta Material-like
4. Modificar main.py (entry point com detecção automática)
5. DashboardScreen com timeblocks proporcionais + tasks

### Fase 2: CRUD Screens (Sprint 2)

1. RoutinesScreen com CRUD e ativação
2. HabitsScreen com instâncias e done/skip
3. TasksScreen com CRUD e filtros
4. ConfirmDialog widget

### Fase 3: Timer + Polish (Sprint 3)

1. TimerScreen com display live centralizado
2. Timer ativo na command bar
3. Keybindings completos
4. Testes completos

### Fase 4: Analytics + Detail (Futuro)

1. AnalyticsScreen com gráficos (barras, heatmap, sparklines)
2. HabitDetailScreen com drill-down e métricas
3. Navegação via keybinding `a` e `enter` em hábito

## Referências

- [ADR-006](ADR-006-textual-tui.md) — Decisão original Textual
- [ADR-007](ADR-007-service-layer.md) — Service Layer (consumida pela TUI)
- [ADR-032](ADR-032-branding-repository-naming.md) — Branding e nomenclatura
- [Textual Documentation](https://textual.textualize.io/)
- [Textual CSS Reference](https://textual.textualize.io/css_types/)
- [Material Design 3 Color System](https://m3.material.io/styles/color)
