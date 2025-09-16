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

def compute_bottom_levels(quests, deps, succ):
    """BL iterativo no DAG: bl[u] = T[u] se folha, senão T[u] + max(bl[v])"""
    indeg = {q: len(deps.get(q, [])) for q in quests}
    q0 = deque([q for q in quests if indeg[q] == 0])
    topo = []
    while q0:
        u = q0.popleft()
        topo.append(u)
        for v in succ[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q0.append(v)
    bl = {q: quests[q][0] for q in quests}
    for u in reversed(topo):
        if succ[u]:
            bl[u] = quests[u][0] + max(bl[v] for v in succ[u])
    return bl

def solve_case():
    N, M = map(int, sys.stdin.readline().split())

    heroes = []
    prod = []
    for _ in range(N):
        name, level = sys.stdin.readline().split()
        heroes.append(name)
        prod.append(LEVEL_PRODUCTIVITY[level])

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

    # bottom-level para desempate
    bl = compute_bottom_levels(quests, deps, succ)

    # raízes e conjunto de heróis ativos: só os K mais rápidos trabalham
    roots = [q for q in q_ids if indeg[q] == 0]
    K = min(len(roots), N)
    active_heroes = sorted(range(N), key=lambda h: prod[h], reverse=True)[:K]
    active_set = set(active_heroes)

    # prioridade de tarefa: (-outdeg, -BL, -T, ready_ts, q)
    ready = []

    # t = 0: atribuir as K melhores raízes aos K heróis mais rápidos
    root_items = []
    for q in roots:
        Tq = quests[q][0]
        root_items.append((-outdeg[q], -bl[q], -Tq, 0.0, q))
    heapq.heapify(root_items)

    running = []         # (t_finish, h, q)
    hero_free_at = [0.0] * N
    assign = [[] for _ in range(N)]
    q_finish = {}
    t = 0.0

    # pega até K raízes para iniciar
    for h in active_heroes:
        if not root_items:
            break
        neg_od, neg_bl, neg_T, ts, q = heapq.heappop(root_items)
        Tq = quests[q][0]
        t_fin = t + Tq / prod[h]
        hero_free_at[h] = t_fin
        heapq.heappush(running, (t_fin, h, q))
        assign[h].append(q)

    # raízes restantes entram em ready
    while root_items:
        heapq.heappush(ready, heapq.heappop(root_items))

    # coloca no ready quaisquer tarefas não raízes cuja indegree tenha virado 0 ao longo do processo
    # (para este problema, só acontece após as primeiras conclusões)

    def best_wait_eft(q, p_now):
        """melhor EFT esperando um herói ocupado mais rápido"""
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

        # processa batelada de término
        t_first, h_fin, q_fin = heapq.heappop(running)
        t = t_first
        batch = [(h_fin, q_fin)]
        while running and abs(running[0][0] - t) <= EPS:
            _, h2, q2 = heapq.heappop(running)
            batch.append((h2, q2))

        # marcar conclusões e liberar sucessores
        for h_done, q_done in batch:
            hero_free_at[h_done] = t
            q_finish[q_done] = t
            for s in succ[q_done]:
                indeg[s] -= 1
                if indeg[s] == 0:
                    Ts = quests[s][0]
                    heapq.heappush(ready, (-outdeg[s], -bl[s], -Ts, t, s))

        # apenas heróis ativos que acabaram de ficar livres em t
        just_freed = sorted([h for h, _ in batch if h in active_set], key=lambda h: prod[h], reverse=True)

        # cada herói pega no máximo 1 tarefa neste evento
        deferred = []
        for h in just_freed:
            if not ready:
                continue
            p_now = prod[h]
            picked = None
            buf = []

            while ready:
                neg_od, neg_bl, neg_T, ts, q = heapq.heappop(ready)
                Tq = quests[q][0]
                finish_now = t + Tq / p_now
                wait_eft = best_wait_eft(q, p_now)

                # só adia se houver outra tarefa pronta para evitar ociosidade
                if wait_eft + EPS < finish_now and len(ready) >= 1:
                    buf.append((neg_od, neg_bl, neg_T, ts, q))
                    continue
                else:
                    picked = (neg_od, neg_bl, neg_T, ts, q)
                    break

            # devolve as adiadas
            for item in buf:
                deferred.append(item)

            if picked is None:
                continue

            neg_od, neg_b, neg_T, ts, q = picked
            Tq = quests[q][0]
            t_fin = t + Tq / p_now
            hero_free_at[h] = t_fin
            heapq.heappush(running, (t_fin, h, q))
            assign[h].append(q)

        for item in deferred:
            heapq.heappush(ready, item)

    # saída
    for h in range(N):
        tasks_sorted = sorted(assign[h])
        print(f"{heroes[h]} = " + "{" + ",".join(map(str, tasks_sorted)) + "}")
    makespan = max(q_finish.values()) if q_finish else 0.0
    print(f"Tempo mínimo: {makespan:.2f}")

if __name__ == "__main__":
    X = int(sys.stdin.readline())
    for case in range(X):
        solve_case()
        if case < X - 1:
            print()
