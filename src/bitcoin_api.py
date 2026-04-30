"""Online Bitcoin block explorer access for Problem 4.

This module uses the Esplora HTTP API exposed by Blockstream. Keep these calls
separate from bitcoin_tools.py so offline parsing can be tested without network
access.
"""

from typing import Any, Iterator, Optional

try:
    import requests
except ImportError:  # pragma: no cover - exercised only when dependency is absent
    requests = None

from bitcoin_tools import find_transaction_by_input_address


class BitcoinAPIError(RuntimeError):
    """Raised when a block explorer request cannot be completed."""


class EsploraClient:
    """Small client for the Blockstream Esplora HTTP API."""

    def __init__(self, base_url: str = "https://blockstream.info/api", timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _require_requests(self) -> None:
        if requests is None:
            raise BitcoinAPIError("requests is not installed; run pip install -r requirements.txt")

    def _get(self, path: str):
        self._require_requests()
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            raise BitcoinAPIError(f"failed to fetch {url}: {exc}") from exc

    def _get_json(self, path: str) -> Any:
        response = self._get(path)
        try:
            return response.json()
        except ValueError as exc:
            raise BitcoinAPIError(f"API response for {response.url} was not valid JSON") from exc

    def _get_text(self, path: str) -> str:
        return self._get(path).text.strip()

    def get_block_hash(self, height: int) -> str:
        """Return the block hash at a given height."""
        return self._get_text(f"block-height/{height}")

    def get_block(self, block_hash: str) -> dict[str, Any]:
        """Return block metadata."""
        return self._get_json(f"block/{block_hash}")

    def get_transaction(self, txid: str) -> dict[str, Any]:
        """Return one transaction by txid."""
        return self._get_json(f"tx/{txid}")

    def get_block_transactions(
        self, block_hash: str, start_index: int = 0
    ) -> list[dict[str, Any]]:
        """Return up to 25 transactions from a block page."""
        if start_index == 0:
            return self._get_json(f"block/{block_hash}/txs")
        return self._get_json(f"block/{block_hash}/txs/{start_index}")

    def iter_block_transactions(self, height: int) -> Iterator[dict[str, Any]]:
        """Yield all transactions in a block using 25-transaction pages."""
        block_hash = self.get_block_hash(height)
        block = self.get_block(block_hash)
        tx_count = int(block.get("tx_count", 0))

        for start_index in range(0, tx_count, 25):
            for transaction in self.get_block_transactions(block_hash, start_index):
                yield transaction

    def find_transaction_in_block(
        self, height: int, address: str
    ) -> Optional[dict[str, Any]]:
        """Find a transaction in a block whose input spends from address."""
        return find_transaction_by_input_address(list(self.iter_block_transactions(height)), address)

    def get_coinbase_transaction(self, height: int) -> dict[str, Any]:
        """Return the first transaction in a block, which is the coinbase transaction."""
        block_hash = self.get_block_hash(height)
        transactions = self.get_block_transactions(block_hash, 0)
        if not transactions:
            raise BitcoinAPIError(f"block {height} did not return any transactions")
        return transactions[0]
