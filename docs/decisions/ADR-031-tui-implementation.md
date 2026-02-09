# ADR-031: Implementação TUI com Textual

**Status**: Acceito

**Data**: 2026-02-05

**Supersedes**: ADR-006 (expande decisão original com detalhes de implementação)

## Contexto

O ATOMVS TimeBlock v1.6.0 possui CLI funcional com 95% dos comandos operacionais, 87% de cobertura e 778 testes. A interface CLI atende automação e uso pontual, mas a experiência interativa diária (consultar agenda, marcar hábitos, operar timer) requer navegação repetitiva entre comandos.

A v1.7.0 introduz a TUI como interface interativa complementar. Simultaneamente, o repositório é reestruturado: `cli/` é eliminado (flatten), `src/`, `tests/` e configs sobem para a raiz, e o repo é renomeado para `atomvs-timeblock-terminal` seguindo o namespace ATOMVS definido em ADR-032.

ADR-006 propôs Textual como framework. Este ADR detalha a implementação concreta.

Requisitos:

- Experiência interativa fluida para uso diário
- Coexistência CLI/TUI sem duplicação de lógica
- Visual moderno (Material-like) com cards, spacing e paleta consistente
- Testabilidade automatizada da TUI
- Textual como dependência opcional (CLI funciona sem ela)

## Decisão

A implementação da TUI se organiza em nove decisões técnicas que cobrem desde a reestruturação física do repositório até a estratégia de testes. Cada decisão foi tomada priorizando coexistência com a CLI, compartilhamento total da service layer e manutenção da testabilidade automatizada.

A implementação da TUI se organiza em nove decisões técnicas que cobrem desde a reestruturação física do repositório até a estratégia de testes. Cada decisão foi tomada priorizando coexistência com a CLI, compartilhamento total da service layer e manutenção da testabilidade automatizada.

### 1. Reestruturação do Repositório (Sprint 0)

O diretório `cli/` é eliminado. Todo o conteúdo sobe para a raiz do repositório.

**Antes (v1.6.0):**

```
timeblock-organizer/
├── cli/
│   ├── src/timeblock/
│   ├── tests/
│   ├── data/
│   ├── pyproject.toml
│   ├── pytest.ini
│   └── .ruff.toml
├── docs/
├── scripts/
└── README.md
```

**Depois (v1.7.0):**

```
atomvs-timeblock-terminal/
├── src/timeblock/
│   ├── commands/            # CLI (existente, inalterado)
│   ├── tui/                 # TUI (novo)
│   │   ├── __init__.py
│   │   ├── app.py           # TimeBlockApp (classe principal)
│   │   ├── screens/
│   │   │   ├── __init__.py
│   │   │   ├── dashboard.py
│   │   │   ├── routines.py
│   │   │   ├── habits.py
│   │   │   ├── tasks.py
│   │   │   └── timer.py
│   │   ├── widgets/
│   │   │   ├── __init__.py
│   │   │   ├── card.py
│   │   │   ├── sidebar.py
│   │   │   ├── status_bar.py
│   │   │   └── confirm_dialog.py
│   │   └── styles/
│   │       └── theme.tcss
│   ├── services/            # Compartilhado (existente)
│   ├── models/              # Compartilhado (existente)
│   ├── database/            # Compartilhado (existente)
│   ├── utils/               # Compartilhado (existente)
│   ├── config.py
│   └── main.py              # Entry point unificado
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── bdd/
├── data/
├── docs/
├── scripts/
├── pyproject.toml
├── pytest.ini
├── .ruff.toml
├── mkdocs.yml
├── README.md
└── CHANGELOG.md
```

**Justificativa:** O nome `cli/` era preciso quando só havia CLI. Com a TUI, o subdiretório deixa de representar o conteúdo. Flatten simplifica paths, elimina `cd cli/` de todos os workflows, e alinha com a convenção Python padrão (`src/` na raiz).

### 2. Entry Point: Detecção Automática

`timeblock` sem argumentos abre a TUI. Com argumentos, executa CLI normalmente.

