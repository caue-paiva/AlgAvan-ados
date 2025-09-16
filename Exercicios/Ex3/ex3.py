def stringHoraParaNum(hora):
    hora,min = hora.split(":")
    return (int(hora) * 60) + int(min)

def guloso(valores):
    lista_clientes = []
    valores.sort(key=lambda x : x[2]) #ordena pelo fim
    fimAntigo = None
    selecionados = []  # Store (cliente, comeco, fim) tuples
    for cliente,comeco,fim in valores:        
        if fimAntigo is None or fimAntigo <= comeco:
            fimAntigo = fim
            selecionados.append((cliente, comeco, fim))
    
    # Sort selected clients by start time (chronological order)
    selecionados.sort(key=lambda x: x[1])
    lista_clientes = [cliente for cliente, _, _ in selecionados]
    
    return lista_clientes
            

N = int(input())

for test_case in range(N):
    nCarros = int(input())
    m = int(input())

    dictCarrors = {}

    for _ in range(m):
        linha = input().split(" ")
        cliente,comeco,fim,carro = int(linha[0]), \
        stringHoraParaNum(linha[1]), \
        stringHoraParaNum(linha[2]), \
        int(linha[3]) \

        if carro not in dictCarrors:
            dictCarrors[carro] = [(cliente,comeco,fim)]
        else:
            dictCarrors[carro].append((cliente,comeco,fim))
    

    saidas = []
    for carro in range(1, nCarros + 1):
        if carro in dictCarrors:
            listaAluguel = guloso(dictCarrors[carro])
            if len(listaAluguel) > 0:
                saidas.append(f"{carro}: {len(listaAluguel)} = {', '.join(map(str, listaAluguel))}")
            else:
                saidas.append(f"{carro}: 0")
        else:
            saidas.append(f"{carro}: 0")

    final = " | ".join(saidas)
    print(final, end="" if test_case == N - 1 else "\n")
