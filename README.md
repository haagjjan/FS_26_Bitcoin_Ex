# Bitcoin Blockchain Exercises

Reusable Python toolkit for the Bitcoin and Blockchain lecture exercises.

The original problem sheet is stored in `docs/Problem Set 2026-1.pdf`.
The Markdown files in `exercises/` are the source of truth for the tasks.

## Python version
Requires Python 3.10+

## Structure

- `docs/`: local reference material
- `exercises/`: extracted problem statements
- `src/`: solution code
- `tests/`: tests for the solutions
- `outputs/`: generated charts or exported output files

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run tests:

```bash
PYTHONPATH=src pytest
```

## Exercise Mapping
| Problem | Topic | CLI command |
|---|---|---|
| 1 | Number systems | `cli number ...` |
| 2 | Substitution cipher | `cli cipher ...` |
| 3 | RSA | `cli rsa ...` |
| 4 | Bitcoin transaction data | `cli bitcoin ...` |

## CLI Examples

Problem 1, number systems:

```bash
PYTHONPATH=src python -m cli number bin-to-dec 10010110
PYTHONPATH=src python -m cli number dec-to-bin 77
PYTHONPATH=src python -m cli number bin-to-hex 11011001
PYTHONPATH=src python -m cli number hex-to-bin 4d7a
```

Problem 2, substitution cipher:

```bash
PYTHONPATH=src python -m cli cipher frequencies --limit 5
PYTHONPATH=src python -m cli cipher frequencies --chart outputs/cipher_frequencies.png
PYTHONPATH=src python -m cli cipher decrypt --mapping "L=T,N=O,C=K"
PYTHONPATH=src python -m cli cipher exercise
```

Unknown letters in partial decryptions are shown as `_`. The mapping format is
`cipher=plain`, separated by commas.

Problem 3, RSA:

```bash
PYTHONPATH=src python -m cli rsa --p 13 --q 29 --e 5 --message L
```

Problem 4, Bitcoin transaction data:

```bash
PYTHONPATH=src python -m cli bitcoin fetch \
  --height 325001 \
  --address 1CGN1zd62UakPw7neohJN8zTJUJ9LT2Ay8
```

The online command uses the Blockstream Esplora API:
<https://github.com/blockstream/esplora/blob/master/API.md>

Public APIs can be unavailable or rate limited. If the network call fails, paste
raw transaction JSON from a block explorer into a local file and inspect it
offline:

```bash
PYTHONPATH=src python -m cli bitcoin inspect-json path/to/transaction.json --output-index 4
```

The offline parser can count inputs/outputs, inspect standard P2PKH outputs,
extract `pubKeyHash`, detect OP_RETURN outputs, and decode readable OP_RETURN
payloads.


## Troubleshooting:
Common Issues might be fixed with:
- export PYTHONPATH=src
- or test wether pytest is missing