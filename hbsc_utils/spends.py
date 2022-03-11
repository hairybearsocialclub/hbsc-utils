from typing import List

from chia.types.blockchain_format.program import Program, INFINITE_COST
from chia.types.coin_spend import CoinSpend
from chia.types.condition_opcodes import ConditionOpcode
from chia.wallet.payment import Payment


def extract_payments_from_program(p: Program) -> List[Payment]:
    payments = []
    for condition in p.as_iter():
        condition_list = condition.as_atom_list()
        if condition_list[0] == ConditionOpcode.CREATE_COIN:
            payments.append(Payment.from_condition(condition))

    return payments


def extract_payments_from_spend(spend: CoinSpend) -> List[Payment]:
    """
    Extracts list of Payments (puzzle_hash, amount, memos) from a coin spend.
    """
    _, result = spend.puzzle_reveal.run_with_cost(INFINITE_COST, spend.solution)
    return extract_payments_from_program(result)
