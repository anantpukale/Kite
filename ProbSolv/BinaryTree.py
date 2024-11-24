#preorer root> left > right

class Node:
    def __init__(self,data):
        self.data = data
        self.left = None
        self.right = None

    def pre_order(node):
        if(node == None):
            return
        print(node.data, end=" ")
        Node.pre_order(node.left)
        Node.pre_order(node.right)


root = Node(1)
root.left = Node(2)
root.right = Node(4)
root.left.left = Node(5)
root.left.right = Node(6)

Node.pre_order(root)
