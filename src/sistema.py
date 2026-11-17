# =====================================================================
# Neighborhood Action Dashboard - painel comunitário de ocorrências
# Global Solution 2026.2 - Ciência da Computação FIAP
# Gabriel Tancler Armada - RM 574883
#
# Lê as ocorrências e o histórico da pasta data/, organiza os registros
# em lista, dicionário, fila, pilha, hierarquia e matriz, aplica as
# regras de validação, consulta e atualização e mostra os indicadores
# do bairro simulado Jardim Horizonte. Cadastros e mudanças de situação
# são gravados na hora nos arquivos de data/.
#
# Como rodar:  python src/sistema.py   (funciona a partir de qualquer pasta)
# Para voltar aos dados iniciais, copie data/originais/*.csv para data/.
# Só Python básico, versão 3.8 ou mais recente.
# =====================================================================


import os

# ---------------------------------------------------------------------
# 1. CONFIGURAÇÃO
# ---------------------------------------------------------------------
BAIRRO = "Jardim Horizonte"
DIA_ATUAL = 16          # "hoje" na simulação
PRAZO_DIAS = 10         # ocorrência não concluída há mais tempo que isso vira pendência

# Os arquivos são achados a partir do lugar deste programa (src/ fica dentro da
# pasta do projeto), e não da pasta em que o terminal está aberto
PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_OCORRENCIAS = os.path.join(PASTA_PROJETO, "data", "dados.csv")
ARQUIVO_HISTORICO = os.path.join(PASTA_PROJETO, "data", "historico.csv")

# Valores padronizados: a lista guarda o que fica no arquivo, na ordem de exibição;
# o dicionário traduz para o texto mostrado na tela
LISTA_CATEGORIAS = ["iluminacao", "acessibilidade", "limpeza", "conservacao"]
CATEGORIAS = {"iluminacao": "Iluminação",
              "acessibilidade": "Acessibilidade",
              "limpeza": "Limpeza",
              "conservacao": "Conservação"}

LISTA_STATUS = ["aberta", "em_analise", "concluida"]      # ordem obrigatória das etapas
STATUS = {"aberta": "aberta",
          "em_analise": "em análise",
          "concluida": "concluída"}
SIGNIFICADO = {"aberta": "registrada e ainda não examinada",
               "em_analise": "examinada, aguardando solução",
               "concluida": "problema resolvido"}

CAMPOS_OBRIGATORIOS = ["codigo", "categoria", "descricao", "local", "dia_abertura", "status"]


# ---------------------------------------------------------------------
# 2. LEITURA DOS ARQUIVOS E VALIDAÇÃO
# ---------------------------------------------------------------------
def ler_arquivo(caminho):
    """Lê um arquivo de texto separado por ';' e devolve uma lista de
    dicionários, usando a primeira linha (cabeçalho) como chaves."""
    linhas = []
    with open(caminho, encoding="utf-8") as arquivo:
        for linha in arquivo:
            if linha.strip() != "":
                linhas.append(linha.strip())

    campos = linhas[0].split(";")
    registros = []
    for numero in range(1, len(linhas)):
        valores = linhas[numero].split(";")
        registro = {}
        for i in range(len(campos)):
            if i < len(valores):
                registro[campos[i]] = valores[i].strip()
            else:
                registro[campos[i]] = ""
        registros.append(registro)
    return registros


def validar_ocorrencia(registro, codigos_usados):
    """Devolve "" se o registro pode entrar no sistema, ou o motivo da recusa."""
    for campo in CAMPOS_OBRIGATORIOS:
        if registro[campo] == "":
            return f"campo obrigatório '{campo}' vazio"

    codigo = registro["codigo"]
    dia = registro["dia_abertura"]
    if not (codigo.isdigit() and len(codigo) == 3):
        return "código deve ter 3 dígitos, como 014"
    elif codigo in codigos_usados:
        return "código já cadastrado"
    elif registro["categoria"] not in CATEGORIAS:
        return "categoria desconhecida"
    elif ";" in registro["descricao"] or ";" in registro["local"]:
        return "descrição e local não podem ter ';', que separa os campos no arquivo"
    elif registro["status"] not in STATUS:
        return "situação desconhecida"
    elif not (dia.isdigit() and 1 <= int(dia) <= DIA_ATUAL):
        return f"dia de abertura deve estar entre 1 e {DIA_ATUAL}"
    else:
        return ""


