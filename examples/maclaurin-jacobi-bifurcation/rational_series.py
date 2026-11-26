"""Second enclosure, using only integers and the series in DERIVATION §5."""

from fractions import Fraction
from math import isqrt


def ceil_div(n, d):
    return -((-n)//d)


class Grid:
    """An interval (L, U) represents [L/scale, U/scale]."""

    def __init__(self, bits):
        self.scale = 1 << bits

    def interval(self, lo, hi):
        lo,hi = Fraction(lo),Fraction(hi)
        if lo > hi:
            raise ValueError("reversed grid input")
        s = self.scale
        return lo.numerator*s//lo.denominator, ceil_div(hi.numerator*s,hi.denominator)

    def number(self, value):
        return self.interval(value,value)

    def exact_bounds(self, x):
        return tuple(Fraction(t,self.scale) for t in x)

    @staticmethod
    def add(x, y):
        return x[0]+y[0],x[1]+y[1]

    @staticmethod
    def sub(x, y):
        return x[0]-y[1],x[1]-y[0]

    @staticmethod
    def times_integer(x, n):
        return (x[0]*n,x[1]*n) if n>=0 else (x[1]*n,x[0]*n)

    @staticmethod
    def times_positive_ratio(x, n, d):
        return x[0]*n//d,ceil_div(x[1]*n,d)

    def mul(self, x, y):
        products = [a*b for a in x for b in y]
        return min(products)//self.scale,ceil_div(max(products),self.scale)

    def div(self, x, y):
        if y[0]<=0:
            raise ValueError("nonpositive denominator")
        s = self.scale
        return (min(a*s//b for a in x for b in y),
                max(ceil_div(a*s,b) for a in x for b in y))

    def sqrt(self, x):
        if x[0]<0:
            raise ValueError("negative square-root enclosure")
        lo,hi = x[0]*self.scale,x[1]*self.scale
        root = isqrt(hi)
        return isqrt(lo),root+(root*root<hi)

    def power(self, x, n):
        result = self.number(1)
        while n:
            if n%2:
                result = self.mul(result,x)
            n //= 2
            if n:
                x = self.mul(x,x)
        return result

    def polynomial(self, coefficients, x):
        result = coefficients[-1]
        for i in range(len(coefficients)-2,-1,-1):
            result = self.add(coefficients[i],self.mul(x,result))
        return result


class Series:
    def __init__(self, bits, terms):
        if terms<2:
            raise ValueError("series requires at least two terms")
        self.grid = g = Grid(bits)
        self.terms = terms
        self.one = g.number(1)
        c = self.one
        self.arc = [c]
        self.psi = [g.number(Fraction(-4,15))]
        self.dpsi = []
        for n in range(1,terms+1):
            c = g.times_positive_ratio(c,2*n-1,2*n)
            self.arc.append(g.times_positive_ratio(c,1,2*n+1))
            numerator = 4*(4*n*n+8*n-1)
            denominator = (2*n+1)*(2*n+3)*(2*n+5)
            b = g.times_positive_ratio(c,numerator,denominator)
            self.psi.append(b)
            self.dpsi.append(g.times_integer(b,n))

    def enclose(self, mode, lo, hi):
        g,n = self.grid,self.terms
        e = g.interval(lo,hi)
        s = g.mul(e,e)
        q2 = g.sub(self.one,s)
        if not (0<s[0]<=s[1]<g.scale):
            raise ValueError("series request outside 0<e<1")
        power = g.power(s,n)
        if mode=="df":
            majorant = g.add(g.div(g.number(n+1),q2),g.div(s,g.mul(q2,q2)))
            tail = g.mul(power,majorant)
            low,high = g.polynomial(self.dpsi,s)
            enclosure = g.mul(g.times_integer(e,2),(low,high+tail[1]))
        else:
            tail = g.div(g.mul(power,s),q2)
            if mode=="f":
                low,high = g.polynomial(self.psi,s)
                enclosure = low,high+tail[1]
            elif mode=="omega":
                low,high = g.polynomial(self.arc,s)
                U = low,high+tail[1]
                q = g.sqrt(q2)
                shape = g.sub(g.number(3),g.times_integer(s,2))
                difference = g.sub(g.mul(shape,U),g.times_integer(q,3))
                enclosure = g.mul(g.div(g.times_integer(q,2),s),difference)
            else:
                raise ValueError("unknown series quantity")
        return g.exact_bounds(enclosure)
