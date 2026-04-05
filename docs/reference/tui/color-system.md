# ATOMVS Color System

> Status: Proposto
>
> Data: 2026-02-23
>
> ADR-021: Sistema de Cores Semânticas para TUI

## Contexto

O ATOMVS TimeBlock Planner utiliza a paleta Catppuccin Mocha como base visual
para toda a interface de terminal. A aplicação precisa de um sistema de cores
consistente que comunique significado funcional -- status, urgência, feedback
-- de forma intuitiva e independente do tema visual.

Este documento define o mapeamento entre cores semânticas e a paleta Catppuccin,
servindo como referência única para toda a aplicação. Cada decisão de cor foi
fundamentada em padrões industriais de sinalização visual, garantindo que o
sistema seja imediatamente compreensível para qualquer usuário.

### Referências Industriais

O sistema de cores foi projetado com base em dois padrões internacionais de
sinalização e segurança visual:

A **ISO 3864** (Graphical symbols -- Safety colours and safety signs) estabelece
os significados universais: vermelho para perigo e proibição, amarelo para cautela
e aviso, verde para seguro e permitido, azul para informação e obrigação. Esses
mapeamentos fundamentais guiam todas as decisões de cor no ATOMVS.

A **ANSI Z535** (Safety Signs and Colors) refina a hierarquia com a adição do
laranja como cor de warning e standby, diferenciando-o do amarelo de cautela
genérica. No ATOMVS, o laranja (Peach) é utilizado como extremo térmico nos
gradientes de substatus e proximidade, enquanto o amarelo unifica os estados
que requerem atenção do usuário (paused, skip justified, hoje).

## Princípios

O sistema opera sob sete princípios fundamentais que orientam todas as decisões
de design visual:

1. **Cores comunicam função, não decoração** -- cada cor tem um papel semântico definido
2. **Consistência acima de preferência** -- mesma cor = mesmo significado em toda a UI
3. **Catppuccin como fonte de verdade** -- todas as cores devem vir da paleta oficial
4. **Preparado para temas** -- o sistema usa nomes semânticos, não valores hex diretos
5. **Status define cor do bloco** -- timeblocks na agenda usam a cor do status
6. **Tags para reports** -- tags e categorias são usadas em analytics, não na agenda
7. **Subsistemas por contexto** -- domínios diferentes podem reutilizar cores sem conflito

## Paleta Base: Catppuccin Mocha

A paleta Catppuccin Mocha fornece 14 cores de acento e 12 tons neutros organizados
em uma hierarquia clara de backgrounds, textos e superfícies. Todas as cores do
ATOMVS derivam desta paleta sem exceção.

### Backgrounds (hierarquia de profundidade)

Os backgrounds criam profundidade visual através de camadas progressivamente mais
claras, do fundo mais escuro (Crust) até as superfícies interativas (Surface 2).

| Camada     | Nome Catppuccin | Hex       | Uso no ATOMVS                    |
| ---------- | --------------- | --------- | -------------------------------- |
| Base       | Base            | `#1E1E2E` | Fundo principal da aplicação     |
| Elevação 1 | Mantle          | `#181825` | Sidebar, áreas secundárias       |
| Elevação 2 | Crust           | `#11111B` | Rodapé, áreas terciárias         |
| Surface 0  | Surface 0       | `#313244` | Cards, containers elevados       |
| Surface 1  | Surface 1       | `#45475A` | Bordas, separadores, scrollbar   |
| Surface 2  | Surface 2       | `#585B70` | Hover em bordas, scrollbar ativo |

### Texto (hierarquia tipográfica)

A hierarquia tipográfica define cinco níveis de ênfase textual, do texto primário
até o texto completamente muted. Cada nível comunica um grau diferente de
importância na interface.

| Função     | Nome Catppuccin | Hex       | Uso no ATOMVS                     |
| ---------- | --------------- | --------- | --------------------------------- |
| Primário   | Text            | `#CDD6F4` | Corpo, títulos, labels principais |
| Secundário | Subtext 1       | `#BAC2DE` | Subtítulos, descrições            |
| Terciário  | Subtext 0       | `#A6ADC8` | Metadata, informações auxiliares  |
| Dim/Sutil  | Overlay 1       | `#7F849C` | Timestamps, hints, placeholders   |
| Muted      | Overlay 0       | `#6C7086` | Texto desabilitado, pendente      |

