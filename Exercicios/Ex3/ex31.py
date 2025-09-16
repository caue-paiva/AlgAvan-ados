def stringHoraParaNum(hora):
    h, m = map(int, hora.split(":"))
    return h * 60 + m

def guloso(valores):
    # valores: [(cliente, inicio, fim)]
    aceitos = []
    ultimo_fim = None
    for cliente, inicio, fim in sorted(valores, key=lambda x: (x[2], x[1], x[0])):
        if ultimo_fim is None or inicio >= ultimo_fim:  # [inicio, fim)
            aceitos.append(cliente)
            ultimo_fim = fim
    return aceitos

X = int(input())
for caso in range(X):
    N = int(input())
    M = int(input())

    por_modelo = {i: [] for i in range(1, N + 1)}  # garante todos os modelos

    for _ in range(M):
        cli, ini, fim, mod = input().split()
        por_modelo[int(mod)].append((
            int(cli),
            stringHoraParaNum(ini),
            stringHoraParaNum(fim),
        ))

    partes = []
    for mod in range(1, N + 1):
        selecionados = guloso(por_modelo[mod])
        if selecionados:
            partes.append(f"{mod}: {len(selecionados)} = {', '.join(map(str, selecionados))}")
        else:
            partes.append(f"{mod}: 0")

    linha = " | ".join(partes)
    print(linha, end="" if caso == X - 1 else "\n")
