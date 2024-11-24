
class Node:
    def __init__(self,data):
        self.data= data
        self.left = None
        self.right = None

    def build_zigzag(root):
        if(root == None):
            return

        stack = []
        c = 0
        stack.append(root)
        while(len(stack) != 0):
            size = len(stack)
            p_stack = []
            for i in range(size):
                c+=1
                temp = stack.pop(0)
                p_stack.append(temp.data)
                if temp.left != None:
                    stack.append(temp.left)

                if temp.right != None:
                    stack.append(temp.right)
            if(c%2==0):
                p_stack = p_stack[::-1]
            for p in range(len(p_stack)):
                print(p_stack.pop())








root= Node(7)
root.left = Node(9)
root.right = Node(7)
root.left.left = Node(8)
root.left.right = Node(1)
root.right.left = Node(6)
root.left.left.right = Node(9)
root.left.left.left = Node(10)

Node.build_zigzag(root)


