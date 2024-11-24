class Node:
    def __init__(self,data):
        self.data = data
        self.next = None

    def isPalindrome(self)-> bool:
        if(selfa == None):
            return

        stack = []
        curr = self
        while(curr != None):
            stack.append(curr.data)
            curr = curr.next
        curr = self
        isPalind= True

        while(curr != None):
            i= stack.pop()
            if(not curr.data.__eq__(i)):
                isPalind = False
                break

        return isPalind


# Addition of linked list
one = Node(1)
two = Node(2)
three = Node(3)
four = Node(4)
five = Node(3)
six = Node(2)
seven = Node(1)

# Initialize the  pointer
# of every current pointer
one.next = two
two.next = three
three.next = four
four.next = five
five.next = six
six.next = seven
seven.next = None

print(one.isPalindrome())
