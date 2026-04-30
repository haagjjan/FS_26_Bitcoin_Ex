from number_systems import (
    binary_to_decimal,
    binary_to_hexadecimal,
    decimal_to_binary,
    hexadecimal_to_binary,
)


def test_problem_1_known_results():
    assert binary_to_decimal("10010110").value == 150
    assert decimal_to_binary(77).value == "1001101"
    assert binary_to_hexadecimal("11011001").value == "D9"
    assert hexadecimal_to_binary("4d7a").value == "0100110101111010"


def test_binary_to_decimal_explains_powers_of_two():
    result = binary_to_decimal("1010")

    assert result.value == 10
    assert "1 * 2^3 = 8" in result.steps
    assert "1 * 2^1 = 2" in result.steps


def test_decimal_to_binary_explains_division():
    result = decimal_to_binary(13)

    assert result.value == "1101"
    assert "13 / 2 = 6 remainder 1" in result.steps


def test_binary_to_hex_groups_nibbles():
    result = binary_to_hexadecimal("101")

    assert result.value == "5"
    assert "Pad on the left with 1 zero(s): 0101" in result.steps
    assert "0101 = 5" in result.steps
