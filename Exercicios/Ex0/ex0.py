

Nruns = int(input())

def parse_input()->list[float]:
    N = input()
    vals = []
    for _ in range(N):
        vals.append(
            float(input())
        )
    return vals


def prefix_arr(nums) -> list[float]:
    total = sum(nums)
    remaining_money = []
    for num in nums:
        remaining_money.append(total-num)
        total -= num
    return remaining_money

#for cases N >= 2
def greedy_guy(nums,prefix) -> int:
    i = 0
    j = 1

    window_sum = nums[0] + nums[1]


for i in range(Nruns):
    nums = parse_input()
    pre_arr = prefix_arr(nums)