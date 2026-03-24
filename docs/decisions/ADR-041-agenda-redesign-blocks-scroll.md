# ADR-041: Redesign da Agenda Panel — blocos contínuos, scroll horizontal e granularidade 15min

**Status:** Proposto

## Contexto

A renderização atual da Agenda Panel utiliza linhas horizontais (`───`) na régua de horário que atravessam os blocos de tempo coloridos, criando intersecções (`─┼─`) que quebram a continuidade visual dos blocos. Com múltiplas colunas de sobreposição, o problema se multiplica: 3 colunas geram 4 intersecções por linha, tornando o layout ilegível. Títulos truncam severamente em 3+ colunas porque a largura de cada coluna é limitada pela viewport do painel.

Adicionalmente, a granularidade temporal da régua precisa ser redefinida: cada linha visual corresponde a 15 minutos (não 30), com labels de hora exibidos a cada 30min (2 linhas). Blocos de tempo podem iniciar e terminar em qualquer múltiplo de 15min (:00, :15, :30, :45).

## Decisão

### Renderização de blocos

1. Blocos de tempo são retângulos contínuos de cor sólida, sem interrupção por linhas horizontais.
2. Primeira linha do bloco (linha de início): `{título} {ícone_status}` — sem `▌`, sem cor de fundo. Texto limpo.
3. Linhas seguintes do bloco: `▌{cor_sólida}` — accent bar na borda esquerda.
4. Accent bar (`▌`) na cor saturada do hábito (paleta Catppuccin Mocha).
5. Fundo do bloco na cor suave (mesma família, luminosidade alta).
6. Áreas sem bloco: pontilhado sutil (`· · · ·`) como guia visual, ou vazio.

### Granularidade temporal

7. Cada linha da agenda = 15 minutos.
8. Labels de hora exibidos a cada 2 linhas (30min): a primeira linha mostra `HH:MM`, a segunda é vazia na coluna de hora.
9. Blocos iniciam/terminam em qualquer múltiplo de 15min.
10. A linha correspondente ao horário de término do bloco AINDA exibe cor (`▌░░░`). A linha seguinte é livre.
11. Blocos consecutivos sem gap: o título do segundo bloco substitui diretamente a última linha de cor do primeiro.

### Scroll horizontal

12. Scroll horizontal interno no painel da agenda quando o conteúdo excede a viewport.
13. Input: Shift + scroll wheel do mouse; Shift+h / Shift+l (vi-like).
14. Margem de horas fixa à esquerda — não scrolla horizontalmente (padrão Google Calendar).
15. Largura mínima por coluna de bloco: 18 caracteres. Não encolhe abaixo disso.
16. Gap entre colunas: 1 caractere vazio.
17. Indicador visual de overflow: `→` no BorderTitle quando há conteúdo à direita.
18. Linha vertical `│` interna (separador horas/blocos) permanece fixa no scroll H.

### Layout interno

19. Implementação via `Horizontal(horas_widget, ScrollableContainer(blocos_widget))` no Textual.
20. `horas_widget`: Static com a coluna de horas + separador `│`, posição fixa.
21. `blocos_widget`: ScrollableContainer com scroll_x habilitado.

## Consequências

### Positivas

- Blocos visuais são unidades contínuas, legíveis em qualquer número de colunas.
- Scroll horizontal permite blocos largos (18+ chars) independente da viewport.
- Granularidade de 15min permite representação precisa de horários não-redondos.
- Padrão de accent bar (`▌`) é consistente com TUIs modernas (lazygit, etc.).

### Negativas

- Refatoração significativa de `AgendaPanel._render_slot()` e renderização interna.
- Lógica de iteração muda de slots de 30min para linhas de 15min.
- Scroll horizontal adiciona complexidade de input handling (Shift+scroll, conflito com ←→).
- Testes e2e existentes do AgendaPanel podem precisar de atualização.

## Referências

- DT-045: Renderização multi-coluna para eventos sobrepostos (implementação parcial existente)
- DT-061: Scroll horizontal no AgendaPanel
- DT-062: Renderização de blocos contínuos
- BR-TUI-031: Scroll horizontal da agenda
- BR-TUI-032: Renderização de blocos de tempo na agenda

---

**Data:** 2026-03-22
