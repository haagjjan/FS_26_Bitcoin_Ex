"""Offline Bitcoin transaction and script helpers for Problem 4."""

import binascii
from typing import Any, Optional


P2PKH_PREFIX = "76a914"
P2PKH_SUFFIX = "88ac"


def transaction_hash(transaction: dict[str, Any]) -> str:
    """Return the transaction hash from common explorer JSON formats."""
    txid = transaction.get("txid") or transaction.get("hash")
    if not txid:
        raise ValueError("transaction JSON does not contain a txid/hash")
    return str(txid)


def count_inputs(transaction: dict[str, Any]) -> int:
    """Count transaction inputs."""
    return len(transaction.get("vin", transaction.get("inputs", [])))


def count_outputs(transaction: dict[str, Any]) -> int:
    """Count transaction outputs."""
    return len(transaction.get("vout", transaction.get("out", [])))


def get_outputs(transaction: dict[str, Any]) -> list[dict[str, Any]]:
    """Return outputs from common explorer JSON formats."""
    return list(transaction.get("vout", transaction.get("out", [])))


def get_inputs(transaction: dict[str, Any]) -> list[dict[str, Any]]:
    """Return inputs from common explorer JSON formats."""
    return list(transaction.get("vin", transaction.get("inputs", [])))


def get_output(transaction: dict[str, Any], index: int) -> dict[str, Any]:
    """Return one output by zero-based index."""
    outputs = get_outputs(transaction)
    if index < 0 or index >= len(outputs):
        raise IndexError(f"output index {index} is out of range")
    return outputs[index]


def output_script_hex(output: dict[str, Any]) -> str:
    """Extract scriptPubKey hex from common output JSON shapes."""
    if "scriptpubkey" in output:
        return str(output["scriptpubkey"]).lower()
    if "script" in output:
        return str(output["script"]).lower()
    script_pub_key = output.get("scriptPubKey")
    if isinstance(script_pub_key, dict) and "hex" in script_pub_key:
        return str(script_pub_key["hex"]).lower()
    return ""


def output_script_asm(output: dict[str, Any]) -> str:
    """Extract scriptPubKey assembly from common output JSON shapes."""
    if "scriptpubkey_asm" in output:
        return str(output["scriptpubkey_asm"])
    script_pub_key = output.get("scriptPubKey")
    if isinstance(script_pub_key, dict) and "asm" in script_pub_key:
        return str(script_pub_key["asm"])
    return ""


def p2pkh_pubkey_hash_from_script(script_hex: str) -> Optional[str]:
    """Extract the pubKeyHash from a standard P2PKH scriptPubKey."""
    cleaned = script_hex.lower()
    expected_length = len(P2PKH_PREFIX) + 40 + len(P2PKH_SUFFIX)
    if (
        len(cleaned) == expected_length
        and cleaned.startswith(P2PKH_PREFIX)
        and cleaned.endswith(P2PKH_SUFFIX)
    ):
        return cleaned[len(P2PKH_PREFIX) : -len(P2PKH_SUFFIX)]
    return None


def p2pkh_pubkey_hash(output: dict[str, Any]) -> Optional[str]:
    """Extract a P2PKH pubKeyHash from an output when possible."""
    script_hash = p2pkh_pubkey_hash_from_script(output_script_hex(output))
    if script_hash:
        return script_hash

    asm_parts = output_script_asm(output).split()
    if len(asm_parts) >= 5 and asm_parts[0] == "OP_DUP" and asm_parts[1] == "OP_HASH160":
        candidate = asm_parts[-3]
        if len(candidate) == 40 and all(char in "0123456789abcdefABCDEF" for char in candidate):
            return candidate.lower()
    return None


def is_op_return_output(output: dict[str, Any]) -> bool:
    """Detect OP_RETURN/nulldata outputs."""
    output_type = str(
        output.get("scriptpubkey_type")
        or output.get("type")
        or output.get("scriptPubKey", {}).get("type", "")
    ).lower()
    script_hex = output_script_hex(output)
    script_asm = output_script_asm(output).upper()
    return (
        output_type in {"op_return", "nulldata"}
        or script_hex.startswith("6a")
        or script_asm.startswith("OP_RETURN")
    )