```python
# main.py
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

### 3. Framework: Textual

Textual foi escolhido na ADR-006 e confirmado aqui como framework de TUI por sua integração nativa com Rich (já dependência do projeto), CSS-like styling via TCSS, e Pilot para testes automatizados. A dependência é mantida como opcional para que a CLI permaneça funcional sem instalação adicional.

Textual foi escolhido na ADR-006 e confirmado aqui como framework de TUI por sua integração nativa com Rich (já dependência do projeto), CSS-like styling via TCSS, e Pilot para testes automatizados. A dependência é mantida como opcional para que a CLI permaneça funcional sem instalação adicional.

**Versão mínima:** textual >= 0.89.0
**Dependência:** Opcional (grupo `[tui]` no pyproject.toml)

```toml
[project.optional-dependencies]
tui = ["textual>=0.89.0"]
```

**Fallback:** Se Textual não está instalado e usuário executa sem args, exibe mensagem orientando instalação.

### 4. Arquitetura de Screens

A TUI é organizada em cinco screens que mapeiam diretamente os domínios do sistema. Cada screen é um widget Textual independente com seu próprio conjunto de keybindings locais, enquanto a sidebar e a status bar fornecem navegação e contexto global persistentes.

A TUI é organizada em cinco screens que mapeiam diretamente os domínios do sistema. Cada screen é um widget Textual independente com seu próprio conjunto de keybindings locais, enquanto a sidebar e a status bar fornecem navegação e contexto global persistentes.

Cinco screens na v1.7.0, navegáveis por sidebar:

| Screen    | Funcionalidade                         | Keybinding |
| --------- | -------------------------------------- | ---------- |
| Dashboard | Visão geral do dia, quick actions      | `1` ou `d` |
| Routines  | CRUD rotinas, ativar/desativar         | `2` ou `r` |
| Habits    | Hábitos + instâncias, marcar done/skip | `3` ou `h` |
| Tasks     | CRUD tarefas, marcar completa          | `4` ou `t` |
| Timer     | Display live, start/pause/resume/stop  | `5` ou `m` |

**Layout:**

```
┌───────────┬─────────────────────────────────────┐
│  Sidebar  │            Content Area             │
│           │                                     │
│  [D] Dash │  ┌─────────┐  ┌─────────┐          │
│  [R] Rout │  │  Card 1  │  │  Card 2  │         │
│  [H] Habi │  └─────────┘  └─────────┘          │
│  [T] Task │  ┌─────────┐  ┌─────────┐          │
│  [M] Time │  │  Card 3  │  │  Card 4  │         │
│           │  └─────────┘  └─────────┘          │
├───────────┴─────────────────────────────────────┤
│  Status Bar: Rotina Ativa | Timer 05:23 | 14:30 │
└─────────────────────────────────────────────────┘
```

### 5. Gerenciamento de Session

Services recebem `Session` no construtor. A TUI tem lifecycle longo (minutos/horas), diferente da CLI (segundos).

**Estratégia:** Session-per-action (não session-per-screen).

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

**Cada operação na TUI:**

1. Abre session via context manager
2. Instancia service com session
3. Executa operação
4. Session fecha automaticamente (commit ou rollback)

**Justificativa:** Evita sessions stale em TUI de longa duração. Cada ação vê dados frescos do banco. Consistente com CLI que já usa sessions curtas.

### 6. Fluxo de Dados

O fluxo de dados na TUI segue direção unidirecional: input do usuário aciona um handler de screen, que abre uma session atômica, invoca o service apropriado, e ao retornar, atualiza os widgets da screen. Este padrão garante que a TUI nunca manipula dados diretamente e que cada operação é isolada transacionalmente.

O fluxo de dados na TUI segue direção unidirecional: input do usuário aciona um handler de screen, que abre uma session atômica, invoca o service apropriado, e ao retornar, atualiza os widgets da screen. Este padrão garante que a TUI nunca manipula dados diretamente e que cada operação é isolada transacionalmente.

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

### 7. Design Visual: Material-like

O design visual segue princípios Material Design adaptados para terminal: superfícies com elevação via cores distintas, hierarquia tipográfica (bold, normal, dim) e cores semânticas consistentes para status. A paleta é definida inteiramente em theme.tcss como single source of truth, evitando cores hardcoded nos widgets.

O design visual segue princípios Material Design adaptados para terminal: superfícies com elevação via cores distintas, hierarquia tipográfica (bold, normal, dim) e cores semânticas consistentes para status. A paleta é definida inteiramente em theme.tcss como single source of truth, evitando cores hardcoded nos widgets.

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

**Card widget:** Borda arredondada (`border: round $primary`), padding 1x2, margin 1, título em bold com cor contextual, conteúdo com texto muted para labels.

**Spacing:** Padding padrão 1 (vertical) e 2 (horizontal), margin entre cards 1, sidebar 22 caracteres fixo, content area fluid.

### 8. Estratégia de Testes

A TUI é testada com Textual Pilot, framework de testes assíncronos embutido no Textual que permite simular interações de usuário (keypresses, clicks) e inspecionar estado de widgets programaticamente. A distribuição de testes segue a pirâmide do projeto, com ênfase em testes unitários de widgets isolados.

A TUI é testada com Textual Pilot, framework de testes assíncronos embutido no Textual que permite simular interações de usuário (keypresses, clicks) e inspecionar estado de widgets programaticamente. A distribuição de testes segue a pirâmide do projeto, com ênfase em testes unitários de widgets isolados.

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

**Naming:** Segue ADR-019: `test_br_tui_xxx_cenário`

### 9. Gerenciamento de Dependências

Textual e suas ferramentas de desenvolvimento são gerenciadas como dependency groups opcionais no pyproject.toml. O grupo `[tui]` instala apenas o runtime, enquanto `[dev]` inclui textual-dev e pytest-asyncio para desenvolvimento e testes. Esta separação garante que ambientes de produção CLI permaneçam enxutos.

Textual e suas ferramentas de desenvolvimento são gerenciadas como dependency groups opcionais no pyproject.toml. O grupo `[tui]` instala apenas o runtime, enquanto `[dev]` inclui textual-dev e pytest-asyncio para desenvolvimento e testes. Esta separação garante que ambientes de produção CLI permaneçam enxutos.

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

Quatro alternativas foram avaliadas nas dimensões de UX, complexidade de manutenção e consistência com a arquitetura existente.

Quatro alternativas foram avaliadas nas dimensões de UX, complexidade de manutenção e consistência com a arquitetura existente.

### Textual sem detecção automática (subcomando `timeblock tui`)

**Prós:** Explícito, sem ambiguidade
**Contras:** Mais digitação para uso mais frequente, UX inferior

### Prompt Toolkit para TUI

**Prós:** Maduro, menos opinionado
**Contras:** Low-level, requer mais código para visual Material-like, não aproveita Rich

### Session-per-screen (em vez de session-per-action)

**Prós:** Menos overhead de conexão
**Contras:** Sessions stale em TUI longa, risco de dados desatualizados, inconsistência com CLI

### Manter subdiretório cli/ (ou renomear para terminal/)

**Prós:** Menos alterações no flatten
**Contras:** Path desnecessário, inconsistente com convenção Python `src/` na raiz

## Consequências

A introdução da TUI impacta o projeto em três dimensões: amplia significativamente a experiência do usuário, introduz complexidade de manutenção de duas interfaces, e requer reestruturação do repositório. O balanço é positivo desde que a service layer compartilhada previna duplicação de lógica.

A introdução da TUI impacta o projeto em três dimensões: amplia significativamente a experiência do usuário, introduz complexidade de manutenção de duas interfaces, e requer reestruturação do repositório. O balanço é positivo desde que a service layer compartilhada previna duplicação de lógica.

### Positivas

- Experiência interativa rica para uso diário
- Visual moderno e consistente
- Compartilha 100% da lógica de negócios com CLI (service layer)
- Textual usa Rich internamente (já é dependência)
- Testes automatizados com Pilot
- CLI permanece funcional e independente
- Estrutura flatten simplifica todos os workflows

### Negativas

- Nova dependência (textual ~15MB)
- Complexidade de manutenção em duas interfaces
- Testes TUI são assíncronos (pytest-asyncio necessário)
- TCSS é específico do Textual (vendor lock-in para styling)
- Flatten requer atualização de CI/CD, README, scripts

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
- Pipeline CI/CD verde após flatten

## Referências

- [ADR-006](ADR-006-textual-tui.md) — Decisão original Textual
- [ADR-007](ADR-007-service-layer.md) — Service Layer (consumida pela TUI)
- [ADR-032](ADR-032-branding-repository-naming.md) — Branding e nomenclatura de repositórios
- [Textual Documentation](https://textual.textualize.io/)
- [Textual CSS Reference](https://textual.textualize.io/css_types/)
- [Material Design 3 Color System](https://m3.material.io/styles/color)
