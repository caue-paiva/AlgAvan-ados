from collections import defaultdict, deque
from operator import add

# Produtividade dos níveis
PRODUCTIVITY = {
    "Aprendiz": 0.75,
    "Aventureiro": 1.0,
    "Cavaleiro": 1.2,
    "Mestre": 1.5,
    "Lenda": 2.0
}

def final_output(total_time,heroes,add_newline):
    for h in heroes:
            if h["quests"]:
                print(f"{h['name']} = {{{','.join(map(str, h['quests']))}}}")
            else:
                print(f"{h['name']} = {{}}")
    if add_newline:
        print(f"Tempo mínimo: {total_time:.2f}\n")
    else:
        print(f"Tempo mínimo: {total_time:.2f}")


def solve():
    X = int(input().strip())  # número de casos de teste

    iter = 0 
    for _ in range(X):
        # Lê N (heróis) e M (quests)
        N, M = map(int, input().split())
        iter += 1

        # Lê heróis
        heroes = []
        for _ in range(N):
            name, level = input().split()
            heroes.append({
                "name": name,
                "prod": PRODUCTIVITY[level],
                "time_free": 0.0,
                "quests": []
            })

        # Estruturas para quests
        quests = {}
        indegree = [0] * (M + 1)
        graph = defaultdict(list)

        for _ in range(M):
            data = list(map(int, input().split()))
            idx, base_time, *deps = data
            if deps[0] == 0:
                deps = []
            quests[idx] = {"time": base_time, "deps": deps}
            for d in deps:
                graph[d].append(idx)
            indegree[idx] = len(deps)

        # Ordenação topológica (Kahn)
        q = deque()
        for i in range(1, M + 1):
            if indegree[i] == 0:
                q.append(i)

        completed_time = [0.0] * (M + 1)  # momento de conclusão de cada quest
        total_time = 0.0

        while q:
            quest = q.popleft()
            base_time = quests[quest]["time"]

            # escolher herói ótimo
            best_hero = None
            best_finish = float("inf")

            for h in heroes:
                # max entre o tempo que um heroi está livre e o maior tempo que uma dependencia da quest atual vai ter
                start_time = max(h["time_free"], max([completed_time[d] for d in quests[quest]["deps"]] or [0]))
                finish_time = start_time + (base_time / h["prod"])

                # or para edge case:
                # "Se dois ou mais heróis puderem terminar uma quest no mesmo tempo, escolha o herói que aparece primeiro na lista de entrada."
                # usamos o abs por causa  que o tempo pode ser um float e podemos ter erros de arrendondamento que uma == n poderia pegar
                if finish_time < best_finish or (abs(finish_time - best_finish) < 1e-9 and best_hero is None):
                    best_finish = finish_time
                    best_hero = h

            # atribui quest
            best_hero["quests"].append(quest)
            best_hero["time_free"] = best_finish
            completed_time[quest] = best_finish
            total_time = max(total_time, best_finish)

            # libera dependentes reduzindo o grau de entrada de cada dependencia
            for nxt in graph[quest]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    q.append(nxt)

        # saída formatada
        if iter < X:
            final_output(total_time,heroes,True)
        else:
            final_output(total_time,heroes,False)

            

solve()