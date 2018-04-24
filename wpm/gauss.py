"""
Functions for dealing with the normal distribution.
"""

import math

def erf_inv(z, steps=10):
    """Computes the inverse error function thourh a few expansions of its
    Maclaurin series.

    The value z must be inside <-1, 1>.
    """
    def c(k):
        """MacLaurin coefficient."""
        if k == 0:
            return 1

        res = 0
        for m in range(k):
            res += (c(m) * c(k - 1 - m)) / float((m + 1) * (2*m + 1))
        return res

    if not (-1 < z < 1):
        raise ValueError(z)

    out = 0
    for k in range(steps):
        out += (c(k) / (2*k + 1)) * (math.sqrt(math.pi) * z / 2.0)**(2*k + 1)

    return out

def phi_inv(p):
    """The normal distribution's quantile function z_p / phi^(-1)(p)."""
    return math.sqrt(2) * erf_inv(2*p - 1)

def confidence_interval(mu, sd, n, alpha):
    """Calculates the confidence interval given the normal distribution."""
    if n == 0:
        return 0, 0
    z = phi_inv(1.0 - alpha/2.0)
    return mu - z*sd/math.sqrt(n), mu + z*sd/math.sqrt(n)
