from collections import defaultdict

# árvore de Fenwik
class FenTree:
    def __init__(self, n):
        self.n = n
        self.bit = [0]*(n+1)
    def add(self, i, v=1):
        while i <= self.n:
            self.bit[i] += v
            i += i & -i
    def sum_prefix(self, i):
        s = 0
        while i > 0:
            s += self.bit[i]
            i -= i & -i
        return s

N = int(input())
#maior tamanho da arvore de fenwik, igual à 10ˆ8 
MAXSIZE =  1_00_000_000

#tupla para resultado final
results = []

for i_iter in range(N):
    M = int(input())

    posi = []
    #vamos agrupar num dict todos os carros que acabaram numa mesma posição
    groups = defaultdict(list)
    for _ in range(M):
        i,j = input().split(" ")
        i,j = int(i),int(j)

        groups[j].append((i))

    tree = FenTree(MAXSIZE)
    ans = 0
    
    #numero de carros anteriores processados
    totalCarsProcessed = 0

    #loop pelas posições final em ordem crescente
    for end in sorted(groups.keys()):
        # carros que acabaram na mesma posição
        startGroup = groups[end]
        groupSize = len(startGroup)

        #adicionar ultrapassagens em caso de empate na posição final
        ans +=  groupSize*(groupSize-1)//2

        for start in startGroup:
            #vamos ver quantos carros começaram antes da gnt
            startedBefore = tree.sum_prefix(start+1) 
            
            # mas queremos o número de carros que começaram depois da gnt, então é o total - {num. começaram antes}
            startedAfter = totalCarsProcessed - startedBefore            
            ans += startedAfter
        
        #add os carros que terminaram antes na árvore 
        for start in startGroup:
             tree.add(start+1)
        
        #processamos mais carros (equivale ao tam do grupo)
        totalCarsProcessed += groupSize
    
    results.append((i_iter,ans))

# ordenar os resultados para maximizar as ultrapassagems
results.sort(key=lambda x: x[1],reverse=True)

for index,result in results:
    print(index,result)
