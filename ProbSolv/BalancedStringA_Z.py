class BalancedStringA_Z:
    def __init__(self, instr: str):
        self.instr = instr

    def dictAdd(dict, ch):
        if (dict.__contains__(ch)):
            dict[ch] = dict[ch] + 1
        else:
            dict[ch] = 1
        return dict

    def isBalanced(self):
        if (len(set(self.instr)) % 26 != 0):
            return False

        dict = {}
        sum = 0
        print(sum)
        for ch in self.instr:
            dict = BalancedStringA_Z.dictAdd(dict, ch)
            sum = sum + dict[ch]
        if sum % 26 .__eq__(0):
            return True
        else:
            return False

    def getBalancedSubStrings(self):

        for n in range(1,len(self.instr)):
            out = [(self.instr[i:i + n]) for i in range(0, len(self.instr), 1)]

        print(out)



BalancedStringA_Z("RLRRLLRLRL").getBalancedSubStrings()
# T = input()  # Reading input from STDIN
# print('Test, %s.' % T)  # Writing output to STDOUT
#
# for t in range(int(T)):
#     S = input()
#     if (BalancedStringA_Z(S).isBalanced() == True):
#         print("YES")
#     else:
#         print("NO")



