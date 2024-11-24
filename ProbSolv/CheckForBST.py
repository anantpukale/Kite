#User function template for Python

class Solution:
	def remove_duplicate(self, A, N):
		arr = A
		dict = {}
		for i in range(len(arr)):
			if (dict.__contains__(arr[i])):
				dict[arr[i]] = dict[arr[i]] + 1
				if(i< len(arr)):
					arr.pop(i)
			else:
				dict[arr[i]] = 1
		print(len(arr))

n = 5
A=[2,2,2,2,2]
Solution.remove_duplicate(Solution,A,n)
for i in range(n):
    print(A[i], end=" ")
print()


# } Driver Code Ends