import sys

def trap(bars):
    if(len(bars)<=2):
        return 0

    water = 0
    n = len(bars)
    left = [None] * (n-1)
    left[0] = -sys.maxsize

    for i in range(1 , n-1):
        left[i] = max(left[i-1],bars[i-1] )

    right = -sys.maxsize
    for i in reversed(range(1, n-1)):
        right = max(right, bars[i+1])

        if( min(left[i], right) > bars[i]):
            print(i)
            water += min(left[i],right) - bars[i]

    return water

if __name__ == '__main__':
    heights = [5, 0, 4, 2, 5, 0, 6, 4, 0, 5]
    print("The maximum amount of water that can be trapped is", trap(heights))