def acrescentar_linha(caminho, linha):
    """Grava uma linha nova no fim do arquivo, sem mexer nas que já existem."""
    with open(caminho, encoding="utf-8") as arquivo:
        conteudo = arquivo.read()
    if conteudo != "" and not conteudo.endswith("\n"):
        linha = "\n" + linha
    with open(caminho, "a", encoding="utf-8", newline="") as arquivo:
        arquivo.write(linha + "\n")


def gravar_situacao(codigo, novo):
    """Reescreve o arquivo de ocorrências trocando só a situação da linha do
    código indicado. As outras linhas, inclusive as recusadas na leitura,
    continuam exatamente como estavam."""
    linhas = []
    with open(ARQUIVO_OCORRENCIAS, encoding="utf-8") as arquivo:
        for linha in arquivo:
            linhas.append(linha.rstrip("\n").rstrip("\r"))

    campos = linhas[0].split(";")
    coluna = posicao(campos, "status")
    texto = ""
    trocou = False
    for linha in linhas:
        valores = linha.split(";")
        if not trocou and valores[0].strip() == codigo and coluna < len(valores):
            trocou = True
            valores[coluna] = novo
            linha = ""
            for i in range(len(valores)):
                if i > 0:
                    linha = linha + ";"
                linha = linha + valores[i]
        texto = texto + linha + "\n"

    with open(ARQUIVO_OCORRENCIAS, "w", encoding="utf-8", newline="") as arquivo:
        arquivo.write(texto)


# ---------------------------------------------------------------------
# 3. ESTRUTURAS DE DADOS
# ---------------------------------------------------------------------
# Fila: entra no fim, sai do começo (a demanda registrada primeiro é examinada primeiro)
def enfileirar(fila, item):
    fila.append(item)


def desenfileirar(fila):
    return fila.pop(0)


# Pilha: entra e sai pelo topo (o evento mais recente fica por cima)
def empilhar(pilha, item):
    pilha.append(item)


def topo(pilha, quantidade):
    """Devolve os últimos itens empilhados, do mais recente para o mais antigo,
    sem tirá-los da pilha."""
    recentes = []
    i = len(pilha) - 1
    while i >= 0 and len(recentes) < quantidade:
        recentes.append(pilha[i])
        i = i - 1
    return recentes


def posicao(lista, valor):
    """Busca linear: devolve a posição de valor na lista, ou -1 se não estiver."""
    for i in range(len(lista)):
        if lista[i] == valor:
            return i
    return -1


def adicionar(base, registro):
    """Coloca uma ocorrência já validada em todas as estruturas."""
    registro["dia_abertura"] = int(registro["dia_abertura"])
    base["lista"].append(registro)
    base["por_codigo"][registro["codigo"]] = registro
    if registro["status"] == "aberta":
        enfileirar(base["fila"], registro["codigo"])


def criar_evento(codigo, dia, anterior, novo):
    return {"codigo": codigo, "dia": dia, "anterior": anterior, "novo": novo}


def registrar_mudanca(base, ocorrencia, novo):
    """Muda a situação na memória, empilha o evento e grava os dois arquivos."""
    anterior = ocorrencia["status"]
    ocorrencia["status"] = novo
    empilhar(base["pilha"], criar_evento(ocorrencia["codigo"], DIA_ATUAL, anterior, novo))
    gravar_situacao(ocorrencia["codigo"], novo)
    acrescentar_linha(ARQUIVO_HISTORICO, f"{ocorrencia['codigo']};{DIA_ATUAL};{anterior};{novo}")
    return anterior


