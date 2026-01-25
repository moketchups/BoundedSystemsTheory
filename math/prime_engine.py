"""
Prime Verification Engine - Step 1.1
Mathematical Basis: Axiom 1 - primes as irreducible atoms
"""


def is_prime(n: int) -> bool:
    """
    Determine if n is a prime number.

    Axiom 1: Primes are informational atoms - irreducible units.
    A prime has exactly two divisors: 1 and itself.

    Returns True if n is prime, False otherwise.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    # Check odd divisors up to sqrt(n)
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2

    return True
