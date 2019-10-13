"""
    Represents a fraction
    author: Hayder
    mailto: hayder_endo@icloud.com
"""
class Frac:

    def __init__(self, num, den=1):
        num = int(num)
        div = self.gcd(num, den)
        self.num = num // div
        self.den = den // div

    def gcd(self, a, b):
        if b == 0:
            return a
        return self.gcd(b, a % b) 

    def add(self, other):
        if type(other) == int:
            other = Frac(other, 1)
        den = self.den * other.den
        num = other.den * self.num + self.den * other.num
        div = self.gcd(num, den)
        return Frac(num // div, den // div)
    
    def mul(self, other):
        if type(other) == int:
            other = Frac(other, 1)
        num = self.num * other.num
        den = self.den * other.den 
        div = self.gcd(num, den)
        num //= div
        den //=  div
        return Frac(num, den)

    def sub(self, other):
        if type(other) == int:
            other = Frac(other, 1)
        return self.add(other.mul(-1))
    
    def div(self, other):
        if type(other) == int:
            other = Frac(other, 1)
        return self.mul(Frac(other.den, other.num))

    def __str__(self):
        if self.den == 1:
            return str(self.num)
        return str(self.num) + '/' + str(self.den)

    def lt(self, other):
        if type(other) == int:
            other = Frac(other, 1)
        diff = self.sub(other)
        return diff.num < 0

    def le(self, other):
        if type(other) == int:
            other = Frac(other, 1)
        diff = self.sub(other)
        return diff.num <= 0

    def gt(self, other):
        return other.lt(self)
    
    def ge(self, other):
        return other.le(self)

    def eq(self, other):
        if type(other) == int:
            other = Frac(other, 1)
        if self.num == 0 and other.num == 0:
            return True
        diff = self.sub(other)
        return diff.num == 0

ZERO = Frac(0,1)
ONE = Frac(1)
MONE = Frac(-1)