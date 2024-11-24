class Solution:
	def remove_duplicate(self, A, N):
		arr = A
		dict = {}
		for i in range(len(arr)):
			if (dict.__contains__(arr[i])):
				dict[arr[i]] = dict[arr[i]] + 1
			else:
				dict[arr[i]] = 1