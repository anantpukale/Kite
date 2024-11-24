# a= [-1,2,3,-1,1]

def getRearranged(arr):
    for i, item in enumerate(arr):
        if(item == i or i == -1):
            arr
        else:
            a = item
            idx = i
            while(a != -1 ):
                print("in")
                temp = arr[a]
                arr[a] = a
                arr[i] = temp
                a= temp


    return arr


a= [-1,2,3,-1,1,8]
print(getRearranged(a))