### Componentes de Cards

Os cards utilizam uma combinação consistente de cores para bordas, títulos e
elementos interativos como scrollbars. O border_title sempre usa Text para
máxima legibilidade, enquanto informações secundárias usam Subtext 0.

| Elemento         | Cor       | Hex       | Notas                           |
| ---------------- | --------- | --------- | ------------------------------- |
| border_title     | Text      | `#CDD6F4` | Título principal do card        |
| border_subtitle  | Subtext 0 | `#A6ADC8` | Info secundária (ex: "6 pend.") |
| border           | Surface 1 | `#45475A` | Bordas dos containers           |
| separator        | Surface 1 | `#45475A` | Separadores em border_title     |
| scrollbar        | Surface 1 | `#45475A` | Cor padrão                      |
| scrollbar:hover  | Surface 2 | `#585B70` | Hover                           |
| scrollbar:active | Overlay 1 | `#7F849C` | Arrastando                      |

## Cores Semânticas

O mapeamento semântico traduz os padrões industriais ISO 3864 e ANSI Z535 para
a paleta Catppuccin. Cada cor semântica tem um significado único e consistente
em toda a aplicação, eliminando ambiguidade visual.

### Mapeamento Principal

| Nome Semântico | Catppuccin | Hex       | Uso                            |
| -------------- | ---------- | --------- | ------------------------------ |
| success        | Green      | `#A6E3A1` | Concluído, done/full, salvo    |
| below-target   | Rosewater  | `#F5E0DC` | done/partial, abaixo da meta   |
| above-target   | Flamingo   | `#F2CDCD` | done/overdone, acima da meta   |
| over-limit     | Peach      | `#FAB387` | done/excessive, muito acima    |
| warning        | Yellow     | `#F9E2AF` | Paused, skip justificado, hoje |
| error          | Red        | `#F38BA8` | Skip unjustified, overdue      |
| passive-fail   | Maroon     | `#EBA0AC` | Ignored, falha passiva         |
| info           | Blue       | `#89B4FA` | Rescheduled, links, tooltips   |
| accent         | Mauve      | `#CBA6F7` | Running, timer, foco ativo     |
| muted          | Overlay 0  | `#6C7086` | Pendente, inativo, cancelled   |

### Fundamentação (ISO 3864 / ANSI Z535)

A tabela abaixo mostra como cada cor industrial foi traduzida para o contexto
do ATOMVS. O amarelo unifica todos os estados que requerem atenção consciente
do usuário, enquanto o laranja (Peach) funciona como extremo térmico nos
gradientes de substatus e proximidade.

| Cor Industrial | Significado Padrão        | Mapeamento ATOMVS                 |
| -------------- | ------------------------- | --------------------------------- |
| Verde          | Seguro, permitido, ok     | success (done/full)               |
| Amarelo        | Cautela, atenção          | warning (paused, skip j., hoje)   |
| Laranja/Amber  | Warning, standby, extremo | over-limit (excessive, amanhã)    |
| Vermelho       | Perigo, proibição, erro   | error (skip unjustified, overdue) |
| Azul           | Informação, obrigatório   | info (links, rescheduled)         |

## Gradiente Térmico Quente

As quatro cores quentes da paleta Catppuccin (Yellow, Peach, Flamingo, Rosewater)
formam um gradiente térmico reutilizado em dois subsistemas: o heat de substatus
DONE nos hábitos e o heat de proximidade nas tasks. A direção do calor varia
conforme o contexto, mas a progressão térmica é consistente.

```
  Quente <== ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ==> Frio

  Yellow      Peach       Flamingo    Rosewater
  #F9E2AF     #FAB387     #F2CDCD     #F5E0DC
```

No **substatus DONE**, o calor aumenta conforme o desvio do ideal: Green (centro
frio) → Rosewater (abaixo) → Flamingo (acima) → Peach (muito acima). Na
**proximidade de Tasks**, o calor aumenta conforme a urgência: Rosewater (longe)
→ Flamingo (próximo) → Peach (amanhã) → Yellow (hoje).

## Escala de Agência do Usuário

O sistema de cores reflete o grau de consciência e agência do usuário em relação
ao resultado de cada hábito. Quanto mais consciente e ativo o usuário foi na
decisão, mais "controlada" é a cor. Quanto mais passiva a falha, mais grave o tom.

