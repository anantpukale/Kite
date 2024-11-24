# class Node:
#     def __int__(self,data):
#         self.data= data
#         self.next= None
#
#     def ll_merger_sort(head ):
#         if (head == None):
#             return
#
#         mid = Node.get_middle(head)
#         left= Node.ll_merger_sort(head)
#         right= Node.ll_merger_sort(mid)
#
#         sortlist = Node.sorted_merge(left, right)
#         return sortlist
#
#
#     def sorted_merge(a, b):
#         if a == None:
#             return b
#         if b == None:
#             return a
#
#         if a.data <= b.data:
#             result = a
#             result.next = Node.sorted_merge(a.next, b)
#         else:
#             result = b
#             result.next = Node.sorted_merge(a, b.next)
#
#         return result
#
#     def get_middle(head):
#         if(head == None):
#             return head
#         slow = head
#         fast = head
#
#         while(fast.next != None and fast.next.next != None):
#             slow = slow.next
#             fast = fast.next.next
#
#         return slow
#
#
# def merge_sort(arr):
#     if(len(arr) > 1):
#         mid = int(len(arr)/2)
#
#         L = arr[:mid]
#         R = arr[mid:]
#
#         merge_sort(L)
#          merge_sort(R)
#
#         i = j = k = 0
#
#         while(i< len(L) and j < len(R)):
#             if L[i] < R[j]:
#                 arr[k]=L[i]
#                 i+=1
#
#             else:
#                 arr[k] = R[j]
#                 j+=1
#             k+=1
#
#         while i< len(L):
#             arr[k]=L[i]
#             k+=1
#             i+=1
#
#         while j< len(R):
#             arr[k]=R[j]
#             k+=1
#             j+=1
#
# def printList(arr):
#     for i in range(len(arr)):
#         print(arr[i], end=" ")
#     print()
#
#
#
# arr = [12, 11, 13, 5, 6, 7]
# print("Given array is", end="\n")
# printList(arr)
# merge_sort(arr)
# print("Sorted array is: ", end="\n")
# printList(arr)
#
#
#
#