def carregar():
    """Lê os dois arquivos de data/ e monta as estruturas do sistema."""
    base = {
        "lista": [],        # lista: todas as ocorrências válidas, na ordem de registro
        "por_codigo": {},   # dicionário: código -> ocorrência (acesso direto)
        "fila": [],         # fila: códigos das ocorrências abertas, por ordem de registro
        "pilha": [],        # pilha: eventos de mudança de situação
        "reservados": [],   # códigos que já aparecem no arquivo, mesmo recusados
        "recusados": [],    # registros inválidos, com o motivo
    }
    for registro in ler_arquivo(ARQUIVO_OCORRENCIAS):
        motivo = validar_ocorrencia(registro, base["reservados"])
        if registro["codigo"] != "" and registro["codigo"] not in base["reservados"]:
            base["reservados"].append(registro["codigo"])
        if motivo == "":
            adicionar(base, registro)
        else:
            base["recusados"].append({"codigo": registro["codigo"], "motivo": motivo})

    for evento in ler_arquivo(ARQUIVO_HISTORICO):
        if evento["codigo"] in base["por_codigo"] and evento["status_anterior"] in STATUS \
                and evento["status_novo"] in STATUS:
            empilhar(base["pilha"], criar_evento(evento["codigo"], int(evento["dia"]),
                                                 evento["status_anterior"], evento["status_novo"]))
    return base


def montar_hierarquia(lista):
    """Hierarquia bairro -> categoria -> códigos das ocorrências."""
    hierarquia = {BAIRRO: {}}
    for categoria in LISTA_CATEGORIAS:
        hierarquia[BAIRRO][categoria] = []
    for ocorrencia in lista:
        hierarquia[BAIRRO][ocorrencia["categoria"]].append(ocorrencia["codigo"])
    return hierarquia


def montar_matriz(lista):
    """Matriz categoria x situação: matriz[i][j] = quantidade de ocorrências da
    categoria i (ordem de LISTA_CATEGORIAS) na situação j (ordem de LISTA_STATUS)."""
    matriz = []
    for i in range(len(LISTA_CATEGORIAS)):
        linha = []
        for j in range(len(LISTA_STATUS)):
            linha.append(0)
        matriz.append(linha)
    for ocorrencia in lista:
        i = posicao(LISTA_CATEGORIAS, ocorrencia["categoria"])
        j = posicao(LISTA_STATUS, ocorrencia["status"])
        matriz[i][j] = matriz[i][j] + 1
    return matriz


# ---------------------------------------------------------------------
# 4. CONSULTAS E REGRAS
# ---------------------------------------------------------------------
def filtrar(lista, categoria, status):
    """Texto vazio em categoria ou status significa "qualquer"."""
    resultado = []
    for ocorrencia in lista:
        if (categoria == "" or ocorrencia["categoria"] == categoria) and \
           (status == "" or ocorrencia["status"] == status):
            resultado.append(ocorrencia)
    return resultado


def pendente(ocorrencia):
    """Não concluída e (registrada há mais que o prazo ou de acessibilidade)."""
    dias_aberta = DIA_ATUAL - ocorrencia["dia_abertura"]
    return not ocorrencia["status"] == "concluida" and \
        (dias_aberta > PRAZO_DIAS or ocorrencia["categoria"] == "acessibilidade")


def validar_mudanca(atual, novo):
    """Devolve "" se a situação pode mudar de atual para novo, ou o motivo da recusa."""
    if not (novo in STATUS and novo != atual and not atual == "concluida"):
        if novo not in STATUS:
            return "situação desconhecida"
        elif novo == atual:
            return f"a ocorrência já está {STATUS[atual]}"
        else:
            return "ocorrência concluída não muda mais de situação"
    elif posicao(LISTA_STATUS, novo) != posicao(LISTA_STATUS, atual) + 1:
        return "a situação avança uma etapa por vez: aberta -> em análise -> concluída"
    else:
        return ""


def atualizar_status(base, codigo, novo):
    """Muda a situação de uma ocorrência e registra o evento na pilha."""
    if codigo not in base["por_codigo"]:
        return f"Ocorrência {codigo} não encontrada."
    ocorrencia = base["por_codigo"][codigo]
    motivo = validar_mudanca(ocorrencia["status"], novo)
    if motivo != "":
        return f"Atualização recusada: {motivo}."
    anterior = registrar_mudanca(base, ocorrencia, novo)
    return f"Ocorrência {codigo}: {STATUS[anterior]} -> {STATUS[novo]} (registrado no histórico e salvo)."


def examinar_proxima(base):
    """Tira da fila a demanda aberta mais antiga e passa para "em análise".
    Códigos que já mudaram de situação por outro caminho são descartados."""
    while len(base["fila"]) > 0:
        codigo = desenfileirar(base["fila"])
        ocorrencia = base["por_codigo"][codigo]
        if ocorrencia["status"] == "aberta":
            registrar_mudanca(base, ocorrencia, "em_analise")
            return f"Examinada a ocorrência {codigo} ({ocorrencia['descricao']}): agora está em análise."
    return "Não há demandas abertas na fila."