```
  ✓   done/full       Green      → Fez conforme planejado
  ✓~  done/partial    Rosewater  → Fez abaixo, mas fez
  ✓+  done/overdone   Flamingo   → Fez acima (informativo)
  ✓!  done/excessive  Peach      → Fez muito acima (over-limit)
  !   skip/justified  Yellow     → Desviou com consciência
  ✗!  skip/unjustif.  Red        → Negligência ativa
  ✗?  ignored         Maroon     → Omissão passiva
```

## Heat de Substatus DONE

Os substatus do DONE formam um gradiente térmico próprio, onde o Green (full)
representa o centro ideal "frio" e os desvios em qualquer direção esquentam
progressivamente. Isso permite ao usuário identificar instantaneamente se
o resultado está abaixo, no alvo, ou acima da meta.

O desvio para baixo (partial) usa Rosewater, um tom suave e encorajador que
comunica "você fez algo, mas ficou abaixo." Os desvios para cima esquentam
progressivamente: Flamingo para overdone (levemente acima) e Peach para
excessive (muito acima, laranja quente). Essa progressão térmica é independente
do sistema semântico principal e só se aplica aos substatus DONE.

```
  Green => Rosewater => Flamingo => Peach
  ideal    abaixo       acima       muito acima
  frio     morno        quente      hot
```

| Substatus | Cor       | Hex       | Ícone | Barra  | Threshold |
| --------- | --------- | --------- | ----- | ------ | --------- |
| full      | Green     | `#A6E3A1` | ✓     | ▪▪▪▪   | 90-110%   |
| partial   | Rosewater | `#F5E0DC` | ✓~    | ▪▪░░   | < 90%     |
| overdone  | Flamingo  | `#F2CDCD` | ✓+    | ▪▪▪▪▪  | 110-150%  |
| excessive | Peach     | `#FAB387` | ✓!    | ▪▪▪▪▪▪ | > 150%    |

## Status de HabitInstance (BR-HABITINSTANCE-001/002)

Os hábitos são o domínio mais rico em estados do sistema. Cada hábito possui
um status principal e, nos casos de DONE e NOT_DONE, um substatus que refina
o resultado. O running é o único estado que colore a linha inteira em Mauve,
criando um destaque visual forte e inequívoco.

### Status Principal

| Status   | Cor         | Ícone | Significado                |
| -------- | ----------- | ----- | -------------------------- |
| pending  | muted       | ·     | Aguardando execução        |
| done     | (substatus) | ✓     | Concluído (ver substatus)  |
| not_done | error       | (var) | Não realizado (ver subst.) |
| running  | accent      | ▶     | Em execução agora          |
| paused   | warning     | ⏸     | Pausado, aguardando ação   |

### Substatus NOT_DONE (BR-HABITINSTANCE-002)

Os substatus de NOT_DONE refletem três níveis de responsabilidade do usuário.
O skip justificado é um desvio consciente e documentado -- a cor amarela comunica
cautela sem gravidade. O skip injustificado é negligência ativa, representada em
vermelho. O ignored é a pior situação: a omissão passiva onde o hábito expirou
sem qualquer ação, representada em Maroon.

| Substatus           | Cor          | Ícone | Significado               |
| ------------------- | ------------ | ----- | ------------------------- |
| skipped_justified   | warning      | !     | Desvio consciente         |
| skipped_unjustified | error        | ✗!    | Negligência ativa         |
| ignored             | passive-fail | ✗?    | Omissão passiva (timeout) |

### Resumo de Ícones

Cada ícone combina um símbolo base com um modificador que refina o significado.
Os ícones de DONE usam ✓ como base com modificadores ~, + e !. Os ícones de
NOT_DONE usam ✗ como base com modificadores ! e ?. Essa consistência permite
que o usuário decodifique rapidamente qualquer combinação.

| Ícone | Significado                     | Cor       |
| ----- | ------------------------------- | --------- |
| ✓     | Concluído com sucesso           | Green     |
| ✓~    | Concluído parcialmente          | Rosewater |
| ✓+    | Concluído acima da meta         | Flamingo  |
| ✓!    | Concluído excessivamente        | Peach     |
| !     | Desvio consciente (justificado) | Yellow    |
| ✗!    | Negligência ativa (unjustified) | Red       |
| ✗?    | Omissão passiva (ignored)       | Maroon    |
| ▶     | Em execução                     | Mauve     |
| ⏸     | Pausado (atenção)               | Yellow    |
| ·     | Pendente, aguardando            | Overlay 0 |

