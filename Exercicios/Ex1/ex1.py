Ntests = int(input())

for _ in range(Ntests):
    N = int(input())
    parentDict = {}
    diabetesDict = {-1:False}

    for _ in range(N):
        lineVals = input().split(" ")
        personID = int(lineVals[0])
        
        hasDiab = lineVals[1] == "sim"
        
        fatherID = int(lineVals[2])
        motherID = int(lineVals[3])

        diabetesDict[personID] = hasDiab
        parentDict[personID] = (fatherID,motherID)
    
    acc = 0
    for son in parentDict:
        #key == filho
        father,mother = parentDict[son]
        if diabetesDict[son] and (diabetesDict[father] or diabetesDict[mother]):
            acc += 1
    
    print(acc)
    
