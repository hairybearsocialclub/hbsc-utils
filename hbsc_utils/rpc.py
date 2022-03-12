import os
from pathlib import Path
from typing import Tuple, Optional

from chia.rpc.full_node_rpc_client import FullNodeRpcClient
from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.types.coin_record import CoinRecord
from chia.types.coin_spend import CoinSpend
from chia.util.bech32m import encode_puzzle_hash
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.ints import uint16

from .cat import get_tail_wrapped_puzhash, get_tail_wrapped_address
from .spends import extract_payments_from_program



class ChiaWrapperException(Exception):
    pass


class SpendNotFoundException(ChiaWrapperException):
    pass


class ChiaWalletWrapper:
    """
    Chia wallet RPC wrapper as a context manager.
    When instantiated, returns both the underlying RPC client and itself, allowing for additional features.
    """

    _client: "WalletRpcClient"

    def __init__(
        self,
        *,
        hostname: str = os.getenv("CHIA_WALLET_HOSTNAME", "127.0.0.1"),
        port: int = int(os.getenv("CHIA_WALLET_PORT", "9256")),
        root_path: Path = DEFAULT_ROOT_PATH,
    ):
        self.hostname = hostname
        self.port = port
        self.root_path = root_path
        self.config = load_config(root_path, "config.yaml")

    async def __aenter__(self) -> Tuple["ChiaWalletWrapper", WalletRpcClient]:
        self._client = await WalletRpcClient.create(
            self.hostname, uint16(self.port), self.root_path, self.config
        )
        return self, self._client

    async def __aexit__(self, *args):
        await self._client.session.close()


class ChiaFullNodeWrapper:
    """
    Chia full node RPC wrapper as a context manager.
    When instantiated, returns both the underlying RPC client and itself, allowing for additional features.
    """

    _client: "FullNodeRpcClient"

    def __init__(
        self,
        *,
        hostname: str = os.getenv("CHIA_FULL_NODE_HOSTNAME", "127.0.0.1"),
        port: int = int(os.getenv("CHIA_FULL_NODE_PORT", "8555")),
        root_path: Path = DEFAULT_ROOT_PATH,
    ):
        self.hostname = hostname
        self.port = port
        self.root_path = root_path
        self.config = load_config(root_path, "config.yaml")

    async def __aenter__(self) -> Tuple["ChiaFullNodeWrapper", "FullNodeRpcClient"]:
        self._client = await FullNodeRpcClient.create(
            self.hostname, uint16(self.port), self.root_path, self.config
        )
        return self, self._client

    async def __aexit__(self, *args):
        await self._client.session.close()

    async def _get_spend(self, record: CoinRecord) -> CoinSpend:
        if not (
            spend := await self._client.get_puzzle_and_solution(
                record.coin.parent_coin_info, record.confirmed_block_index
            )
        ):
            raise SpendNotFoundException(
                f"Could not find spend for coin {record.name}."
            )

        return spend

    async def get_original_address_for_cat(
        self, record: CoinRecord, tail: str
    ) -> Optional[str]:
        """
        Tries to get original XCH send address from CAT coin.
        """
        spend = await self._get_spend(record)
        program = spend.solution.to_program()

        try:
            # offer?
            # TODO test with an offer with multiple outputs
            possible_puzhash = program.at("ffrff").as_python()
            if get_tail_wrapped_puzhash(possible_puzhash, tail) == record.coin.puzzle_hash:
                return encode_puzzle_hash(possible_puzhash, "xch")
        except:
            # normal spend?
            inner_solution = program.at("frfr")
            payments = extract_payments_from_program(inner_solution)
            for p in payments:
                if get_tail_wrapped_puzhash(p.puzzle_hash, tail) == record.coin.puzzle_hash:
                    return encode_puzzle_hash(p.puzzle_hash, "xch")