def demandas_na_fila(base):
    """Quantas ocorrências da fila ainda estão abertas."""
    total = 0
    for codigo in base["fila"]:
        if base["por_codigo"][codigo]["status"] == "aberta":
            total = total + 1
    return total


def proximo_codigo(base):
    maior = 0
    for codigo in base["reservados"]:
        if codigo.isdigit() and int(codigo) > maior:
            maior = int(codigo)
    return f"{maior + 1:03d}"


def cadastrar(base, codigo, categoria, descricao, local, dia):
    """Valida e cadastra uma nova ocorrência, sempre com situação "aberta"."""
    registro = {"codigo": codigo, "categoria": categoria, "descricao": descricao,
                "local": local, "dia_abertura": dia, "status": "aberta"}
    motivo = validar_ocorrencia(registro, base["reservados"])
    if motivo != "":
        return f"Cadastro recusado: {motivo}."
    linha = ""
    for campo in CAMPOS_OBRIGATORIOS:
        if linha != "":
            linha = linha + ";"
        linha = linha + registro[campo]
    acrescentar_linha(ARQUIVO_OCORRENCIAS, linha)
    base["reservados"].append(codigo)
    adicionar(base, registro)
    return f"Ocorrência {codigo} cadastrada como aberta, salva e colocada no fim da fila."


# ---------------------------------------------------------------------
# 5. INDICADORES
# ---------------------------------------------------------------------
def contar(lista, campo, chaves):
    """Conta quantas ocorrências têm cada valor de campo."""
    totais = {}
    for chave in chaves:
        totais[chave] = 0
    for ocorrencia in lista:
        totais[ocorrencia[campo]] = totais[ocorrencia[campo]] + 1
    return totais


def tempos_de_conclusao(base):
    """Para cada evento de conclusão: dias entre a abertura e a conclusão."""
    tempos = []
    for evento in base["pilha"]:
        if evento["novo"] == "concluida":
            abertura = base["por_codigo"][evento["codigo"]]["dia_abertura"]
            tempos.append({"codigo": evento["codigo"], "dias": evento["dia"] - abertura})
    return tempos


def mostrar_indicadores(base):
    lista = base["lista"]
    total = len(lista)
    if total == 0:
        print("Nenhuma ocorrência cadastrada.")
        return
    titulo("INDICADORES DO BAIRRO " + BAIRRO.upper())
    print(f"Ocorrências válidas: {total}   (dia atual da simulação: {DIA_ATUAL})\n")

    por_categoria = contar(lista, "categoria", LISTA_CATEGORIAS)
    print("Por categoria (proporção = quantidade / total x 100)")
    for chave in LISTA_CATEGORIAS:
        print(f"  {CATEGORIAS[chave]:<15} {por_categoria[chave]:>3}   {por_categoria[chave] / total * 100:5.1f}%")

    por_status = contar(lista, "status", LISTA_STATUS)
    print("\nPor situação")
    for chave in LISTA_STATUS:
        print(f"  {STATUS[chave]:<15} {por_status[chave]:>3}   {por_status[chave] / total * 100:5.1f}%")

    print("\nMatriz categoria x situação")
    matriz = montar_matriz(lista)
    cabecalho = f"  {'':<15}"
    for chave in LISTA_STATUS:
        cabecalho = cabecalho + f"{STATUS[chave]:>12}"
    print(cabecalho + f"{'total':>8}")
    for i in range(len(LISTA_CATEGORIAS)):
        texto = f"  {CATEGORIAS[LISTA_CATEGORIAS[i]]:<15}"
        soma_linha = 0
        for j in range(len(LISTA_STATUS)):
            texto = texto + f"{matriz[i][j]:>12}"
            soma_linha = soma_linha + matriz[i][j]
        print(texto + f"{soma_linha:>8}")

    tempos = tempos_de_conclusao(base)
    print("\nTempo médio até a conclusão = soma dos dias (conclusão - abertura) / quantidade de concluídas")
    if len(tempos) > 0:
        soma = 0
        dados = ""
        for item in tempos:
            soma = soma + item["dias"]
            if dados != "":
                dados = dados + ", "
            dados = dados + f"{item['codigo']}: {item['dias']}"
        print(f"  dados: {dados} dias")
        print(f"  resultado: {soma} / {len(tempos)} = {soma / len(tempos):.1f} dias")
    else:
        print("  nenhuma ocorrência concluída ainda")

    pendentes = ""
    quantidade_pendentes = 0
    for ocorrencia in lista:
        if pendente(ocorrencia):
            if pendentes != "":
                pendentes = pendentes + ", "
            pendentes = pendentes + ocorrencia["codigo"]
            quantidade_pendentes = quantidade_pendentes + 1
    print(f"\nPendências (não concluídas e registradas há mais de {PRAZO_DIAS} dias, ou de acessibilidade): "
          f"{quantidade_pendentes}")
    if quantidade_pendentes > 0:
        print("  " + pendentes)

    # conclusão curta a partir dos números
    maior = LISTA_CATEGORIAS[0]
    for chave in LISTA_CATEGORIAS:
        if por_categoria[chave] > por_categoria[maior]:
            maior = chave
    nao_concluidas = total - por_status["concluida"]
    print("\nLeitura dos números:")
    print(f"  {CATEGORIAS[maior]} é a categoria com mais registros "
          f"({por_categoria[maior] / total * 100:.0f}% do total).")
    print(f"  {nao_concluidas} de {total} ocorrências ainda não foram resolvidas, "
          f"e {quantidade_pendentes} merecem atenção primeiro.")


