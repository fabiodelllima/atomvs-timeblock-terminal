# Estratégia de Snapshot Testing para TUI

**Status:** RASCUNHO — aguardando revisão e aprovação

**Criado:** 2026-03-23

**Referências:**
- pytest-textual-snapshot (Textualize, 2024)
- Textual Testing Guide (textual.textualize.io/guide/testing)
- ADR-037: Testes E2E com Textual Pilot

---

## 1. Contexto e Motivação

O ATOMVS Time Planner Terminal possui 1284 testes (mar/2026), com cobertura extensiva de lógica via `pilot.press()` + asserções de estado. Porém, esses testes não validam renderização visual — é possível que um bloco de agenda renderize com cores trocadas, alinhamento quebrado ou accent bar ausente sem que nenhum teste falhe.

Snapshot testing preenche essa lacuna: captura SVGs da TUI em execução e compara com baselines aprovadas. Mudanças visuais — intencionais ou acidentais — geram falhas com diff visual, permitindo detecção automática de regressões visuais.

---

## 2. Ferramenta: pytest-textual-snapshot

O `pytest-textual-snapshot` é o plugin oficial da Textualize, mantido pela mesma equipe que desenvolve o Textual. Internamente, o Textual usa snapshot testing para validar todos os widgets builtin em cada release.

**Instalação:**
```bash
pip install pytest-textual-snapshot
```

**Como funciona:**

1. O teste instancia a app Textual (sem rodar)
2. O plugin renderiza a app num terminal virtual
3. Gera um SVG da tela renderizada
4. Na primeira execução, salva como baseline (teste falha — esperado)
5. Nas execuções seguintes, compara SVG atual com baseline
6. Se diferir, gera report HTML com diff visual lado a lado

**Exemplo básico:**
```python
def test_dashboard_initial_state(snap_compare):
    """Snapshot: dashboard renderiza corretamente com rotina ativa."""
    assert snap_compare("src/timeblock/tui/app.py")
```

**Com interação antes da captura:**
```python
def test_dashboard_after_creating_habit(snap_compare):
    """Snapshot: dashboard após criar hábito via modal."""
    async def run_before(pilot):
        await pilot.press("tab", "tab")  # Foca panel hábitos
        await pilot.press("n")            # Abre FormModal
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

    assert snap_compare(
        "src/timeblock/tui/app.py",
        run_before=run_before,
        terminal_size=(120, 40),
    )
```

**Atualizando baselines:**
```bash
# Após validar visualmente que o output está correto:
pytest tests/snapshot/ --snapshot-update
```

---

## 3. Organização no Projeto
```
tests/
├── snapshot/                          # Snapshot tests
│   ├── __snapshots__/                 # SVGs gerados (gittracked)
│   ├── test_dashboard_snapshots.py    # Dashboard states
│   ├── test_agenda_snapshots.py       # Agenda rendering
│   └── test_modal_snapshots.py        # Modais (FormModal, ConfirmDialog)
├── unit/                              # Lógica pura
├── integration/                       # Service + DB
├── e2e/                               # Fluxos completos com pilot
└── bdd/                               # Cenários Gherkin
```

Os SVGs em `__snapshots__/` são rastreados pelo git. São a "verdade visual" do projeto — qualquer mudança neles deve ser revisada no MR.

---

## 4. O que Testar com Snapshots

### Prioridade alta (implementar primeiro)

- Dashboard vazio (sem rotina) — placeholder com hint
- Dashboard com rotina ativa + 3 hábitos + 2 tasks — estado padrão
- Agenda com blocos sobrepostos (3 colunas) — cenário principal
- Agenda com blocos consecutivos — transição título a título
- Bloco mínimo 15min — 2 linhas (título + end line)

### Prioridade média

- FormModal aberto (criação de hábito) — layout do modal
- ConfirmDialog aberto (deleção) — layout do modal
- Timer ativo com elapsed visível — atualização live
- Metrics panel com dados reais — formatação de streaks

### Prioridade baixa (futuro)

- Cada screen (Routines, Habits, Tasks, Timer) em estado padrão
- Help overlay (?) aberto
- Sidebar navigation highlights
- Responsividade em 80, 120, 160 colunas

---

## 5. Integração com CI
```yaml
# .gitlab-ci.yml (proposta)
test:snapshot:
  stage: test
  script:
    - python -m pytest tests/snapshot/ -v
  allow_failure: true  # Remover quando baselines estiverem estáveis
  artifacts:
    when: on_failure
    paths:
      - tests/snapshot/__snapshots__/
    expire_in: 7 days
```

---

## 6. Fluxo de Trabalho

### Ao criar novo snapshot test

1. Escrever o teste em `tests/snapshot/`
2. Rodar `pytest tests/snapshot/test_novo.py` — vai falhar (sem baseline)
3. Abrir o report HTML, verificar visualmente
4. Se correto: `pytest tests/snapshot/test_novo.py --snapshot-update`
5. Commitar o SVG junto com o teste

### Ao alterar renderização visual

1. Rodar `pytest tests/snapshot/` — falhas esperadas
2. Verificar cada diff no report HTML
3. Se todas as mudanças são intencionais: `pytest tests/snapshot/ --snapshot-update`
4. Commitar SVGs atualizados com mensagem descritiva

### Ao receber falha inesperada no CI

1. Baixar artifacts do job
2. Comparar SVGs — identificar a mudança visual
3. Se regressão: corrigir código
4. Se mudança intencional esquecida: atualizar baselines

---

## 7. Relação com Outros Tipos de Teste

| Tipo | Valida | Ferramenta |
| ---- | ------ | ---------- |
| Unit | Lógica de negócio isolada | pytest + mocks |
| Integration | Service + DB | pytest + test engine |
| E2E (pilot) | Fluxos de interação | pytest-asyncio + Textual pilot |
| Snapshot | Renderização visual | pytest-textual-snapshot |
| BDD | Cenários de aceite | pytest-bdd + Gherkin |
| Visual (futuro) | Sessões gravadas | pexpect + asciinema |

Snapshot tests NÃO substituem testes com pilot. O pilot valida "pressionar Tab foca o próximo panel" (lógica). O snapshot valida "o panel focado tem borda branca e o desfocado tem borda cinza" (visual).

---

## 8. Decisões Pendentes

- Job CI separado ou dentro de `test:unit`?
- `terminal_size` padrão para todos os snapshots (proposta: 120x40)
- Política de atualização de baselines — quem aprova?
- Frequência mínima de snapshot tests por BR-TUI?
