"""
    Represents the target function for an optimizacion model
    author: Hayder
    mailto: hayder_endo@icloud.com
"""
class Target:

    def __init__(self, kind, pairs):

        self.kind = kind
        self.pairs = pairs
    
    def __str__(self):
        rep = self.kind
        rep += ' z = '
        for pair in self.pairs:
            rep += str(self.pairs[pair]) + pair + ' '
        return rep
         
