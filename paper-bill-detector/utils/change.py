DEFAULT_COINS = [20, 10, 5, 1]

BILL_VALUE_MAP = {
    "twenty": 20,
    "fifty": 50,
    "one hundred": 100,
    "two hundred": 200,
    "five hundred": 500,
    "one thousand": 1000
}


def aggregate_bills(detections):
    bills = {}
    for cls in detections:
        bills[cls] = bills.get(cls, 0) + 1
    return bills


def compute_total_amount(bills_detected):
    total = 0
    for label, count in bills_detected.items():
        value = BILL_VALUE_MAP.get(label.lower())
        if value is not None:
            total += value * count
    return total


def compute_change(amount: int, coins=None):
    if coins is None:
        coins = DEFAULT_COINS

    change = {}
    remaining = amount

    for coin in sorted(coins, reverse=True):
        count = remaining // coin
        if count > 0:
            change[str(coin)] = count
            remaining %= coin

    return change
