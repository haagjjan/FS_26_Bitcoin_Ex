from substitution_cipher import (
    EXERCISE_CIPHERTEXT,
    decrypt,
    exercise_solution_mapping,
    letter_counts,
    most_frequent_letters,
    partial_decrypt,
)


def test_letter_counts_ignore_punctuation_and_case():
    counts = letter_counts("ABBA! cab")

    assert counts["A"] == 3
    assert counts["B"] == 3
    assert counts["C"] == 1


def test_most_frequent_letters_for_exercise_ciphertext():
    top_letters = [row[0] for row in most_frequent_letters(EXERCISE_CIPHERTEXT, 3)]

    assert top_letters == ["P", "L", "B"]


def test_partial_decrypt_shows_unknown_letters():
    plaintext = partial_decrypt("LNCPF", {"L": "T", "N": "O"}, unknown="_")

    assert plaintext == "TO___"


def test_exercise_solution_mapping_decrypts_ciphertext():
    plaintext = decrypt(EXERCISE_CIPHERTEXT, exercise_solution_mapping())

    assert plaintext.startswith("TOKENIZATION, BLOCKCHAIN, AND SMART CONTRACTS")
    normalized = " ".join(plaintext.split())
    assert "THE COURSE IS OFFERED AS A TWO WEEK BLOCK SEMINAR" in normalized
