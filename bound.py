"""
    Represents a bound for an optimization model
    author: Hayder
    mailto: hayder_endo@icloud.com
"""

class Bound:

    def __init__(self, pairs, kind, b, non_neg = False):
        self.pairs = pairs
        self.kind = kind
        self.b = b
        self.non_neg = non_neg

    def __str__(self):
        rep = ''
        for pair in self.pairs:
            rep += str(self.pairs[pair]) + pair + ' '
        rep += self.kind
        rep += str(self.b)
        return rep
        