import collections
from collections import deque


class Node:
    def __init__(self,data):
        self.data = data
        self.left = None
        self.right = None
        self.nextRight = None

    def connect(root):
        if root == None:
            return

        queue = []

        queue.append(root)
        prevNode = Node(None)
        while(len(queue) != 0):
            size = len(queue)
            for i in range(size):
                temp = queue.pop(0)
                if temp.left != None:
                    queue.append(temp.left)

                if temp.right != None:
                    queue.append(temp.right)

                if prevNode != None:
                    if i == 0:
                        print(i, size)
                        prevNode.nextRight = None
                    else:
                        prevNode.nextRight = temp
                    prevNode = temp




root = Node(10)
root.left = Node(8)
root.right = Node(2)
root.left.left = Node(3)
root.left.right = Node(7)
root.right.left = Node(11)
root.right.right = Node(12)

# Populates nextRight pointer in all nodes
Node.connect(root)
# if root.left.nextRight:
#     print(root.left.nextRight.data)
# else:
#     print(-1)

a = deque()

m = collections.Mapping()

m.items()

