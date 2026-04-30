"""Monoalphabetic substitution cipher helpers for Problem 2."""

from collections import Counter
from typing import Iterable


EXERCISE_CIPHERTEXT = """LNCPFUVBLUNF, YKNZCZSBUF, BFQ XHBWL ZNFLWBZLX BWP LPWHX
LSBL POPWTNFP UX QUXZIXXUFM. LSP ZPFLPW GNW UFFNOBLUOP
GUFBFZP BL LSP IFUOPWXULT NG YBXPK NGGPWX LSP IFUAIP ZSBFZP
LN ZNFOPWL LSPNWPLUZBK CFNEKPQMP BFQ UFFNOBLUOP UQPBX
UFLN JWBZLUZBK BJJKUZBLUNFX UF LSP BWPB NG YKNZCZSBUFX EULS
LSP YKNZCZSBUF ZSBKKPFMP. BZZNHJBFUPQ YT PRJPWLX BFQ
ZNBZSPX, LSP XLIQPFLX MN LSWNIMS LSP HNXL UHJNWLBFL XLPJX
UF ZWPBLUFM B XNKILUNF ZNFZPJL, UFZKIQUFM LPZSFUZBK
JWNLNLTJPX. LSP ZNIWXP UX NGGPWPQ BX B LEN EPPC YKNZC
XPHUFBW, LBCUFM JKBZP YPGNWP LSP XLBWL NG LSP GBKK XPHPXLPW."""


EXERCISE_PLAINTEXT = """TOKENIZATION, BLOCKCHAIN, AND SMART CONTRACTS ARE TERMS
THAT EVERYONE IS DISCUSSING. THE CENTER FOR INNOVATIVE
FINANCE AT THE UNIVERSITY OF BASEL OFFERS THE UNIQUE CHANCE
TO CONVERT THEORETICAL KNOWLEDGE AND INNOVATIVE IDEAS
INTO PRACTICAL APPLICATIONS IN THE AREA OF BLOCKCHAINS WITH
THE BLOCKCHAIN CHALLENGE. ACCOMPANIED BY EXPERTS AND
COACHES, THE STUDENTS GO THROUGH THE MOST IMPORTANT STEPS
IN CREATING A SOLUTION CONCEPT, INCLUDING TECHNICAL
PROTOTYPES. THE COURSE IS OFFERED AS A TWO WEEK BLOCK
SEMINAR, TAKING PLACE BEFORE THE START OF THE FALL SEMESTER."""


def only_letters(text: str) -> list[str]:
    """Return uppercase alphabetic characters from text."""
    return [char.upper() for char in text if char.isalpha()]


def letter_counts(text: str) -> Counter:
    """Count letters in text, ignoring spaces, numbers, and punctuation."""
    return Counter(only_letters(text))


def letter_frequencies(text: str) -> list[tuple[str, int, float]]:
    """Return letter frequencies sorted by count descending, then letter."""
    counts = letter_counts(text)
    total = sum(counts.values())
    if total == 0:
        return []

    rows = []
    for letter, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        rows.append((letter, count, count / total * 100))
    return rows


def most_frequent_letters(text: str, limit: int = 3) -> list[tuple[str, int, float]]:
    """Return the most frequent ciphertext letters."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    return letter_frequencies(text)[:limit]


def normalize_mapping(mapping: dict[str, str]) -> dict[str, str]:
    """Normalize a ciphertext-to-plaintext mapping to uppercase letters."""
    normalized: dict[str, str] = {}
    used_plain_letters: dict[str, str] = {}

    for cipher, plain in mapping.items():
        cipher_letter = cipher.strip().upper()
        plain_letter = plain.strip().upper()
        if len(cipher_letter) != 1 or not cipher_letter.isalpha():
            raise ValueError(f"invalid cipher letter: {cipher!r}")
        if len(plain_letter) != 1 or not plain_letter.isalpha():
            raise ValueError(f"invalid plain letter: {plain!r}")
        if cipher_letter in normalized and normalized[cipher_letter] != plain_letter:
            raise ValueError(f"conflicting mapping for {cipher_letter}")
        if plain_letter in used_plain_letters and used_plain_letters[plain_letter] != cipher_letter:
            raise ValueError(f"plain letter {plain_letter} is mapped from multiple letters")
        normalized[cipher_letter] = plain_letter
        used_plain_letters[plain_letter] = cipher_letter

    return normalized


def mapping_from_pairs(pairs: Iterable[tuple[str, str]]) -> dict[str, str]:
    """Build a ciphertext-to-plaintext mapping from letter pairs."""
    return normalize_mapping(dict(pairs))


def mapping_from_plaintext(ciphertext: str, plaintext: str) -> dict[str, str]:
    """Derive a mapping by aligning ciphertext and plaintext letters."""
    cipher_letters = only_letters(ciphertext)
    plain_letters = only_letters(plaintext)
    if len(cipher_letters) != len(plain_letters):
        raise ValueError("ciphertext and plaintext contain different numbers of letters")

    mapping: dict[str, str] = {}
    for cipher, plain in zip(cipher_letters, plain_letters):
        existing = mapping.get(cipher)
        if existing is not None and existing != plain:
            raise ValueError(f"conflicting plaintext for cipher letter {cipher}")
        mapping[cipher] = plain
    return normalize_mapping(mapping)


def partial_decrypt(text: str, mapping: dict[str, str], unknown: str = "_") -> str:
    """Decrypt text with a partial mapping, showing unknown letters clearly."""
    normalized = normalize_mapping(mapping)
    output: list[str] = []

    for char in text:
        if not char.isalpha():
            output.append(char)
            continue

        plain = normalized.get(char.upper())
        if plain is None:
            output.append(unknown)
        elif char.isupper():
            output.append(plain)
        else:
            output.append(plain.lower())

    return "".join(output)


def decrypt(text: str, mapping: dict[str, str]) -> str:
    """Decrypt text and fail if any ciphertext letter is still unknown."""
    normalized = normalize_mapping(mapping)
    missing = sorted(set(only_letters(text)) - set(normalized))
    if missing:
        raise ValueError(f"missing mappings for: {', '.join(missing)}")
    return partial_decrypt(text, normalized)


def exercise_solution_mapping() -> dict[str, str]:
    """Return the known ciphertext-to-plaintext mapping for Problem 2."""
    return mapping_from_plaintext(EXERCISE_CIPHERTEXT, EXERCISE_PLAINTEXT)