## Status de Timer (BR-TIMER-002)

O timer possui quatro estados simples que cobrem todo o ciclo de vida de uma
sessão. O running e o paused são estados transitórios (Mauve e Yellow), enquanto
done e cancelled são estados terminais (Green e Red).

| Status    | Cor     | Ícone | Significado                 |
| --------- | ------- | ----- | --------------------------- |
| running   | accent  | ▶     | Timer contando              |
| paused    | warning | ⏸     | Timer pausado               |
| done      | success | ✓     | Sessão finalizada (salva)   |
| cancelled | error   | ✗     | Sessão cancelada (descarta) |

## Status de Event (EventStatus)

Os eventos seguem um ciclo de vida similar ao timer, mas com dois estados
adicionais: planned (agendado, ainda não iniciou) e rescheduled (reagendado
para outra data). O Blue para rescheduled comunica informação sem gravidade --
é um aviso neutro de que o evento mudou de data.

| Status      | Cor     | Ícone | Significado  |
| ----------- | ------- | ----- | ------------ |
| planned     | muted   | ·     | Agendado     |
| in_progress | accent  | ▶     | Em andamento |
| paused      | warning | ⏸     | Pausado      |
| completed   | success | ✓     | Concluído    |
| cancelled   | error   | ✗     | Cancelado    |
| rescheduled | info    | ↻     | Reagendado   |

## Status de Task (BR-TASK-001/002)

Tasks são intencionalmente simples (BR-TASK-006). O modelo de dados usa apenas
completed_datetime como campo binário. Na TUI, a representação visual combina
o estado lógico com urgência temporal, criando um gradiente de proximidade que
comunica prioridade sem necessidade de leitura atenta.

### Colunas de Task na TUI

A ordem de leitura segue o fluxo natural: ícone identifica o status, nome diz
o que é, proximidade mostra a urgência relativa, data e horário dão o contexto
absoluto.

```plaintext
  ícone | nome | proximidade | data | horário
```

### Estados Visuais de Task

A organização do card segue a ordem: pendentes (por proximidade crescente),
completed, cancelled, e overdue (por data crescente, mais antiga primeiro).
Não há separadores horizontais -- a mudança de cor e ícone já comunica a
transição entre grupos.

| Estado    | Cor          | Ícone | Strike | Significado                 |
| --------- | ------------ | ----- | ------ | --------------------------- |
| overdue   | error        | ✗     | não    | Vencida, precisa resolver   |
| pendente  | (heat prox.) | (var) | não    | Ativa (ver subsistema heat) |
| completed | success      | ✓     | sim    | Concluída                   |
| cancelled | muted        | ✗     | sim    | Cancelada, descartada       |

## Subsistema: Heat de Proximidade (Tasks)

O heat de proximidade é um subsistema de cores exclusivo do card de Tasks. Ele
define a cor de cada linha com base na distância temporal até o prazo, criando
um gradiente térmico que vai do quente (urgente) ao frio (distante).

A primeira metade do gradiente (até 7 dias) utiliza as quatro cores quentes da
Catppuccin: Yellow, Peach, Flamingo e Rosewater. A segunda metade (além de 7
dias) transiciona para a hierarquia tipográfica neutra. Essa fronteira marca
visualmente a diferença entre "esta semana" (cores quentes, atenção) e "depois"
(tons neutros, pode esperar).

A coluna de proximidade sempre usa valores relativos (Hoje, Amanhã, 3 dias,
1 semana), nunca nomes de dias da semana. A data absoluta aparece na coluna
"data" separada.

### Mapeamento Proximidade → Cor

| Proximidade | Cor       | Hex       | Temperatura |
| ----------- | --------- | --------- | ----------- |
| Hoje        | Yellow    | `#F9E2AF` | Quente      |
| Amanhã      | Peach     | `#FAB387` | Morno-forte |
| 2-3 dias    | Flamingo  | `#F2CDCD` | Morno       |
| 4-7 dias    | Rosewater | `#F5E0DC` | Tépido      |
| 1-2 semanas | Subtext 1 | `#BAC2DE` | Fresco      |
| 2+ semanas  | Subtext 0 | `#A6ADC8` | Frio        |
| 1+ mês      | Overlay 0 | `#6C7086` | Congelado   |