# ---------------------------------------------------------------------
# 6. INTERFACE NO TERMINAL
# ---------------------------------------------------------------------
def titulo(texto):
    print("\n" + "=" * 72)
    print(texto)
    print("=" * 72)


def escolher(chaves, nomes, mensagem):
    """Mostra opções numeradas e devolve a chave escolhida,
    "" se o usuário só apertar Enter ou "invalida" se o número não existir."""
    for i in range(len(chaves)):
        print(f"  {i + 1} - {nomes[chaves[i]]}")
    resposta = input(mensagem).strip()
    if resposta == "":
        return ""
    elif resposta.isdigit() and 1 <= int(resposta) <= len(chaves):
        return chaves[int(resposta) - 1]
    else:
        return "invalida"


def mostrar_tabela(lista):
    if len(lista) == 0:
        print("Nenhuma ocorrência encontrada com esses critérios.")
        return
    print(f"{'Código':<8}{'Categoria':<16}{'Local':<34}{'Situação':<12}")
    print("-" * 70)
    for o in lista:
        print(f"{o['codigo']:<8}{CATEGORIAS[o['categoria']]:<16}{o['local']:<34}{STATUS[o['status']]:<12}")
    print(f"({len(lista)} ocorrência(s))")


def mostrar_ocorrencia(o):
    print(f"Código:     {o['codigo']}")
    print(f"Categoria:  {CATEGORIAS[o['categoria']]}")
    print(f"Descrição:  {o['descricao']}")
    print(f"Local:      {o['local']}")
    print(f"Abertura:   dia {o['dia_abertura']} ({DIA_ATUAL - o['dia_abertura']} dias atrás)")
    print(f"Situação:   {STATUS[o['status']]} - {SIGNIFICADO[o['status']]}")
    if pendente(o):
        print("Pendência:  sim")
    else:
        print("Pendência:  não")


def opcao_cadastrar(base):
    titulo("CADASTRAR OCORRÊNCIA")
    sugerido = proximo_codigo(base)
    codigo = input(f"Código (Enter para usar {sugerido}): ").strip()
    if codigo == "":
        codigo = sugerido
    print("Categoria:")
    categoria = escolher(LISTA_CATEGORIAS, CATEGORIAS, "Número da categoria: ")
    if categoria == "" or categoria == "invalida":
        print(f"Cadastro recusado: escolha uma categoria de 1 a {len(LISTA_CATEGORIAS)}.")
        return
    descricao = input("Descrição breve: ").strip()
    local = input("Local genérico (ex.: Praça Central): ").strip()
    dia = input(f"Dia de abertura (1 a {DIA_ATUAL}): ").strip()
    print(cadastrar(base, codigo, categoria, descricao, local, dia))


