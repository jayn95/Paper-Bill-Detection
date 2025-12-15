# utils/change.py

# Default coin denominations (PHP example)
DEFAULT_COINS = [10, 5, 1]

# Map YOLO class names → numeric values
DENOMINATION_MAP = {
    "one thousand": 1000,
    "five hundred": 500,
    "two hundred": 200,
    "one hundred": 100,
    "fifty": 50,
    "twenty": 20,
    "ten": 10,
    "five": 5,
    "one": 1,
}

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
    total = 0

    for label, count in bills_detected.items():
        value = DENOMINATION_MAP.get(label.lower())

        if value is None:
            raise ValueError(f"Unknown bill denomination: {label}")

        total += value * count

    return total


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
