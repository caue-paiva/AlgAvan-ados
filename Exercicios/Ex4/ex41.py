import sys
import heapq
from collections import defaultdict

EPS = 1e-9

LEVEL_PRODUCTIVITY = {
    "Aprendiz": 0.75,
    "Aventureiro": 1.0,
    "Cavaleiro": 1.2,
    "Mestre": 1.5,
    "Lenda": 2.0,
}

def solve_case():
    N, M = map(int, sys.stdin.readline().split())

    # Heróis
    heroes = []
    prod = []
    for _ in range(N):
        name, level = sys.stdin.readline().split()
        heroes.append(name)
        prod.append(LEVEL_PRODUCTIVITY[level])

    # Quests e grafo
    quests = {}                       # q -> (T, deps)
    succ = defaultdict(list)          # u -> [v]
    indeg = {}                        # q -> grau de entrada
    q_ids = []

    for _ in range(M):
        parts = list(map(int, sys.stdin.readline().split()))
        q, T = parts[0], parts[1]
        deps = parts[2:]
        if len(deps) == 1 and deps[0] == 0:
            deps = []
        quests[q] = (T, deps)
        q_ids.append(q)
        indeg[q] = len(deps)
        for d in deps:
            succ[d].append(q)

    # Grau de saída (para prioridade)
    outdeg = {q: 0 for q in q_ids}
    for u in succ:
        for v in succ[u]:
            outdeg[u] += 1

    # Heap de tarefas prontas:
    #   (-outdeg, ready_ts, T, q)
    ready = []
    for q in q_ids:
        if indeg[q] == 0:
            Tq = quests[q][0]
            heapq.heappush(ready, (-outdeg[q], 0.0, Tq, q))

    # Heróis: tempo em que ficam livres
    hero_free_at = [0.0] * N

    # Execuções em andamento: (t_finish, h, q)
    running = []

    # Resultado
    assign = [[] for _ in range(N)]
    q_finish = {}
    t = 0.0

    def best_wait_eft(q, p_now):
        """Melhor EFT para 'q' esperando algum herói ocupado mais rápido que p_now."""
        Tq = quests[q][0]
        best = float('inf')
        for t_av, h_occ, _ in running:
            if prod[h_occ] > p_now + EPS:
                eft = t_av + Tq / prod[h_occ]
                if eft < best:
                    best = eft
        return best

    # Fallback para evitar deadlock (todos recusam e nada está rodando)
    def force_assign_when_stalled():
        if running or not ready:
            return False
        # pegar o herói mais rápido e a tarefa de topo
        h = max(range(N), key=lambda x: prod[x])
        neg_od, tsr, Tq, q = heapq.heappop(ready)
        t_fin = t + Tq / prod[h]
        hero_free_at[h] = t_fin
        heapq.heappush(running, (t_fin, h, q))
        assign[h].append(q)
        return True

    while ready or running:
        # === Fase de atribuição no tempo atual t ===
        # Se não há nada rodando, t é 0 e todos heróis estão livres: tentamos atribuir agora.
        # Em tempos subsequentes, essa fase também roda antes de processar novos términos,
        # porque pode haver heróis ociosos com hero_free_at <= t.
        any_assigned = False
        deferred_all = []  # devolvemos ao final do evento

        # Heróis livres no tempo t (inclui quem já estava ocioso)
        free_now = [h for h in range(N) if hero_free_at[h] <= t + EPS]
        free_now.sort(key=lambda h: prod[h], reverse=True)

        for h in free_now:
            if not ready:
                continue
            p_now = prod[h]
            picked = None
            buf = []

            # varre o ready (sem reservar) até achar algo que "valha agora"
            while ready:
                neg_od, tsr, Tq, q = heapq.heappop(ready)
                finish_now = t + Tq / p_now
                wait_eft = best_wait_eft(q, p_now)
                if wait_eft + EPS < finish_now:
                    # melhor esperar alguém mais rápido: adia
                    buf.append((neg_od, tsr, Tq, q))
                    continue
                else:
                    picked = (neg_od, tsr, Tq, q)
                    break

            # devolve as adiadas (no fim do evento, para que outro herói não pegue no mesmo instante)
            for item in buf:
                deferred_all.append(item)

            if picked is None:
                continue

            neg_od, tsr, Tq, q = picked
            t_fin = t + Tq / p_now
            hero_free_at[h] = t_fin
            heapq.heappush(running, (t_fin, h, q))
            assign[h].append(q)
            any_assigned = True

        # devolve as tarefas adiadas ao ready
        for item in deferred_all:
            heapq.heappush(ready, item)

        # Se nada foi atribuído e também nada está em execução, force uma atribuição para avançar o tempo
        if not any_assigned and not running:
            forced = force_assign_when_stalled()
            if not forced:
                break  # nada a fazer

        # === Se não há execuções, terminou ===
        if not running:
            break

        # === Avança para o próximo término e faz batching ===
        t_next, h_fin, q_fin = heapq.heappop(running)
        t = t_next
        batch = [(h_fin, q_fin)]
        while running and abs(running[0][0] - t) <= EPS:
            _, h2, q2 = heapq.heappop(running)
            batch.append((h2, q2))

        # Marca conclusões e libera sucessores
        for h_done, q_done in batch:
            hero_free_at[h_done] = t
            q_finish[q_done] = t
            for s in succ[q_done]:
                indeg[s] -= 1
                if indeg[s] == 0:
                    Ts = quests[s][0]
                    heapq.heappush(ready, (-outdeg[s], t, Ts, s))

        # Loop continua, podendo haver nova fase de atribuição em t (com heróis da batch + ociosos)

    # Saída
    for h in range(N):
        tasks_sorted = sorted(assign[h])  # por id asc
        print(f"{heroes[h]} = " + "{" + ",".join(map(str, tasks_sorted)) + "}")
    makespan = max(q_finish.values()) if q_finish else 0.0
    print(f"Tempo mínimo: {makespan:.2f}")

if __name__ == "__main__":
    X = int(sys.stdin.readline())
    for case in range(X):
        solve_case()
        if case < X - 1:
            print()