### Ícone por Proximidade

Tasks com prazo hoje ou amanhã usam o ícone de atenção (!), comunicando urgência
imediata. Tasks com prazos mais distantes usam o ponto neutro (·).

| Proximidade | Ícone | Lógica                |
| ----------- | ----- | --------------------- |
| Hoje        | !     | Atenção imediata      |
| Amanhã      | !     | Atenção próxima       |
| 2+ dias     | ·     | Sem urgência imediata |

## Cores de TimeBlock na Agenda

Os blocos de tempo na agenda usam a cor do status, não da tag. Essa decisão
simplifica a leitura visual: ao olhar a agenda, o usuário vê imediatamente o
resultado de cada bloco sem precisar decodificar categorias. As tags e categorias
são usadas exclusivamente em reports e analytics.

### Formato de Linha na Agenda

O formato utiliza um interponto como separador visual limpo entre o nome do
hábito e sua duração planejada. O ícone e substatus ficam à direita, completando
a linha com o resultado. Running e paused usam nome em bold para destacar que
são estados ativos que requerem atenção imediata.

```plaintext
  horário ─┼─ nome · duração        ícone substatus
```

### Mapeamento Status → Cor do Bloco

| Status             | Cor do Fill | Opacidade | Padrão |
| ------------------ | ----------- | --------- | ------ |
| done/full          | Green       | 100%      | solid  |
| done/partial       | Rosewater   | 80%       | solid  |
| done/overdone      | Flamingo    | 100%      | solid  |
| done/excessive     | Peach       | 100%      | solid  |
| running            | Mauve       | 100%      | dense  |
| paused             | Yellow      | 60%       | half   |
| not_done/justified | Yellow      | 40%       | dash   |
| not_done/unjust.   | Red         | 30%       | dash   |
| not_done/ignored   | Maroon      | 20%       | dash   |
| pending            | Overlay 0   | 30%       | dim    |
| cancelled          | Overlay 0   | 20%       | dash   |

### Background de TimeBlock em TUI

O Textual suporta background RGBA em widgets via TCSS. Cada bloco utiliza
um widget com background da cor do status em opacidade baixa, diferenciando-o
visualmente do background do card (Surface 0).

```css
.timeblock-done {
  background: $green 15%;
}
.timeblock-partial {
  background: $rosewater 12%;
}
.timeblock-overdone {
  background: $flamingo 12%;
}
.timeblock-excessive {
  background: $peach 12%;
}
.timeblock-running {
  background: $mauve 18%;
}
.timeblock-paused {
  background: $yellow 10%;
}
.timeblock-justified {
  background: $yellow 6%;
}
.timeblock-unjustif {
  background: $red 5%;
}
.timeblock-ignored {
  background: $maroon 4%;
}
.timeblock-pending {
  background: $overlay0 8%;
}
.timeblock-cancelled {
  background: $overlay0 4%;
}
```

## Tags/Categorias (Reports Only)

As tags definem categorias para agrupamento em relatórios e analytics. Na agenda
visual, a cor de cada bloco vem do status -- as tags não influenciam a aparência
dos timeblocks.

| Tag/Categoria | Catppuccin | Hex       | Exemplos                       |
| ------------- | ---------- | --------- | ------------------------------ |
| Saúde         | Teal       | `#94E2D5` | Academia, natação, boxe        |
| Trabalho      | Blue       | `#89B4FA` | Deep work, reuniões, PRs       |
| Estudo        | Mauve      | `#CBA6F7` | Cursos, leitura técnica        |
| Pessoal       | Pink       | `#F5C2E7` | Música, hobbies                |
| Alimentação   | Green      | `#A6E3A1` | Café da manhã, almoço, jantar  |
| Social        | Peach      | `#FAB387` | Eventos, festivais, networking |
| Descanso      | Lavender   | `#B4BEFE` | Sono, pausas, relaxamento      |
| Organização   | Sky        | `#89DCFE` | Planejamento, limpeza, admin   |
| Outro         | Overlay 1  | `#7F849C` | Sem categoria definida         |

## Feedback do Sistema

As mensagens de feedback da aplicação seguem o mesmo sistema semântico, garantindo
consistência entre a interface visual dos hábitos e as notificações do sistema.

