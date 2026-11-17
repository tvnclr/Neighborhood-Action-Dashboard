<p align="center">
  <a href="https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" width="40%"></a>
</p>

# Neighborhood Action Dashboard

Global Solution 2026.2 · Graduação ON em Ciência da Computação · FIAP

## 👨‍🎓 Integrante

Equipe: Gabriel Tancler Armada (projeto individual).

- Gabriel Tancler Armada · RM 574883 · Turma 1CCOR-2026

## 👩‍🏫 Professores

### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi Chiovato</a>

## 📜 Descrição

### Bairro, problema e público

O **Jardim Horizonte** é um bairro fictício, criado para esta simulação. Os moradores registram problemas de infraestrutura e conservação em quatro categorias: **iluminação**, **acessibilidade**, **limpeza** e **conservação de espaços coletivos**. Sem um lugar organizado para essas demandas, fica difícil saber quais problemas se repetem, quais continuam sem resposta e há quanto tempo.

O sistema é um painel comunitário em texto: registra ocorrências, permite consultar e filtrar, acompanha a mudança de situação de cada uma e calcula indicadores simples. O público é a associação de moradores e quem acompanha as demandas do bairro. O painel não se conecta a nenhum órgão público e não promete atendimento: ele organiza a informação para que a comunidade saiba o que cobrar primeiro.

### Dados

Os dados ficam em dois arquivos de texto separados por `;`, lidos com `open()` e `split()`. Cadastros e mudanças de situação são gravados nesses mesmos arquivos na hora em que acontecem:

- `data/dados.csv`: uma ocorrência por linha, com os campos `codigo;categoria;descricao;local;dia_abertura;status`. **Todos os campos são obrigatórios.** São 13 linhas: 12 válidas e 1 inconsistente de propósito (a 013, sem categoria), que a validação recusa na leitura.
- `data/historico.csv`: 10 eventos de acompanhamento, cada um com `codigo;dia;status_anterior;status_novo`.
- `data/originais/`: cópia dos dois arquivos no estado inicial, que o programa nunca altera.

As datas são simuladas em "dias" (dia 1, dia 2...), e o dia atual da simulação é o **dia 16**. As categorias e situações usam valores padronizados no arquivo (`iluminacao`, `em_analise`...) e são exibidas com acento na tela.

| Situação | Significado |
|---|---|
| `aberta` | registrada e ainda não examinada |
| `em análise` | examinada, aguardando solução |
| `concluída` | problema resolvido |

A situação só avança uma etapa por vez: aberta → em análise → concluída.

## 🧱 Estruturas de dados

| Estrutura | Onde | Por que essa |
|---|---|---|
| Lista | `base["lista"]`, todas as ocorrências | Guarda a ordem de registro e é o que os filtros, a listagem e os indicadores percorrem. |
| Dicionário | `base["por_codigo"]`, código → ocorrência | A busca por código vai direto ao registro, sem percorrer a lista. |
| Fila | `base["fila"]`, códigos das ocorrências abertas | A demanda registrada primeiro é examinada primeiro (FIFO). A opção 6 tira o início da fila e passa para "em análise"; se a ocorrência já tiver mudado de situação por outro caminho, ela é descartada e a próxima é examinada. |
| Pilha | `base["pilha"]`, eventos de mudança | O evento mais recente fica no topo (LIFO), que é o que interessa ao consultar as últimas atualizações. Cada evento é um dicionário com código, dia, situação anterior e situação nova. |
| Hierarquia | dicionário aninhado bairro → categoria → códigos | Mostra o bairro como uma árvore e deixa visível onde os problemas se concentram. Também prepara o sistema para mais bairros. |
| Matriz | lista de listas 4 × 3 (categoria × situação) | Cruza as duas classificações numa tabela só, que é a base dos indicadores. A linha e a coluna de cada ocorrência saem de uma busca linear nas listas de categorias e situações. |

## 🔀 Regras lógicas

**Cadastro e leitura** (`validar_ocorrencia`): `if` algum campo obrigatório está vazio → recusa, dizendo qual campo; `elif` o código não tem 3 dígitos → recusa; `elif` o código já existe → recusa (os códigos do arquivo ficam reservados, inclusive o da ocorrência recusada); `elif` a categoria não é uma das quatro → recusa; `elif` a descrição ou o local contêm `;` (o separador do arquivo) → recusa; `elif` a situação é desconhecida → recusa; `elif` o dia está fora de 1 a 16 → recusa; `else` → aceita. Uma ocorrência nova entra sempre como `aberta` e vai para o fim da fila.

**Atualização de situação** (`validar_mudanca`). A expressão booleana principal é:

```python
novo in STATUS and novo != atual and not atual == "concluida"
```

Se ela for falsa, o sistema diz qual parte falhou: situação desconhecida, situação igual à atual ou ocorrência já concluída (concluída não volta atrás). Se for verdadeira, ainda é preciso que a nova situação seja a etapa seguinte; por isso, de `aberta` direto para `concluída` é recusado, com o motivo explicado.

