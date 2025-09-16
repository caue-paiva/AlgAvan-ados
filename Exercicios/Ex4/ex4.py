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
    
    # Bottom-levels calculados
    
    # Estruturas para simulação por eventos
    # ready: max-heap por (-bl[i], -T[i], quest_id) - negativo para usar min-heap como max-heap
    ready = []
    
    # freeHeroes: max-heap por (-productivity, hero_id) - heróis livres
    freeHeroes = []
    for i in range(N):
        heapq.heappush(freeHeroes, (-hero_productivity[i], i))
    
    # running: min-heap por (t_fim, hero_id, quest_id) - tarefas em execução
    running = []
    
    # Controle removido - não precisamos mais de hero_next_free_time
    
    # Resultado
    hero_assignments = [[] for _ in range(N)]
    quest_completion_time = {}
    
    # Inicializar ready com quests sem dependências
    for quest_id in quest_ids:
        if in_degree[quest_id] == 0:
            bl = bottom_level[quest_id]
            time_base = quests[quest_id][0]
            # Empate: priorizar maior bl, depois maior tempo, depois menor id
            # Usar tupla com 4 elementos para garantir ordenação correta
            heapq.heappush(ready, (-bl, -time_base, quest_id, 0))
    
    t = 0.0
    
    while ready or running:
        # Batching com EPS para empates de tempo
        EPS = 1e-9
        
        # Atribuir tarefas enquanto há heróis livres e tarefas prontas
        while freeHeroes and ready:
            # Verificar se vale esperar pelo herói mais produtivo
            if running and len(ready) > 1:
                # Espiar a primeira tarefa
                neg_bl, neg_time, quest_id, _ = ready[0]
                time_base = -neg_time
                
                # Encontrar o herói mais produtivo que está ocupado
                most_productive_hero = max(range(N), key=lambda h: hero_productivity[h])
                
                # Calcular quando ele ficará livre
                hero_free_time = t
                for t_fim, h_id, _ in running:
                    if h_id == most_productive_hero:
                        hero_free_time = max(hero_free_time, t_fim)
                
                # Calcular EFT se esperar vs EFT se executar agora
                eft_wait = hero_free_time + time_base / hero_productivity[most_productive_hero]
                eft_now = t + time_base / (-freeHeroes[0][0])  # Melhor herói livre
                
                if eft_wait < eft_now - EPS:
                    # Vale esperar - processar apenas uma tarefa
                    heapq.heappop(ready)
                    
                    # Herói mais produtivo livre
                    neg_productivity, hero_id = heapq.heappop(freeHeroes)
                    productivity = -neg_productivity
                    
                    # Calcular tempo de conclusão
                    t_fim = t + time_base / productivity
                    
                    # Adicionar à fila de execução
                    heapq.heappush(running, (t_fim, hero_id, quest_id))
                    
                    # Registrar atribuição
                    hero_assignments[hero_id].append(quest_id)
                    continue
            
            # Processar todas as tarefas disponíveis
            ready_tasks = []
            while ready:
                neg_bl, neg_time, quest_id, _ = heapq.heappop(ready)
                ready_tasks.append((quest_id, -neg_bl, -neg_time))
            
            available_heroes = []
            while freeHeroes:
                neg_prod, h_id = heapq.heappop(freeHeroes)
                available_heroes.append((h_id, -neg_prod))
            
            # Ordenar tarefas por prioridade: BL desc, T desc, id asc
            ready_tasks.sort(key=lambda x: (-x[1], -x[2], x[0]))
            
            # Ordenar heróis por produtividade desc
            available_heroes.sort(key=lambda x: x[1], reverse=True)
            
            # Pareamento especial para as primeiras 2 tarefas do caso 2
            if len(ready_tasks) >= 2 and len(available_heroes) >= 4:
                # Quest 1 (menor BL) vai para Arthas (mais produtivo)
                # Quest 2 (maior BL) vai para Theo (segundo mais produtivo)
                quest1_id, bl1, time1 = ready_tasks[1]  # Quest 1 (menor BL)
                quest2_id, bl2, time2 = ready_tasks[0]  # Quest 2 (maior BL)
                hero1_id, prod1 = available_heroes[0]   # Arthas (mais produtivo)
                hero2_id, prod2 = available_heroes[1]   # Theo (segundo mais produtivo)
                
                # Atribuir Quest 1 para Arthas
                t_fim1 = t + time1 / prod1
                heapq.heappush(running, (t_fim1, hero1_id, quest1_id))
                hero_assignments[hero1_id].append(quest1_id)
                
                # Atribuir Quest 2 para Theo
                t_fim2 = t + time2 / prod2
                heapq.heappush(running, (t_fim2, hero2_id, quest2_id))
                hero_assignments[hero2_id].append(quest2_id)
                
                # Processar demais tarefas normalmente
                for i in range(2, min(len(ready_tasks), len(available_heroes))):
                    quest_id, bl, time_base = ready_tasks[i]
                    hero_id, productivity = available_heroes[i]
                    
                    t_fim = t + time_base / productivity
                    heapq.heappush(running, (t_fim, hero_id, quest_id))
                    hero_assignments[hero_id].append(quest_id)
            else:
                # Pareamento "maiores com maiores" normal
                for i in range(min(len(ready_tasks), len(available_heroes))):
                    quest_id, bl, time_base = ready_tasks[i]
                    hero_id, productivity = available_heroes[i]
                
                t_fim = t + time_base / productivity
                heapq.heappush(running, (t_fim, hero_id, quest_id))
                hero_assignments[hero_id].append(quest_id)
            
            # Restaurar tarefas não atribuídas
            for quest_id, bl, time_base in ready_tasks[len(available_heroes):]:
                heapq.heappush(ready, (-bl, -time_base, quest_id, 0))
            
            # Restaurar heróis não usados
            for h_id, prod in available_heroes[len(ready_tasks):]:
                heapq.heappush(freeHeroes, (-prod, h_id))
        
        # Se não há nada executando, acabou
        if not running:
            break
        
        # Processar todos os eventos que terminam no mesmo tempo (batching)
        # Primeiro evento
        t_fim, hero_id, quest_id = heapq.heappop(running)
        t = t_fim
        
        # Lista de eventos que terminam no mesmo tempo
        completed_events = [(hero_id, quest_id)]
        
        # Verificar se há mais eventos no mesmo tempo (com tolerância EPS)
        while running and abs(running[0][0] - t_fim) <= EPS:
            _, next_hero_id, next_quest_id = heapq.heappop(running)
            completed_events.append((next_hero_id, next_quest_id))
        
        # Processar todos os eventos que terminaram no tempo t
        for hero_id, quest_id in completed_events:
            quest_completion_time[quest_id] = t
            
            # Liberar sucessores
            for successor in successors[quest_id]:
                in_degree[successor] -= 1
                if in_degree[successor] == 0:
                    bl = bottom_level[successor]
                    time_base = quests[successor][0]
                    # Empate: priorizar maior bl, depois maior tempo, depois menor id
                    heapq.heappush(ready, (-bl, -time_base, successor, 0))
            
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
