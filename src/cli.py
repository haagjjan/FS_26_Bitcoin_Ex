"""Command line entry point for the Bitcoin exercise toolkit."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from bitcoin_tools import (
    count_inputs,
    count_outputs,
    decode_op_return_ascii,
    extract_coinbase_message,
    get_output,
    is_op_return_output,
    p2pkh_pubkey_hash,
    summarize_transaction,
    transaction_hash,
)
from number_systems import (
    binary_to_decimal,
    binary_to_hexadecimal,
    decimal_to_binary,
    hexadecimal_to_binary,
)
from rsa_tools import solve_rsa_exercise
from substitution_cipher import (
    EXERCISE_CIPHERTEXT,
    decrypt,
    exercise_solution_mapping,
    letter_frequencies,
    most_frequent_letters,
    partial_decrypt,
)
from visualizations import save_frequency_bar_chart


def _print_steps(title: str, value: object, steps: list[str]) -> None:
    print(title)
    print(f"Answer: {value}")
    print()
    print("Steps:")
    for step in steps:
        print(f"- {step}")


def _read_text_arg(args: argparse.Namespace) -> str:
    if getattr(args, "text", None):
        return args.text
    if getattr(args, "file", None):
        return Path(args.file).read_text(encoding="utf-8")
    return EXERCISE_CIPHERTEXT


def _parse_mapping(mapping_text: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    if not mapping_text.strip():
        return mapping

    for item in mapping_text.split(","):
        separator = "=" if "=" in item else ":"
        if separator not in item:
            raise ValueError("mapping entries must look like L=T,N=O")
        cipher, plain = item.split(separator, 1)
        mapping[cipher.strip()] = plain.strip()
    return mapping


def run_number(args: argparse.Namespace) -> int:
    if args.operation == "bin-to-dec":
        result = binary_to_decimal(args.value)
    elif args.operation == "dec-to-bin":
        result = decimal_to_binary(int(args.value))
    elif args.operation == "bin-to-hex":
        result = binary_to_hexadecimal(args.value)
    elif args.operation == "hex-to-bin":
        result = hexadecimal_to_binary(args.value)
    else:  # pragma: no cover - argparse prevents this
        raise ValueError(args.operation)

    _print_steps("Number System Conversion", result.value, result.steps)
    return 0


def run_rsa(args: argparse.Namespace) -> int:
    result = solve_rsa_exercise(args.p, args.q, args.e, args.message)
    _print_steps("RSA Exercise", result.decrypted_message, result.steps)
    print()
    print(f"N: {result.n}")
    print(f"phi(N): {result.phi}")
    print(f"ASCII({result.message!r}): {result.ascii_value}")
    print(f"Encrypted C: {result.ciphertext}")
    print(f"Private exponent d: {result.private_exponent}")
    return 0


def run_cipher(args: argparse.Namespace) -> int:
    text = _read_text_arg(args)

    if args.cipher_command == "frequencies":
        rows = letter_frequencies(text)
        for letter, count, percent in rows[: args.limit]:
            print(f"{letter}: {count} ({percent:.2f}%)")
        print()
        print("Most frequent:", ", ".join(row[0] for row in most_frequent_letters(text, 3)))
        if args.chart:
            path = save_frequency_bar_chart(text, args.chart)
            print(f"Saved chart to {path}")
        return 0

    if args.cipher_command == "decrypt":
        mapping = exercise_solution_mapping() if args.known_solution else _parse_mapping(args.mapping)
        if args.require_complete:
            print(decrypt(text, mapping))
        else:
            print(partial_decrypt(text, mapping, unknown=args.unknown))
        return 0

    if args.cipher_command == "exercise":
        print("Top ciphertext letters:")
        for letter, count, percent in most_frequent_letters(EXERCISE_CIPHERTEXT, args.limit):
            print(f"{letter}: {count} ({percent:.2f}%)")
        print()
        print("Known solution:")
        print(decrypt(EXERCISE_CIPHERTEXT, exercise_solution_mapping()))
        return 0

    raise ValueError(args.cipher_command)  # pragma: no cover


def _print_transaction_summary(transaction: dict) -> None:
    summary = summarize_transaction(transaction)
    print(f"Transaction hash: {summary['txid']}")
    print(f"Inputs: {summary['input_count']}")
    print(f"Outputs: {summary['output_count']}")

    if summary["p2pkh_outputs"]:
        print("P2PKH outputs:")
        for output in summary["p2pkh_outputs"]:
            print(f"- index {output['index']}: pubKeyHash {output['pubKeyHash']}")

    if summary["op_return_outputs"]:
        print("OP_RETURN outputs:")
        for output in summary["op_return_outputs"]:
            print(
                f"- index {output['index']}: {output['payload_hex']} "
                f"ASCII={output['ascii']!r}"
            )


def run_bitcoin(args: argparse.Namespace) -> int:
    if args.bitcoin_command == "inspect-json":
        transaction = json.loads(Path(args.path).read_text(encoding="utf-8"))
        _print_transaction_summary(transaction)
        if args.output_index is not None:
            output = get_output(transaction, args.output_index)
            print()
            print(f"Output {args.output_index}")
            print(f"pubKeyHash: {p2pkh_pubkey_hash(output)}")
            print(f"OP_RETURN: {is_op_return_output(output)}")
            print(f"OP_RETURN ASCII: {decode_op_return_ascii(output)}")
        return 0

    if args.bitcoin_command == "fetch":
        from bitcoin_api import BitcoinAPIError, EsploraClient

        client = EsploraClient(base_url=args.api_url, timeout=args.timeout)
        try:
            transaction = client.find_transaction_in_block(args.height, args.address)
            coinbase = client.get_coinbase_transaction(args.height)
        except BitcoinAPIError as exc:
            print(f"Bitcoin API error: {exc}", file=sys.stderr)
            return 2

        if transaction is None:
            print(f"No transaction spending from {args.address} found in block {args.height}.")
            return 1

        print(f"Found transaction in block {args.height}:")
        _print_transaction_summary(transaction)
        print()
        print(f"Coinbase transaction: {transaction_hash(coinbase)}")
        print(f"Coinbase inputs: {count_inputs(coinbase)}")
        print(f"Coinbase outputs: {count_outputs(coinbase)}")
        message = extract_coinbase_message(coinbase)
        if message:
            print(f"Coinbase message: {message!r}")
        return 0

    raise ValueError(args.bitcoin_command)  # pragma: no cover


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bitcoin lecture exercise toolkit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    number = subparsers.add_parser("number", help="Problem 1 number conversions")
    number.add_argument(
        "operation",
        choices=["bin-to-dec", "dec-to-bin", "bin-to-hex", "hex-to-bin"],
    )
    number.add_argument("value")
    number.set_defaults(func=run_number)

    rsa = subparsers.add_parser("rsa", help="Problem 3 RSA workflow")
    rsa.add_argument("--p", type=int, default=13)
    rsa.add_argument("--q", type=int, default=29)
    rsa.add_argument("--e", type=int, default=5)
    rsa.add_argument("--message", default="L")
    rsa.set_defaults(func=run_rsa)

    cipher = subparsers.add_parser("cipher", help="Problem 2 substitution cipher")
    cipher_sub = cipher.add_subparsers(dest="cipher_command", required=True)

    frequencies = cipher_sub.add_parser("frequencies", help="show letter frequencies")
    frequencies.add_argument("--text")
    frequencies.add_argument("--file")
    frequencies.add_argument("--limit", type=int, default=26)
    frequencies.add_argument("--chart", default="")
    frequencies.set_defaults(func=run_cipher)

    cipher_decrypt = cipher_sub.add_parser("decrypt", help="decrypt with a manual mapping")
    cipher_decrypt.add_argument("--text")
    cipher_decrypt.add_argument("--file")
    cipher_decrypt.add_argument("--mapping", default="")
    cipher_decrypt.add_argument("--unknown", default="_")
    cipher_decrypt.add_argument("--known-solution", action="store_true")
    cipher_decrypt.add_argument("--require-complete", action="store_true")
    cipher_decrypt.set_defaults(func=run_cipher)

    exercise = cipher_sub.add_parser("exercise", help="run the Problem 2 sample workflow")
    exercise.add_argument("--limit", type=int, default=3)
    exercise.set_defaults(func=run_cipher)

    bitcoin = subparsers.add_parser("bitcoin", help="Problem 4 transaction tools")
    bitcoin_sub = bitcoin.add_subparsers(dest="bitcoin_command", required=True)

    inspect_json = bitcoin_sub.add_parser("inspect-json", help="inspect pasted tx JSON")
    inspect_json.add_argument("path")
    inspect_json.add_argument("--output-index", type=int)
    inspect_json.set_defaults(func=run_bitcoin)

    fetch = bitcoin_sub.add_parser("fetch", help="fetch block transaction data")
    fetch.add_argument("--height", type=int, required=True)
    fetch.add_argument("--address", required=True)
    fetch.add_argument("--api-url", default="https://blockstream.info/api")
    fetch.add_argument("--timeout", type=int, default=15)
    fetch.set_defaults(func=run_bitcoin)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
