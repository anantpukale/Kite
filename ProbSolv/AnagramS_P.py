
class AnnagramS_P:
    def __init__(self, s: str, p: str):
        self.s = s
        self.p = p

    def getAnnagramIndices(self):
        n = len(self.p)
        sorted_p = sorted(self.p)
        #[print(i+n) for i in range(0, len(self.s), 1)]
        #out = [if(sorted((self.s[i:i + n]).__contains__(sorted_p))): i for i in range(0, len(self.s), 1)]
        out = [ (self.s[i:i+n]) for i in range(0, len(self.s),1)]
        outIndices = []
        i = 0
        for word in out:
            if(sorted(word).__eq__(sorted_p)):
                outIndices.append(int(i))
            i += 1
        return outIndices



class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        sorted_s= sorted(s)
        sorted_t = sorted(t)
        if sorted_s.__eq__(sorted_t):
            return True
        else:
            False

class SolutionA:
    def titleToNumber(self, columnTitle: str) -> int:
        ans, pos = 0, 0
        for letter in reversed(columnTitle):
            digit = ord(letter) - 64
            ans += digit * 26 ** pos
            pos += 1
        return ans

    def nCr(n, r):

        return (SolutionA.fact(n) / (SolutionA.fact(r)
                           * SolutionA.fact(n - r)))

    def nPr(n,r):
        return (SolutionA.fact(n)/(SolutionA.fact(n-r)))

    def fact(n):
        if n == 0:
            return 1
        res = 1

        for i in range(2, n + 1):
            res = res * i

        return res


a = SolutionA().titleToNumber("ZY")
print(a)

#
#print(str(AnnagramS_P("acdcaeccde","c").getAnnagramIndices()).replace(' ',''))