def op_return_payload_hex(script_hex: str) -> str:
    """Extract pushed data from a simple OP_RETURN script hex."""
    cleaned = script_hex.lower()
    if not cleaned.startswith("6a"):
        return ""

    data = bytes.fromhex(cleaned)
    index = 1
    chunks: list[bytes] = []

    while index < len(data):
        opcode = data[index]
        index += 1

        if opcode == 0:
            continue
        if 1 <= opcode <= 75:
            length = opcode
        elif opcode == 76 and index < len(data):  # OP_PUSHDATA1
            length = data[index]
            index += 1
        elif opcode == 77 and index + 1 < len(data):  # OP_PUSHDATA2
            length = int.from_bytes(data[index : index + 2], "little")
            index += 2
        elif opcode == 78 and index + 3 < len(data):  # OP_PUSHDATA4
            length = int.from_bytes(data[index : index + 4], "little")
            index += 4
        else:
            # Unknown opcode after OP_RETURN; stop instead of guessing.
            break

        chunks.append(data[index : index + length])
        index += length

    return b"".join(chunks).hex()


def decode_op_return_ascii(output: dict[str, Any]) -> Optional[str]:
    """Decode an OP_RETURN payload as readable text when possible."""
    script_hex = output_script_hex(output)
    if not script_hex.startswith("6a"):
        return None

    payload = op_return_payload_hex(script_hex)
    if not payload:
        return ""

    try:
        return bytes.fromhex(payload).decode("utf-8", errors="replace")
    except (ValueError, binascii.Error):
        return None


def _input_addresses(transaction_input: dict[str, Any]) -> list[str]:
    addresses: list[str] = []

    prevout = transaction_input.get("prevout")
    if isinstance(prevout, dict) and prevout.get("scriptpubkey_address"):
        addresses.append(str(prevout["scriptpubkey_address"]))

    prev_out = transaction_input.get("prev_out")
    if isinstance(prev_out, dict) and prev_out.get("addr"):
        addresses.append(str(prev_out["addr"]))

    if transaction_input.get("address"):
        addresses.append(str(transaction_input["address"]))
    if transaction_input.get("addr"):
        addresses.append(str(transaction_input["addr"]))

    return addresses


def transaction_has_input_address(transaction: dict[str, Any], address: str) -> bool:
    """Return True if any input spends coins from address."""
    return any(address in _input_addresses(tx_input) for tx_input in get_inputs(transaction))


def find_transaction_by_input_address(
    transactions: list[dict[str, Any]], address: str
) -> Optional[dict[str, Any]]:
    """Find the first transaction whose inputs contain address."""
    for transaction in transactions:
        if transaction_has_input_address(transaction, address):
            return transaction
    return None


def extract_coinbase_message(transaction: dict[str, Any]) -> str:
    """Decode the coinbase input script as best-effort text."""
    inputs = get_inputs(transaction)
    if not inputs:
        return ""

    first_input = inputs[0]
    script_hex = str(first_input.get("scriptsig") or first_input.get("script", ""))
    if not script_hex:
        return ""
    try:
        return bytes.fromhex(script_hex).decode("utf-8", errors="replace")
    except (ValueError, binascii.Error):
        return script_hex


def summarize_transaction(transaction: dict[str, Any]) -> dict[str, Any]:
    """Return a compact summary of transaction inputs, outputs, and scripts."""
    outputs = get_outputs(transaction)
    p2pkh_outputs = []
    op_return_outputs = []

    for index, output in enumerate(outputs):
        pubkey_hash = p2pkh_pubkey_hash(output)
        if pubkey_hash:
            p2pkh_outputs.append({"index": index, "pubKeyHash": pubkey_hash})

        if is_op_return_output(output):
            op_return_outputs.append(
                {
                    "index": index,
                    "payload_hex": op_return_payload_hex(output_script_hex(output)),
                    "ascii": decode_op_return_ascii(output),
                }
            )

    return {
        "txid": transaction_hash(transaction),
        "input_count": count_inputs(transaction),
        "output_count": count_outputs(transaction),
        "p2pkh_outputs": p2pkh_outputs,
        "op_return_outputs": op_return_outputs,
    }
