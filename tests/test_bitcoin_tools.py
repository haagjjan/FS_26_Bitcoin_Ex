from bitcoin_tools import (
    count_inputs,
    count_outputs,
    decode_op_return_ascii,
    find_transaction_by_input_address,
    get_output,
    is_op_return_output,
    op_return_payload_hex,
    p2pkh_pubkey_hash,
    summarize_transaction,
    transaction_has_input_address,
)


P2PKH_HASH = "00112233445566778899aabbccddeeff00112233"
P2PKH_SCRIPT = f"76a914{P2PKH_HASH}88ac"
OP_RETURN_SCRIPT = "6a0b48656c6c6f20576f726c64"


def sample_transaction():
    return {
        "txid": "abc123",
        "vin": [
            {"prevout": {"scriptpubkey_address": "1CGN1zd62UakPw7neohJN8zTJUJ9LT2Ay8"}},
            {"prev_out": {"addr": "1OtherAddress"}},
        ],
        "vout": [
            {"scriptpubkey": P2PKH_SCRIPT, "scriptpubkey_type": "p2pkh", "value": 1000},
            {"scriptpubkey": OP_RETURN_SCRIPT, "scriptpubkey_type": "op_return", "value": 0},
        ],
    }


def test_transaction_counts_and_address_lookup():
    tx = sample_transaction()

    assert count_inputs(tx) == 2
    assert count_outputs(tx) == 2
    assert transaction_has_input_address(tx, "1CGN1zd62UakPw7neohJN8zTJUJ9LT2Ay8")
    assert find_transaction_by_input_address([tx], "1CGN1zd62UakPw7neohJN8zTJUJ9LT2Ay8") == tx


def test_p2pkh_pubkey_hash_extraction():
    output = get_output(sample_transaction(), 0)

    assert p2pkh_pubkey_hash(output) == P2PKH_HASH


def test_op_return_detection_and_ascii_decoding():
    output = get_output(sample_transaction(), 1)

    assert is_op_return_output(output)
    assert op_return_payload_hex(OP_RETURN_SCRIPT) == "48656c6c6f20576f726c64"
    assert decode_op_return_ascii(output) == "Hello World"


def test_transaction_summary():
    summary = summarize_transaction(sample_transaction())

    assert summary["txid"] == "abc123"
    assert summary["input_count"] == 2
    assert summary["output_count"] == 2
    assert summary["p2pkh_outputs"] == [{"index": 0, "pubKeyHash": P2PKH_HASH}]
    assert summary["op_return_outputs"][0]["ascii"] == "Hello World"
