def stringHoraParaNum(hora):
    hora,min = hora.split(":")
    return (int(hora) * 60) + int(min)

def guloso(carro,valores):

    valores.sort(key=lambda x : x[2]) #ordena pelo fim

N = int(input())

for _ in range(N):
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
    

    for carro,valores in dictCarrors.items():
        pass