from typing import Union

from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.bech32m import decode_puzzle_hash, encode_puzzle_hash
from chia.wallet.puzzles.cat_loader import CAT_MOD


def get_tail_wrapped_puzhash(xch_puzhash: Union[str, bytes32], tail: Union[str, bytes32]) -> bytes32:
    """
    Returns the tail-wrapped puzzle hash for a given XCH puzzle hash
    """
    if not isinstance(tail, bytes):
        tail = bytes.fromhex(tail)
    if not isinstance(xch_puzhash, bytes):
        xch_puzhash = bytes.fromhex(xch_puzhash)

    return CAT_MOD.curry(
        CAT_MOD.get_tree_hash(), tail, xch_puzhash
    ).get_tree_hash(xch_puzhash)


def get_tail_wrapped_address(xch_address: str, tail: str, prefix: str = "xch") -> str:
    """
    Returns the tail-wrapped address for a given XCH address
    """
    xch_puzhash = decode_puzzle_hash(xch_address)
    return encode_puzzle_hash(get_tail_wrapped_puzhash(xch_puzhash, tail), prefix)
