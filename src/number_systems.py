"""Number system conversion helpers for Problem 1."""

from dataclasses import dataclass
from typing import Union


@dataclass
class ConversionResult:
    """A conversion answer together with learning-friendly steps."""

    value: Union[int, str]
    steps: list[str]

    def explanation(self) -> str:
        """Return the steps as a printable multi-line explanation."""
        return "\n".join(self.steps)


def _clean_binary(binary: str) -> str:
    cleaned = binary.strip().replace(" ", "").replace("_", "")
    if not cleaned or any(char not in "01" for char in cleaned):
        raise ValueError("binary input must contain only 0 and 1")
    return cleaned


def _clean_hex(hex_value: str) -> str:
    cleaned = hex_value.strip().replace(" ", "").replace("_", "")
    if not cleaned or any(char not in "0123456789abcdefABCDEF" for char in cleaned):
        raise ValueError("hexadecimal input must contain only 0-9 and A-F")
    return cleaned.upper()


def binary_to_decimal(binary: str) -> ConversionResult:
    """Convert a binary string to decimal and show powers of 2."""
    bits = _clean_binary(binary)
    steps = [f"Convert binary {bits} to decimal using powers of 2:"]
    total = 0

    for index, bit in enumerate(bits):
        power = len(bits) - index - 1
        contribution = int(bit) * (2**power)
        total += contribution
        steps.append(f"{bit} * 2^{power} = {contribution}")

    steps.append(f"Sum = {total}")
    return ConversionResult(total, steps)


def decimal_to_binary(number: int) -> ConversionResult:
    """Convert a non-negative decimal integer to binary using division by 2."""
    if number < 0:
        raise ValueError("decimal input must be non-negative")
    if number == 0:
        return ConversionResult("0", ["0 in decimal is 0 in binary."])

    steps = [f"Convert decimal {number} to binary by repeated division by 2:"]
    remainders: list[str] = []
    current = number

    while current > 0:
        quotient, remainder = divmod(current, 2)
        steps.append(f"{current} / 2 = {quotient} remainder {remainder}")
        remainders.append(str(remainder))
        current = quotient

    binary = "".join(reversed(remainders))
    steps.append(f"Read the remainders from bottom to top: {binary}")
    return ConversionResult(binary, steps)


def binary_to_hexadecimal(binary: str) -> ConversionResult:
    """Convert binary to hexadecimal by grouping bits into 4-bit nibbles."""
    bits = _clean_binary(binary)
    padding = (-len(bits)) % 4
    padded = ("0" * padding) + bits
    groups = [padded[index : index + 4] for index in range(0, len(padded), 4)]

    steps = [f"Convert binary {bits} to hexadecimal using 4-bit groups:"]
    if padding:
        steps.append(f"Pad on the left with {padding} zero(s): {padded}")

    hex_digits: list[str] = []
    for group in groups:
        digit = format(int(group, 2), "X")
        hex_digits.append(digit)
        steps.append(f"{group} = {digit}")

    value = "".join(hex_digits)
    steps.append(f"Hexadecimal result = {value}")
    return ConversionResult(value, steps)


def hexadecimal_to_binary(hex_value: str) -> ConversionResult:
    """Convert hexadecimal to binary, preserving 4 bits for each hex digit."""
    digits = _clean_hex(hex_value)
    steps = [f"Convert hexadecimal {digits} to binary using 4-bit groups:"]
    groups: list[str] = []

    for digit in digits:
        group = format(int(digit, 16), "04b")
        groups.append(group)
        steps.append(f"{digit} = {group}")

    value = "".join(groups)
    steps.append(f"Binary result = {value}")
    return ConversionResult(value, steps)
