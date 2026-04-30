from rsa_tools import (
    ascii_to_char,
    char_to_ascii,
    compute_n,
    compute_phi,
    decrypt,
    encrypt,
    extended_gcd,
    modular_inverse,
    solve_rsa_exercise,
)


def test_problem_3_known_results():
    result = solve_rsa_exercise(p=13, q=29, e=5, message="L")

    assert result.ascii_value == 76
    assert result.n == 377
    assert result.phi == 336
    assert result.ciphertext == 189
    assert result.private_exponent == 269
    assert result.decrypted_message == "L"


def test_rsa_individual_helpers():
    n = compute_n(13, 29)
    phi = compute_phi(13, 29)
    message = char_to_ascii("L")
    ciphertext = encrypt(message, 5, n)
    d = modular_inverse(5, phi)

    assert n == 377
    assert phi == 336
    assert message == 76
    assert ciphertext == 189
    assert d == 269
    assert ascii_to_char(decrypt(ciphertext, d, n)) == "L"


def test_extended_gcd_coefficients():
    result = extended_gcd(5, 336)

    assert result.gcd == 1
    assert 5 * result.x + 336 * result.y == 1