**Filtro** (`filtrar`): `(categoria == "" or ocorrencia["categoria"] == categoria) and (status == "" or ocorrencia["status"] == status)`. Deixar um campo vazio (Enter) significa "qualquer", então o mesmo filtro serve para categoria, para situação ou para as duas juntas.

**Pendência** (`pendente`): `not ocorrencia["status"] == "concluida" and (dias_aberta > 10 or ocorrencia["categoria"] == "acessibilidade")`. Uma demanda vira pendência quando passou do prazo de referência de 10 dias sem ser concluída, ou na hora, se for de acessibilidade, porque esse tipo de problema impede alguém de circular.

Toda entrada inválida no menu (opção, número de categoria, código inexistente) gera uma mensagem dizendo o que estava errado, e nada é alterado nem gravado. No cadastro, uma categoria inválida é recusada logo depois de escolhida, sem pedir os outros campos.

**Gravação** (`acrescentar_linha`, `gravar_situacao`): um cadastro aceito vira uma linha nova no fim de `data/dados.csv`. Uma mudança de situação aceita vira uma linha nova no fim de `data/historico.csv` e troca só a coluna `status` daquela ocorrência em `data/dados.csv`; as outras linhas, inclusive a 013 recusada, ficam exatamente como estavam.

## 📊 Indicadores

| Indicador | Fórmula |
|---|---|
| Total e proporção por categoria | quantidade da categoria / total × 100 |
| Total e proporção por situação | quantidade da situação / total × 100 |
| Matriz categoria × situação | contagem de cada par, com total da linha |
| Tempo médio até a conclusão | soma de (dia da conclusão − dia de abertura) / número de concluídas |
| Pendências | quantidade de ocorrências que satisfazem a regra de pendência |

Com os dados iniciais: 12 ocorrências, sendo 5 abertas (41,7 %), 4 em análise (33,3 %) e 3 concluídas (25 %). Iluminação é a categoria mais frequente (4 de 12). As três concluídas levaram 4, 3 e 8 dias, o que dá um tempo médio de 5 dias. Há 5 pendências: 003, 004, 005, 007 e 010.

**Interpretação:** três em cada quatro ocorrências ainda não foram resolvidas, e todas as três de acessibilidade continuam abertas ou em análise. Limpeza é a única categoria em que a maioria já foi concluída. Para a associação de moradores, a prioridade sugerida pelos números é cobrar primeiro acessibilidade e as demandas mais antigas, e acompanhar a iluminação, que concentra o maior volume.

## 🔧 Como executar

Precisa só do Python 3.8 ou mais recente. Nenhuma biblioteca externa é usada.

No VS Code: **File > Open Folder** na pasta do projeto, **Terminal > New Terminal** e:

```
python src/sistema.py
```

O programa acha a pasta `data/` a partir do lugar do próprio `sistema.py`, então também roda de outra pasta, pelo botão de executar do editor ou com dois cliques no arquivo.

Cadastros e mudanças de situação ficam salvos em `data/` e continuam lá na próxima execução. Para voltar ao estado inicial (por exemplo, antes de repetir a demonstração), rode na pasta do projeto:

```
Copy-Item data/originais/*.csv data/
```

No Linux ou macOS, o equivalente é `cp data/originais/*.csv data/`.

## ▶️ Exemplo de uso

Trechos da execução real, a partir dos dados iniciais, seguindo o exemplo do enunciado.

Início:

```
========================================================================
NEIGHBORHOOD ACTION DASHBOARD - Jardim Horizonte (simulação)
========================================================================
12 ocorrências carregadas, 10 eventos de histórico, 5 demandas abertas na fila.
Registro 013 recusado na leitura: campo obrigatório 'categoria' vazio.
Situações:
  aberta = registrada e ainda não examinada
  em análise = examinada, aguardando solução
  concluída = problema resolvido
```

Cadastro da ocorrência 014 (opção 2):

```
========================================================================
CADASTRAR OCORRÊNCIA
========================================================================
Código (Enter para usar 014): Categoria:
  1 - Iluminação
  2 - Acessibilidade
  3 - Limpeza
  4 - Conservação
Número da categoria: Descrição breve: Local genérico (ex.: Praça Central): Dia de abertura (1 a 16): Ocorrência 014 cadastrada como aberta, salva e colocada no fim da fila.
```

Consulta das ocorrências abertas de iluminação (opção 4):

```
Opção: Categoria (Enter = qualquer):
  1 - Iluminação
  2 - Acessibilidade
  3 - Limpeza
  4 - Conservação
Número da categoria: Situação (Enter = qualquer):
  1 - aberta
  2 - em análise
  3 - concluída
Número da situação: Código  Categoria       Local                             Situação    
----------------------------------------------------------------------
008     Iluminação      Praça Central                     aberta      
011     Iluminação      Quadra Poliesportiva              aberta      
014     Iluminação      Praça Central                     aberta      
(3 ocorrência(s))
```

