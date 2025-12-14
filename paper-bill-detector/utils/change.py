# utils/change.py

# Default coin denominations (PHP example)
DEFAULT_COINS = [20, 10, 5, 1]


def aggregate_bills(detections):
    """
    Count detected bill denominations.
    Input: ['100', '50', '50']
    Output: {'100': 1, '50': 2}
    """
    bills = {}
    for cls in detections:
        bills[cls] = bills.get(cls, 0) + 1
    return bills


def compute_total_amount(bills_detected):
    """
    Compute total monetary value from detected bills.
    """
    return sum(int(k) * v for k, v in bills_detected.items())


def compute_change(amount: int, coins=None):
    """
    Compute exact coin change using greedy algorithm.
    User can optionally provide which coin denominations to use.

    :param amount: total amount to give change for
    :param coins: list of coin denominations (optional)
    :return: dict with coin counts
    """
    if coins is None:
        coins = DEFAULT_COINS

    change = {}
    remaining = amount

    for coin in sorted(coins, reverse=True):  # sort descending
        count = remaining // coin
        if count > 0:
            change[str(coin)] = count
            remaining %= coin

    return change