| Tipo       | Cor          | Ícone | Uso                        |
| ---------- | ------------ | ----- | -------------------------- |
| Sucesso    | success      | ✓     | Operação concluída         |
| Aviso      | warning      | !     | Atenção necessária         |
| Erro       | error        | ✗     | Falha, ação bloqueada      |
| Info       | info         | i     | Informação, tooltips       |
| Ativo/Foco | accent       | ▶     | Timer, item selecionado    |
| Over-limit | over-limit   | ✓!    | Excessive, acima do limite |
| Passivo    | passive-fail | ✗?    | Timeout, omissão           |
| Neutro     | muted        | ·     | Inativo, desabilitado      |

## Uso do Azul (Info) na Aplicação

O azul é reservado exclusivamente para informação neutra, sem conotação de
status positivo ou negativo. Seus usos incluem:

- **Rescheduled events**: evento reagendado para outra data
- **Links e URLs**: texto clicável no TUI
- **Tooltips e help text**: informações contextuais
- **Breadcrumbs/navegação**: indicação de localização
- **Notificações informativas**: mensagens do sistema sem urgência

## Barras de Progresso

As barras de progresso seguem uma escala de três faixas que comunicam rapidamente
o nível de completude geral.

| Faixa  | Cor     | Hex       | Feedback         |
| ------ | ------- | --------- | ---------------- |
| >= 80% | success | `#A6E3A1` | Excelente        |
| >= 50% | warning | `#F9E2AF` | Atenção          |
| < 50%  | error   | `#F38BA8` | Precisa melhorar |

## Régua de Horários (Agenda)

A régua lateral da agenda utiliza tons discretos para não competir visualmente
com os blocos de tempo. Apenas o horário atual recebe destaque em Mauve bold,
criando um ponto de referência imediato.

| Elemento           | Cor          | Hex       | Notas                  |
| ------------------ | ------------ | --------- | ---------------------- |
| Horário padrão     | Overlay 0    | `#6C7086` | Labels dim na régua    |
| Horário atual      | Mauve (bold) | `#CBA6F7` | Destaque do "agora"    |
| Conector início    | Surface 1    | `#45475A` | Início de bloco        |
| Conector transição | Surface 1    | `#45475A` | Transição entre blocos |
| Slot livre         | Surface 1    | `#45475A` | Gap sem blocos         |

## Migração: #B388FF → #CBA6F7

O valor `#B388FF` (roxo não-Catppuccin) presente no código atual deve ser
substituído por `#CBA6F7` (Mauve oficial) nos seguintes arquivos:

- `src/timeblock/tui/screens/dashboard.py`
- `src/timeblock/tui/widgets/header_bar.py`
- `src/timeblock/tui/styles/theme.tcss`

## Cores Catppuccin Reservadas

Algumas cores da paleta não possuem uso semântico definido no momento, mas estão
reservadas para futuras necessidades.

| Nome     | Hex       | Uso atual / potencial     |
| -------- | --------- | ------------------------- |
| Pink     | `#F5C2E7` | Tag Pessoal (reports)     |
| Lavender | `#B4BEFE` | Tag Descanso (reports)    |
| Sky      | `#89DCFE` | Tag Organização (reports) |
| Sapphire | `#74C7EC` | (reservado) highlights    |

## Implementação: Variáveis CSS (Textual)

```scss
$success: #a6e3a1;
$below-target: #f5e0dc;
$above-target: #f2cdcd;
$over-limit: #fab387;
$warning: #f9e2af;
$error: #f38ba8;
$passive-fail: #eba0ac;
$info: #89b4fa;
$accent: #cba6f7;
$muted: #6c7086;
```

## Localização no Projeto

```
timeblock-organizer/
├── docs/
│   └── tui/
│       └── color-system.md        <== Este arquivo (ref técnica)
└── site/
    └── themes/
        ├── catppuccin-mocha.html  <== Showcase visual
        └── assets/
```

## Referências

- **ISO 3864**: Graphical symbols -- Safety colours and safety signs
- **ANSI Z535**: Safety Signs and Colors
- Catppuccin Style Guide: <https://github.com/catppuccin/catppuccin/blob/main/docs/style-guide.md>
- Catppuccin Palette: <https://github.com/catppuccin/catppuccin>
- BR-HABITINSTANCE-001/002/003
- BR-TIMER-002/003
- BR-TASK-001/002/005/006
