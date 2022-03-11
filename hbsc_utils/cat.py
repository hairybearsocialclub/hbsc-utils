from chia.util.bech32m import decode_puzzle_hash, encode_puzzle_hash
from chia.wallet.puzzles.cat_loader import CAT_MOD


def get_tail_wrapped_puzhash(xch_address: str, tail: str):
    """
    Returns the tail-wrapped puzzle hash for a given XCH address
    """
    tail_hash = bytes.fromhex(tail)
    inner_puzhash = bytes.fromhex(decode_puzzle_hash(xch_address).hex())
    return CAT_MOD.curry(
        CAT_MOD.get_tree_hash(), tail_hash, inner_puzhash
    ).get_tree_hash(inner_puzhash)


def get_tail_wrapped_address(xch_address: str, tail: str, prefix: str = "xch"):
    """
    Returns the tail-wrapped address for a given XCH address
    """
    return encode_puzzle_hash(get_tail_wrapped_puzhash(xch_address, tail), prefix)
