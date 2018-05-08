"""
Functions for dealing with the normal distribution.
"""

import math

def memoized(func):
    """A memoization decorator."""
    cache = {}
    def wrap(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    return wrap

@memoized
def c(k):
    """The MacLaurin coefficient for erf_inv."""
    if k == 0:
        return 1

    res = 0
    for m in range(k):
        res += (c(m) * c(k - 1 - m)) / float((m + 1) * (2*m + 1))

    return res

def erf_inv(z, steps=300):
    """THe inverse error function approximated through its MacLaurin series
    expansion.

    The value z must be inside <-1, 1>.
    """
    if not (-1 < z < 1):
        raise ValueError(z)

    res = 0
    for k in range(steps):
        res += (c(k) / (2*k + 1)) * (math.sqrt(math.pi) * z / 2.0)**(2*k + 1)

    return res

def phi_inv(p):
    """The normal distribution's quantile function z_p / phi^(-1)(p)."""
    return math.sqrt(2) * erf_inv(2*p - 1)

def confidence_interval(mu, sd, n, alpha):
    """Calculates the confidence interval given the normal distribution."""
    if n == 0:
        return 0, 0
    z = phi_inv(1.0 - alpha/2.0)
    return mu - z*sd/math.sqrt(n), mu + z*sd/math.sqrt(n)

def prediction_interval(mu, sd, alpha):
    """Calculates the prediction interval given the normal distribution."""
    z = phi_inv(1.0 - alpha/2.0)
    return mu - z*sd, mu + z*sd
