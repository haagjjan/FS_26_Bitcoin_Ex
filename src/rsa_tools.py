"""Small RSA helpers for Problem 3."""

from dataclasses import dataclass


@dataclass
class ExtendedGcdResult:
    """Result of the extended Euclidean algorithm."""

    gcd: int
    x: int
    y: int
    steps: list[str]


@dataclass
class RsaExerciseResult:
    """All important values for the RSA exercise workflow."""

    p: int
    q: int
    e: int
    message: str
    ascii_value: int
    n: int
    phi: int
    ciphertext: int
    private_exponent: int
    decrypted_ascii: int
    decrypted_message: str
    steps: list[str]


def compute_n(p: int, q: int) -> int:
    """Compute the RSA modulus N = p * q."""
    return p * q


def compute_phi(p: int, q: int) -> int:
    """Compute phi(N) for two prime factors p and q."""
    return (p - 1) * (q - 1)


def char_to_ascii(message: str) -> int:
    """Convert a one-character message to its ASCII decimal value."""
    if len(message) != 1:
        raise ValueError("this exercise helper expects exactly one character")
    return ord(message)


def ascii_to_char(value: int) -> str:
    """Convert an ASCII decimal value back to a character."""
    if value < 0 or value > 127:
        raise ValueError("ASCII value must be between 0 and 127")
    return chr(value)


def encrypt(message_number: int, e: int, n: int) -> int:
    """Encrypt with C = M^e mod N."""
    return pow(message_number, e, n)


def decrypt(ciphertext: int, d: int, n: int) -> int:
    """Decrypt with M = C^d mod N."""
    return pow(ciphertext, d, n)


def extended_gcd(a: int, b: int) -> ExtendedGcdResult:
    """Run the extended Euclidean algorithm.

    The returned coefficients satisfy: a * x + b * y = gcd(a, b).
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    steps = [f"Start with r0={old_r}, r1={r}"]

    while r != 0:
        quotient = old_r // r
        steps.append(f"{old_r} = {quotient} * {r} + {old_r - quotient * r}")
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    steps.append(f"gcd({a}, {b}) = {old_r}")
    steps.append(f"{a} * {old_s} + {b} * {old_t} = {old_r}")
    return ExtendedGcdResult(old_r, old_s, old_t, steps)


def modular_inverse(value: int, modulus: int) -> int:
    """Return the multiplicative inverse of value modulo modulus."""
    result = extended_gcd(value, modulus)
    if result.gcd != 1:
        raise ValueError(f"{value} has no inverse modulo {modulus}")
    return result.x % modulus


def private_exponent(e: int, phi: int) -> int:
    """Compute the RSA private exponent d."""
    return modular_inverse(e, phi)


def solve_rsa_exercise(p: int, q: int, e: int, message: str) -> RsaExerciseResult:
    """Run the full RSA workflow used in Problem 3."""
    n = compute_n(p, q)
    phi = compute_phi(p, q)
    ascii_value = char_to_ascii(message)
    ciphertext = encrypt(ascii_value, e, n)
    d = private_exponent(e, phi)
    decrypted_ascii = decrypt(ciphertext, d, n)
    decrypted_message = ascii_to_char(decrypted_ascii)

    steps = [
        f"N = p * q = {p} * {q} = {n}",
        f"phi(N) = (p - 1)(q - 1) = {p - 1} * {q - 1} = {phi}",
        f"ASCII({message!r}) = {ascii_value}",
        f"C = M^e mod N = {ascii_value}^{e} mod {n} = {ciphertext}",
        f"d = inverse of {e} modulo {phi} = {d}",
        f"M = C^d mod N = {ciphertext}^{d} mod {n} = {decrypted_ascii}",
        f"ASCII({decrypted_ascii}) = {decrypted_message!r}",
    ]
    return RsaExerciseResult(
        p=p,
        q=q,
        e=e,
        message=message,
        ascii_value=ascii_value,
        n=n,
        phi=phi,
        ciphertext=ciphertext,
        private_exponent=d,
        decrypted_ascii=decrypted_ascii,
        decrypted_message=decrypted_message,
        steps=steps,
    )
