N = int(input())

hash_map = {}

for _ in range(N):
    line = input().split(" ")
    key = line[0]
    val = float(line[1])
    if key in hash_map:
        print(f"Produto com código {key} já cadastrado.")
        continue
    hash_map[key] = val

while True:
    num_orders = int(input())
    if num_orders == -1:
        break
    acc = 0
    for _ in range(num_orders):
        line = input().split(" ")
        key,qnt = line[0],float(line[1])
        if key in hash_map:
            acc += hash_map[key] * qnt
        else:
            print(f"Produto com código {key} não cadastrado.")
    print(f"R${acc:.2f}")