Alteração da 014 para "em análise" (opção 5):

```
Opção: Código da ocorrência: Situação atual: aberta. Nova situação:
  1 - aberta
  2 - em análise
  3 - concluída
Número da situação: Ocorrência 014: aberta -> em análise (registrado no histórico e salvo).
```

Indicadores atualizados (opção 9):

```
========================================================================
INDICADORES DO BAIRRO JARDIM HORIZONTE
========================================================================
Ocorrências válidas: 13   (dia atual da simulação: 16)

Por categoria (proporção = quantidade / total x 100)
  Iluminação        5    38.5%
  Acessibilidade    3    23.1%
  Limpeza           3    23.1%
  Conservação       2    15.4%

Por situação
  aberta            5    38.5%
  em análise        5    38.5%
  concluída         3    23.1%

Matriz categoria x situação
                       aberta  em análise   concluída   total
  Iluminação                2           2           1       5
  Acessibilidade            2           1           0       3
  Limpeza                   0           1           2       3
  Conservação               1           1           0       2

Tempo médio até a conclusão = soma dos dias (conclusão - abertura) / quantidade de concluídas
  dados: 001: 4, 006: 3, 002: 8 dias
  resultado: 15 / 3 = 5.0 dias

Pendências (não concluídas e registradas há mais de 10 dias, ou de acessibilidade): 6
  003, 004, 005, 007, 010, 014

Leitura dos números:
  Iluminação é a categoria com mais registros (38% do total).
  10 de 13 ocorrências ainda não foram resolvidas, e 6 merecem atenção primeiro.
```

Saída do sistema (opção 0):

```
Opção: Encerrando. Cadastros e mudanças de situação já estão salvos em data/.
```

## ♿ Acessibilidade, inclusão e privacidade

- O menu e as escolhas de categoria e situação são numerados: não é preciso digitar palavras com acento nem acertar a grafia.
- Toda recusa diz o motivo em linguagem simples ("campo obrigatório 'categoria' vazio", "a situação avança uma etapa por vez").
- A interface é texto puro, sem depender de cor, o que funciona com leitores de tela e em qualquer terminal.
- A regra de pendência dá prioridade à acessibilidade, porque esses problemas impedem pessoas com deficiência, idosos e quem usa carrinho de bebê de circular pelo bairro.
- Os dados são inventados. Os locais são genéricos ("Praça Central", "Rua 3") e nenhum registro tem nome, telefone, endereço residencial ou qualquer dado pessoal.

## 📁 Estrutura de pastas

- `src/sistema.py`: o programa, com cadastro, consulta, atualização de situação e indicadores.
- `data/dados.csv`: as ocorrências simuladas.
- `data/historico.csv`: os eventos de acompanhamento.
- `data/originais/`: cópia dos dois arquivos no estado inicial, para restaurar.
- `docs/relatorio.pdf`: relatório do projeto.
- `docs/link_video.txt`: link do vídeo de apresentação.
- `assets/`: logo usado neste README.

## 📎 Links e observações

### 🔗 Links do projeto

* **Vídeo de apresentação no YouTube (Não listado):** https://youtu.be/4ACeN502kPY

### 🧠 Decisões técnicas

> Os dados ficam em arquivos de texto separados por `;`, lidos com `open()` e `split()`, sem o módulo `csv`. As mudanças são gravadas na hora, e não só ao sair, para que fechar o terminal no meio não perca nada. O único módulo importado é `os`, usado para achar `data/` a partir do lugar do programa. As datas são números de dia, e não datas reais, para que o tempo de acompanhamento seja uma subtração simples. As mudanças de situação só avançam uma etapa por vez, para que o histórico sempre mostre o caminho completo de cada ocorrência.

### 📢 Observações gerais

* **Participação na competição:** Não vamos participar.

## 🏁 Conclusões, limitações e aprendizados

O sistema cumpre o ciclo completo de uma demanda comunitária: entrada validada, organização em estruturas diferentes conforme o uso, acompanhamento da situação com histórico e um resumo que aponta prioridades.

As limitações são as de uma simulação. Os dados são inventados e as datas são dias numerados. O arquivo de texto não protege contra duas pessoas gravando ao mesmo tempo, o que um banco de dados resolveria. Também não existe conexão com órgãos públicos, e o prazo de 10 dias é uma referência escolhida para o exemplo, não uma norma.

O principal aprendizado foi que cada estrutura de dados responde a uma pergunta diferente sobre os mesmos registros: a lista responde "quais são", o dicionário "qual é esta", a fila "qual é a próxima", a pilha "o que mudou por último" e a matriz "onde se concentram".

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/fiap-tutoria/FIAP-PORTFOLIO-AI">TEMPLATE - FIAP PORTFÓLIO AI</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">FIAP</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
