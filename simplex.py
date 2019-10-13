
"""
    Simplex runnable
    author: Hayder
    mailto: hayder_endo@icloud.com
"""

def getPairs(side):
    i = 0
    pairs = {}
    while i < len(side):
        if side[i] in ' \r\n':
            i += 1
            continue
        coef = ''
        while i < len(side) and side[i].isdigit() or side[i] in '+- .':
            if side[i] != ' ':
                coef += side[i]
            i += 1
        if coef == '':
            coef = ONE
        elif coef in '+-':
            coef += '1'
            coef = Frac(int(coef))
        
        if type(coef) == str and coef.count('.') > 0:
            parts = coef.split('.')
            num = int(parts[0] + parts[1])
            den = 10**(len(parts[1]))
            coef = Frac(num, den)
        name = ''
        while i < len(side) and side[i] != ' ':
            name += side[i]
            i += 1
        if type(coef) == str:
            pairs[name] = Frac(coef)
        else:
            pairs[name] = coef
    return pairs

if __name__ == '__main__':
    
    import sys
    from bound import Bound
    from model import Model
    from target import Target
    from frac import *
    
    if len(sys.argv) < 1:
        print('Provide a file')

    else:
        model = []
        with open(sys.argv[1]) as f:
            model = f.readlines()
        
        # Target function
        target = model[0].split('=')
        left = target[0].split(' ')
        right = target[1].replace('\n','')
        
        pairs = getPairs(right)

        # Bounds
        bounds = []
        for i in range(1, len(model)):
            bound = model[i].replace('\n','')
            kind = ''
            if bound.count('<=') > 0:
                kind = '<='
            elif bound.count('<') > 0:
                kind = '<'
            elif bound.count('>=') > 0:
                kind = '>='
            elif bound.count('>') > 0:
                kind = '>'
            elif bound.count('=') > 0:
                kind = '='
            else:
                raise Exception('Invalid bound')
            bound = bound.split(kind)
            b = bound[1].strip()
            if b.count('.'):
                parts = b.split('.')
                num = int(parts[0] + parts[1])
                den = 10**(len(parts[1]))
                b = Frac(num, den)
            else:
                b = Frac(b)
            bound_pairs = getPairs(bound[0])
            non_neg = False
            if len(bound_pairs.keys()) == 1:
                this = bound_pairs.popitem()
                non_neg = this[1] == ONE and kind == '>=' and b.eq(ZERO)
                bound_pairs[this[0]] = this[1]
            bounds.append(Bound(bound_pairs, kind, b, non_neg))

        model = Model(Target(left[0], pairs), bounds)
        try:
            model.solve()
        except Exception as e:
            print(e)
        


