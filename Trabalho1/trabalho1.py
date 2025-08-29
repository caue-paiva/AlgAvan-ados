class TrieNode:
    children: dict[str,"TrieNode"]
    is_word: bool
    word: str

    def __init__(self):
        self.children = {}
        self.is_word = False
        self.word = ""
    
def PrefixExists(Node: TrieNode ,prefix:str, index:int)->bool:
        if len(prefix) == index:
            return True
        curChar = prefix[index]
        if curChar in Node.children:
            nextNode = Node.children[curChar]
            return PrefixExists(nextNode,prefix,index+1)
        return False

def AppendWord(Node:TrieNode,word:str,index:int):
    if len(word) == index:
        Node.is_word = True 
        Node.word = word
        return
    curChar = word[index]
    if curChar in Node.children:
        return AppendWord(Node.children[curChar],word,index+1)
    else:
        NewNode = TrieNode()
        Node.children[curChar] = NewNode
        return AppendWord(NewNode,word,index+1)

def PrintTrie(node: TrieNode, level: int = 0, prefix: str = ""):
    indent = "  " * level
    if node.is_word:
        print(f"{indent}({prefix})")

    for ch, child in node.children.items():
        print(f"{indent}{ch}")
        PrintTrie(child, level + 1, prefix + ch)

def BuildTrie(dictionary:list[str])->TrieNode:
    trieRoot = TrieNode()
    for word in dictionary:
        AppendWord(trieRoot,word,0)
    return trieRoot

# move 0 => all directions
# other moves: 1 => right, 2 => left, 3 => up, 4 => down, 5 => right up, 6 => right down, 7 => left up, 8 => left down 
def addNeighbors(node:TrieNode, i,j, n,m:int, stack:list,move:int):
    directions = [
        (-1, -1), (-1, 0), (-1, 1),  
        (0, -1),          (0, 1),   
        (1, -1),  (1, 0), (1, 1)    
    ]
    
    #maps a direction num to the index of the corresponding next move
    move_to_direction = {
        1: [4],  # right
        2: [3],  # left
        3: [1],  # up
        4: [6],  # down
        5: [2],  # right up
        6: [7],  # right down
        7: [0],  # left up
        8: [5]   # left down
    }

    if move == 0:
        for next_move in move_to_direction:
            direction_index =  move_to_direction[next_move][0]
            di, dj = directions[direction_index]
            ni, nj = i + di, j + dj
            if 0 <= ni < n and 0 <= nj < m:
                stack.append((ni, nj, node, next_move))
    elif move in move_to_direction:
        direction_index =  move_to_direction[move][0]
        di, dj = directions[direction_index]
        ni, nj = i + di, j + dj
        if 0 <= ni < n and 0 <= nj < m:
            stack.append((ni, nj, node, move))

def SearchWordStartingAt(data:list[list[str]], i,j:int, foundWords:set, trieRoot:TrieNode):
    node = trieRoot
    stack = [(i,j,node,0)] #move 0 => first letter of word
    n,m = len(data),len(data[0])

    while stack:
        i,j,curNode,move = stack.pop()
        curChar = data[i][j]

        if curChar in curNode.children:
            nextNode = curNode.children[curChar]
            if nextNode.is_word:
                foundWords.add(nextNode.word)
            addNeighbors(nextNode,i,j,n,m,stack,move)

def getInput()->tuple[list[list[str]],list[str]]:
   line = input().split(" ")
   n,m = int(line[0]),int(line[1])
   dataGrid = []

   for _ in range(n):
        lineIn = input()
        dataGrid.append([ c for c in lineIn])

   nDict = int(input())
   wordsDict = []
   for _ in range(nDict):
        wordsDict.append(input())

   return dataGrid,wordsDict

data,dictionary = getInput()
trie = BuildTrie(dictionary)

foundWords = set()
for i in range(len(data)):
    for j in range(len(data[0])):
        SearchWordStartingAt(data,i,j,foundWords,trie)


print(len(foundWords))
resultList = sorted(list(foundWords))
for word in resultList:
    print(word)