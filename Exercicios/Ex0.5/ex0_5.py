import math, heapq

R = 6371 

def haversine(latC,longC,latInput,longInput)-> float:
    latC = math.radians(latC)
    longC = math.radians(longC)
    latInput = math.radians(latInput)
    longInput = math.radians(longInput)

    deltaPhi =  latInput - latC
    deltaLambda = longInput - longC
    square = math.sqrt(
        (math.sin(deltaPhi/2)**2) +
        
        ((math.cos(latC)*math.cos(latInput)) *
        ((math.sin(deltaLambda/2))**2))
    )

    return 2*R * math.asin(square)

i = 1 #numero do jogador

n = int(input())
correctCoords = input().split(" ")
latC,longC = float(correctCoords[0]), float(correctCoords[1])

pQueue = []

for i in range(1,n+1):
    line = input().split(" ")
    name,latIn,longIn = line[0], float(line[1]), float(line[2])
    hDist = haversine(latC,longC,latIn,longIn)
    heapq.heappush(pQueue,(hDist,i,name))


    bestDist = pQueue[0][0]
    print(f"> [AVISO] MELHOR PALPITE: {bestDist:.3f}km")


best = heapq.nsmallest(len(pQueue),pQueue)

print("\nRANKING")
print("-------")

posi = 1
for dist,i,name in best:
    position = f"{posi:>2}."
    
    name_field = f"{name:<20}"
    
    distance_field = f"{dist:>6.3f}"
    
    special_msg = " [FANTASTICO]" if dist <= 0.050 else ""
    
    if posi == len(best):
        print(f"{position} {name_field} : {distance_field} km{special_msg}", end="")
    else:
        print(f"{position} {name_field} : {distance_field} km{special_msg}")
    posi += 1 

