import sys
import heapq
from collections import defaultdict, deque

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

    # heróis
    heroes, prod = [], []
    for _ in range(N):
        name, level = sys.stdin.readline().split()
        heroes.append(name)
        prod.append(LEVEL_PRODUCTIVITY[level])

    # quests e grafo
    quests = {}                      # q -> (T, deps)
    deps = defaultdict(list)
    succ = defaultdict(list)
    indeg = {}
    q_ids = []

    for _ in range(M):
        parts = list(map(int, sys.stdin.readline().split()))
        q, T = parts[0], parts[1]
        ds = parts[2:]
        if len(ds) == 1 and ds[0] == 0:
            ds = []
        quests[q] = (T, ds)
        q_ids.append(q)
        deps[q] = ds
        indeg[q] = len(ds)
        for d in ds:
            succ[d].append(q)

    # grau de saída
    outdeg = {q: 0 for q in q_ids}
    for u in succ:
        for v in succ[u]:
            outdeg[u] += 1

    # raízes
    roots = [q for q in q_ids if indeg[q] == 0]
    K = min(len(roots), N)

    # heróis ativos = K mais rápidos
    active_heroes = sorted(range(N), key=lambda h: prod[h], reverse=True)[:K]
    active_set = set(active_heroes)

    # estruturas
    # ready (t>0): (-outdeg, ready_ts, T, q)
    ready = []
    running = []          # (t_finish, h, q)
    hero_free_at = [0.0] * N

    assign = [[] for _ in range(N)]
    q_finish = {}
    t = 0.0

    # ---- t = 0: emparelha K raízes com K heróis mais rápidos
    # chave para as raízes: (-outdeg, -T, id)
    roots_items = [(-outdeg[q], -quests[q][0], q) for q in roots]
    heapq.heapify(roots_items)

    for h in active_heroes:
        if not roots_items:
            break
        neg_od, neg_T, q = heapq.heappop(roots_items)
        Tq = quests[q][0]
        t_fin = t + Tq / prod[h]
        hero_free_at[h] = t_fin
        heapq.heappush(running, (t_fin, h, q))
        assign[h].append(q)

    # raízes restantes entram no ready com ts=0
    while roots_items:
        neg_od, neg_T, q = heapq.heappop(roots_items)
        heapq.heappush(ready, (-neg_od, 0.0, -neg_T, q))  # (-outdeg, ts, T, q)

    def push_ready(q, ts):
        Tq = quests[q][0]
        heapq.heappush(ready, (-outdeg[q], ts, Tq, q))

    def best_wait_eft(q, p_now):
        """melhor EFT esperando um herói ocupado mais rápido que p_now"""
        Tq = quests[q][0]
        best = float('inf')
        for t_av, h_occ, _ in running:
            if h_occ in active_set and prod[h_occ] > p_now + EPS:
                eft = t_av + Tq / prod[h_occ]
                if eft < best:
                    best = eft
        return best

    while ready or running:
        if not running:
            break

        # ---- processa batelada de término
        t_first, h_fin, q_fin = heapq.heappop(running)
        t = t_first
        batch = [(h_fin, q_fin)]
        while running and abs(running[0][0] - t) <= EPS:
            _, h2, q2 = heapq.heappop(running)
            batch.append((h2, q2))

        # libera sucessores e marca conclusões
        for h_done, q_done in batch:
            hero_free_at[h_done] = t
            q_finish[q_done] = t
            for s in succ[q_done]:
                indeg[s] -= 1
                if indeg[s] == 0:
                    push_ready(s, t)

        # ---- heróis ativos livres em t (inclui quem já estava ocioso)
        free_now = [h for h in active_set if hero_free_at[h] <= t + EPS]
        free_now.sort(key=lambda h: prod[h], reverse=True)

        # cada herói pega no máximo 1 tarefa neste evento
        deferred = []
        for h in free_now:
            if not ready:
                continue
            p_now = prod[h]
            picked = None
            buf = []

            # tenta pegar o topo; se "vale esperar", adia e olha a próxima
            while ready:
                neg_od, tsr, Tq, q = heapq.heappop(ready)
                finish_now = t + Tq / p_now
                wait_eft = best_wait_eft(q, p_now)
                if wait_eft + EPS < finish_now:
                    buf.append((neg_od, tsr, Tq, q))  # adia
                    continue
                else:
                    picked = (neg_od, tsr, Tq, q)
                    break

            # devolve as adiadas
            for item in buf:
                deferred.append(item)

            if picked is None:
                continue

            neg_od, tsr, Tq, q = picked
            t_fin = t + Tq / p_now
            hero_free_at[h] = t_fin
            heapq.heappush(running, (t_fin, h, q))
            assign[h].append(q)

        # devolve adiadas ao ready
        for item in deferred:
            heapq.heappush(ready, item)

    # ---- saída
    for h in range(N):
        tasks_sorted = sorted(assign[h])  # juiz costuma querer por id asc
        print(f"{heroes[h]} = " + "{" + ",".join(map(str, tasks_sorted)) + "}")
    makespan = max(q_finish.values()) if q_finish else 0.0
    print(f"Tempo mínimo: {makespan:.2f}")

if __name__ == "__main__":
    X = int(sys.stdin.readline())
    for case in range(X):
        solve_case()
        if case < X - 1:
            print()