def opcao_buscar(base):
    codigo = input("Código da ocorrência: ").strip()
    if codigo in base["por_codigo"]:
        mostrar_ocorrencia(base["por_codigo"][codigo])
    else:
        print(f"Ocorrência {codigo} não encontrada.")


def opcao_filtrar(base):
    print("Categoria (Enter = qualquer):")
    categoria = escolher(LISTA_CATEGORIAS, CATEGORIAS, "Número da categoria: ")
    print("Situação (Enter = qualquer):")
    status = escolher(LISTA_STATUS, STATUS, "Número da situação: ")
    if categoria == "invalida" or status == "invalida":
        print("Opção inválida: use um dos números da lista ou Enter.")
    else:
        mostrar_tabela(filtrar(base["lista"], categoria, status))


def opcao_atualizar(base):
    codigo = input("Código da ocorrência: ").strip()
    if codigo not in base["por_codigo"]:
        print(f"Ocorrência {codigo} não encontrada.")
        return
    print(f"Situação atual: {STATUS[base['por_codigo'][codigo]['status']]}. Nova situação:")
    novo = escolher(LISTA_STATUS, STATUS, "Número da situação: ")
    print(atualizar_status(base, codigo, novo))


def opcao_eventos(base):
    titulo("ÚLTIMAS ATUALIZAÇÕES (topo da pilha primeiro)")
    for evento in topo(base["pilha"], 5):
        print(f"  dia {evento['dia']:>2}  {evento['codigo']}  "
              f"{STATUS[evento['anterior']]} -> {STATUS[evento['novo']]}")
    print(f"({len(base['pilha'])} eventos no histórico)")


def opcao_hierarquia(base):
    titulo("HIERARQUIA BAIRRO -> CATEGORIA -> OCORRÊNCIAS")
    hierarquia = montar_hierarquia(base["lista"])
    for bairro in hierarquia:
        print(bairro)
        for categoria in hierarquia[bairro]:
            codigos = hierarquia[bairro][categoria]
            texto = ""
            for codigo in codigos:
                if texto != "":
                    texto = texto + ", "
                texto = texto + codigo
            print(f"  {CATEGORIAS[categoria]} ({len(codigos)}): {texto}")


def menu(base):
    opcao = ""
    while opcao != "0":
        print("\nMENU")
        print("  1 - Listar ocorrências")
        print("  2 - Cadastrar ocorrência")
        print("  3 - Buscar por código")
        print("  4 - Filtrar por categoria e situação")
        print("  5 - Atualizar situação")
        print("  6 - Examinar a próxima demanda da fila")
        print("  7 - Ver últimas atualizações")
        print("  8 - Ver hierarquia do bairro")
        print("  9 - Ver indicadores")
        print("  0 - Sair")
        opcao = input("Opção: ").strip()
        if opcao == "1":
            titulo("OCORRÊNCIAS")
            mostrar_tabela(base["lista"])
        elif opcao == "2":
            opcao_cadastrar(base)
        elif opcao == "3":
            opcao_buscar(base)
        elif opcao == "4":
            opcao_filtrar(base)
        elif opcao == "5":
            opcao_atualizar(base)
        elif opcao == "6":
            print(examinar_proxima(base))
        elif opcao == "7":
            opcao_eventos(base)
        elif opcao == "8":
            opcao_hierarquia(base)
        elif opcao == "9":
            mostrar_indicadores(base)
        elif opcao == "0":
            print("Encerrando. Cadastros e mudanças de situação já estão salvos em data/.")
        else:
            print("Opção inválida: digite um número de 0 a 9.")


# ---------------------------------------------------------------------
# 7. PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------
def main():
    base = carregar()
    titulo(f"NEIGHBORHOOD ACTION DASHBOARD - {BAIRRO} (simulação)")
    print(f"{len(base['lista'])} ocorrências carregadas, {len(base['pilha'])} eventos de histórico, "
          f"{demandas_na_fila(base)} demandas abertas na fila.")
    for recusado in base["recusados"]:
        print(f"Registro {recusado['codigo']} recusado na leitura: {recusado['motivo']}.")
    print("Situações:")
    for chave in LISTA_STATUS:
        print(f"  {STATUS[chave]} = {SIGNIFICADO[chave]}")
    menu(base)


if __name__ == "__main__":
    main()
