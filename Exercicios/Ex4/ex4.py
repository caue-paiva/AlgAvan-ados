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
    
    # Controle de quando cada herói ficará livre (para enfileiramento sequencial)
    hero_next_free_time = [0.0] * N
    
    # Resultado
    hero_assignments = [[] for _ in range(N)]
    quest_completion_time = {}
    
    # Inicializar ready com quests sem dependências
    for quest_id in quest_ids:
        if in_degree[quest_id] == 0:
            bl = bottom_level[quest_id]
            time_base = quests[quest_id][0]
            # Empate: priorizar maior bl, depois maior tempo, depois menor id
            heapq.heappush(ready, (-bl, -time_base, 0.0, quest_id))
    
    t = 0.0
    
    while ready or running:
        # Estratégia: Se há eventos próximos (dentro de um small delay), processar primeiro
        # para ter melhor visibilidade de tarefas que ficarão prontas
        next_event_time = running[0][0] if running else float('inf')
        delay_threshold = 0.0  # Processar imediatamente, sem delay
        
        if running and ready and (next_event_time - t) <= delay_threshold:
            # Há evento próximo, processar primeiro para ter melhor visão global
            pass  # Pula para processamento de eventos
        else:
            # Atribuir tarefas enquanto há heróis livres e tarefas prontas
            while freeHeroes and ready:
                # Tarefa mais crítica
                neg_bl, neg_time, timestamp, quest_id = heapq.heappop(ready)
                time_base = quests[quest_id][0]
                
                # Estratégia: Para tarefas críticas (BL alto), sempre dar ao herói mais produtivo
                # mesmo que esteja ocupado. Para tarefas menos críticas, pode dar a herói livre menos produtivo
                
                bl = bottom_level[quest_id]
                
                # Determinar se é tarefa crítica (apenas as TOP priority)
                max_bl = max(bottom_level.values())
                is_critical = bl == max_bl  # Apenas as de máxima prioridade
                
                if is_critical:
                    # Tarefa crítica: distribuir entre os top heróis para balancear carga
                    # Ordenar heróis por produtividade (desc) 
                    heroes_by_prod = sorted(range(N), key=lambda h: hero_productivity[h], reverse=True)
                    
                    # Escolher entre os top 2 heróis mais produtivos o que fica livre primeiro
                    candidates = heroes_by_prod[:min(2, N)]  # Top 2 ou menos se N < 2
                    
                    best_hero = None
                    best_completion_time = float('inf')
                    
                    for hero_id in candidates:
                        # Calcular quando este herói ficará livre (considerando fila de tarefas)
                        hero_free_time = max(t, hero_next_free_time[hero_id])
                        completion_time = hero_free_time + time_base / hero_productivity[hero_id]
                        
                        if completion_time < best_completion_time:
                            best_hero = hero_id
                            best_completion_time = completion_time
                    
                    # Se herói estava livre, remover da heap
                    temp_heroes = []
                    while freeHeroes:
                        neg_prod, hero_id = heapq.heappop(freeHeroes)
                        if hero_id != best_hero:
                            temp_heroes.append((neg_prod, hero_id))
                    
                    # Restaurar outros heróis à heap
                    for hero_data in temp_heroes:
                        heapq.heappush(freeHeroes, hero_data)
                else:
                    # Tarefa não crítica: considerar esperar pelo herói mais produtivo se espera for pequena
                    most_productive_hero = max(range(N), key=lambda h: hero_productivity[h])
                    
                    # Calcular quando herói mais produtivo ficará livre (considerando fila de tarefas)
                    mp_free_time = max(t, hero_next_free_time[most_productive_hero])
                    mp_completion_time = mp_free_time + time_base / hero_productivity[most_productive_hero]
                    
                    # Comparar com melhor herói livre
                    temp_heroes = []
                    best_free_hero = None
                    best_free_completion = float('inf')
                    best_free_productivity = 0
                    
                    while freeHeroes:
                        neg_prod, hero_id = heapq.heappop(freeHeroes)
                        productivity = -neg_prod
                        completion_time = t + time_base / productivity
                        
                        if productivity > best_free_productivity:
                            if best_free_hero is not None:
                                temp_heroes.append((-hero_productivity[best_free_hero], best_free_hero))
                            best_free_hero = hero_id
                            best_free_completion = completion_time
                            best_free_productivity = productivity
                        else:
                            temp_heroes.append((neg_prod, hero_id))
                    
                    # Decidir: se esperar pelo herói mais produtivo adiciona menos de 50% do tempo da tarefa, vale a pena
                    wait_threshold = time_base * 0.5
                    if (mp_completion_time - best_free_completion) <= wait_threshold:
                        # Vale a pena esperar
                        best_hero = most_productive_hero
                        best_completion_time = mp_completion_time
                        
                        # Não adicionar herói ocupado de volta à heap
                        for hero_data in temp_heroes:
                            if hero_data[1] != most_productive_hero:
                                heapq.heappush(freeHeroes, hero_data)
                    else:
                        # Usar herói livre
                        best_hero = best_free_hero
                        best_completion_time = best_free_completion
                        
                        # Restaurar heróis não selecionados à heap
                        for hero_data in temp_heroes:
                            heapq.heappush(freeHeroes, hero_data)
                
                # Atribuir tarefa ao melhor herói
                t_fim = best_completion_time
                
                # Atualizar quando este herói ficará livre para próximas tarefas
                hero_next_free_time[best_hero] = t_fim
                
                # Atribuição realizada
                
                # Adicionar à fila de execução
                heapq.heappush(running, (t_fim, best_hero, quest_id))
                
                # Registrar atribuição
                hero_assignments[best_hero].append(quest_id)
        
        # Se não há nada executando, acabou
        if not running:
            break
        
        # Processar todos os eventos que terminam no mesmo tempo (batching)
        # Primeiro evento
        t_fim, hero_id, quest_id = heapq.heappop(running)
        t = t_fim
        
        # Lista de eventos que terminam no mesmo tempo
        completed_events = [(hero_id, quest_id)]
        
        # Verificar se há mais eventos no mesmo tempo
        while running and running[0][0] == t_fim:
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
                    # Mas dar ligeira vantagem a tarefas que ficaram prontas primeiro (timestamp)
                    heapq.heappush(ready, (-bl, -time_base, t, successor))
            
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
