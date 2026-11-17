# Registro de Uso de Inteligência Artificial

**Projeto:** Neighborhood Action Dashboard  
**Integrante:** Gabriel Tancler Armada (RM 574883 · Turma 1CCOR-2026)  
**Disciplina / Entrega:** Global Solution 2026.2 · Ciência da Computação (FIAP)

---

## 1. Papel da Inteligência Artificial no Projeto

O desenvolvimento do código-fonte (`src/sistema.py`), a criação dos dados fictícios (`data/dados.csv` e `data/historico.csv`), a redação da documentação (`README.md` e `docs/relatorio.pdf`) e o roteiro de apresentação (`Roteiro_Video_GS.pdf`) foram realizados integralmente pelo autor do projeto.

A Inteligência Artificial (Google Gemini) foi utilizada exclusivamente na etapa final de **revisão e auditoria cruzada**, sem geração ou substituição do código-fonte original, apoiando nos seguintes pontos:

1. **Auditoria de consistência entre código e documentação:** Verificação se as expressões booleanas (`validar_mudanca`, `filtrar` e `pendente`), a cadeia de validação `if/elif/else` e as justificativas das estruturas de dados descritas no `README.md` e no `docs/relatorio.pdf` correspondiam exatamente à implementação em `src/sistema.py`.
2. **Conferência de integridade dos dados simulados:** Checagem cruzada entre `data/dados.csv` e `data/historico.csv` para confirmar que o status atual de cada uma das 12 ocorrências válidas condizia com o último evento registrado no histórico, que nenhuma data de evento era anterior à abertura e que o registro inconsistente (`013`) disparava corretamente a regra de recusa e reserva de código.
3. **Verificação matemática dos indicadores:** Conferência manual das contagens da matriz $4 \times 3$ (categoria $\times$ situação), das proporções percentuais, da lista de pendências e do cálculo do tempo médio até a conclusão ($5,0\text{ dias}$).
4. **Revisão do checklist de entrega e do roteiro de vídeo:** Conferência dos itens obrigatórios do enunciado (estrutura de pastas, restrição de bibliotecas às fases 1 a 3, placeholder do link do YouTube e fluxo de demonstração no terminal).

---

## 2. Como os Resultados Foram Verificados

Nenhuma alteração sugerida foi incorporada sem validação prática pelo autor:

- **Execução local e casos de teste:** O código `src/sistema.py` foi executado diretamente no terminal (`python src/sistema.py` em Python 3.8 e 3.13) e validado contra os 24 casos de teste documentados na Seção 6 do `docs/relatorio.pdf`, confirmando todas as mensagens de erro, filtros, transições de fila/pilha e cálculos de indicadores.
- **Simulação do roteiro de gravação:** A sequência exata de comandos prevista no roteiro de vídeo (listagem, cadastro da ocorrência `014`, filtro por iluminação e aberta, busca de código inexistente `099`, tentativas de transição de status e consulta à fila, pilha e indicadores) foi testada passo a passo no terminal antes da gravação.
- **Revisão editorial:** Todos os apontamentos de formatação (como quebras de linha nos exemplos de terminal do `README.md` e substituição do marcador `LINK_DO_VIDEO`) foram revisados manualmente antes do envio final.