import heapq
from collections import defaultdict, deque

def solve_quest_scheduling():
    # Mapeamento de níveis para produtividades
    level_productivity = {
        "Aprendiz": 0.75,
        "Aventureiro": 1.0,
        "Cavaleiro": 1.2,
        "Mestre": 1.5,
        "Lenda": 2.0
    }
    
    # Leitura da entrada
    N, M = map(int, input().split())
    
    # Leitura dos heróis
    heroes = []
    hero_productivity = []
    for i in range(N):
        line = input().split()
        name = line[0]
        level = line[1]
        productivity = level_productivity[level]
        heroes.append(name)
        hero_productivity.append(productivity)
    
    # Leitura das quests
    quests = {}  # quest_id -> (time_base, dependencies)
    quest_ids = []
    quest_times = []
    dependencies = defaultdict(list)  # quest -> list of dependencies
    successors = defaultdict(list)    # quest -> list of successors
    in_degree = defaultdict(int)
    
    for _ in range(M):
        line = list(map(int, input().split()))
        quest_id = line[0]
        time_base = line[1]
        deps = line[2:]
        
        quest_ids.append(quest_id)
        quest_times.append(time_base)
        quests[quest_id] = (time_base, deps)
        
        # Se deps contém apenas 0, não há dependências
        if len(deps) == 1 and deps[0] == 0:
            deps = []
        
        dependencies[quest_id] = deps
        in_degree[quest_id] = len(deps)
        
        # Construir lista de sucessores
        for dep in deps:
            if dep != 0:  # dep = 0 significa sem dependências
                successors[dep].append(quest_id)
    
    # Mapear quest_id para índice para facilitar acesso
    quest_to_idx = {quest_id: i for i, quest_id in enumerate(quest_ids)}
    
    # Calcular bottom-level usando DP reversa
    bottom_level = {}
    
    def calculate_bottom_level(quest_id):
        if quest_id in bottom_level:
            return bottom_level[quest_id]
        
        time_base = quests[quest_id][0]
        max_successor_bl = 0
        
        for successor in successors[quest_id]:
            max_successor_bl = max(max_successor_bl, calculate_bottom_level(successor))
        
        bottom_level[quest_id] = time_base + max_successor_bl
        return bottom_level[quest_id]
    
    # Calcular bottom-level para todas as quests
    for quest_id in quest_ids:
        calculate_bottom_level(quest_id)
    
    # Estruturas para simulação por eventos
    # ready: max-heap por (-bl[i], -T[i], quest_id) - negativo para usar min-heap como max-heap
    ready = []
    
    # freeHeroes: max-heap por (-productivity, hero_id) - heróis livres
    freeHeroes = []
    for i in range(N):
        heapq.heappush(freeHeroes, (-hero_productivity[i], i))
    
    # running: min-heap por (t_fim, hero_id, quest_id) - tarefas em execução
    running = []
    
    # Resultado
    hero_assignments = [[] for _ in range(N)]
    quest_completion_time = {}
    
    # Inicializar ready com quests sem dependências
    for quest_id in quest_ids:
        if in_degree[quest_id] == 0:
            bl = bottom_level[quest_id]
            time_base = quests[quest_id][0]
            # Empate: priorizar maior bl, depois maior tempo, depois menor id
            heapq.heappush(ready, (-bl, -time_base, quest_id))
    
    t = 0.0
    
    while ready or running:
        # Atribuir tarefas enquanto há heróis livres e tarefas prontas
        while freeHeroes and ready:
            # Herói mais produtivo livre
            neg_productivity, hero_id = heapq.heappop(freeHeroes)
            productivity = -neg_productivity
            
            # Tarefa mais crítica
            neg_bl, neg_time, quest_id = heapq.heappop(ready)
            time_base = quests[quest_id][0]
            
            # Calcular tempo de conclusão
            t_fim = t + time_base / productivity
            
            # Adicionar à fila de execução
            heapq.heappush(running, (t_fim, hero_id, quest_id))
            
            # Registrar atribuição
            hero_assignments[hero_id].append(quest_id)
        
        # Se não há nada executando, acabou
        if not running:
            break
        
        # Próximo evento de conclusão
        t_fim, hero_id, quest_id = heapq.heappop(running)
        t = t_fim
        quest_completion_time[quest_id] = t
        
        # Liberar sucessores
        for successor in successors[quest_id]:
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                bl = bottom_level[successor]
                time_base = quests[successor][0]
                # Empate: priorizar maior bl, depois maior tempo, depois menor id
                heapq.heappush(ready, (-bl, -time_base, successor))
        
        # Herói fica livre
        heapq.heappush(freeHeroes, (-hero_productivity[hero_id], hero_id))
    
    # Formatação da saída
    for i in range(N):
        assignments = sorted(hero_assignments[i])  # Ordenar por índice
        assignments_str = "{" + ",".join(map(str, assignments)) + "}"
        print(f"{heroes[i]} = {assignments_str}")
    
    # Tempo mínimo
    makespan = max(quest_completion_time.values()) if quest_completion_time else 0.0
    print(f"Tempo mínimo: {makespan:.2f}")

if __name__ == "__main__":
    # Leitura do número de casos de teste
    X = int(input())
    
    for case in range(X):
        solve_quest_scheduling()
        # Imprimir linha em branco entre casos, exceto no último
        if case < X - 1:
            print()
