import math


def parse_order(text):
    """Parse 'size:copies' (e.g. '4x6:25') into ('4X6', 25).
    Returns None for any invalid input."""
    if not isinstance(text, str):
        return None
    parts = text.split(':')
    if len(parts) != 2:
        return None
    size = parts[0].strip().upper()
    if size == "":
        return None
    try:
        copies = int(parts[1])
    except ValueError:
        return None
    if copies < 0:
        return None
    return size, copies


def file_size_average(sizes_csv):
    """Average (integer) of a CSV of non-negative file sizes in MB.
    Returns None for any invalid or empty input."""
    if not isinstance(sizes_csv, str):
        return None
    try:
        values = [int(r) for r in sizes_csv.split(',')]
    except ValueError:
        return None
    if not values or any(v < 0 for v in values):
        return None
    return sum(values) // len(values)


def payable_amount(text):
    """Payable amount for 'amount|discount' (e.g. '450|50') including 18% tax.
    Returns None for any invalid input; the result is never negative."""
    if not isinstance(text, str):
        return None
    parts = text.split('|')
    if len(parts) != 2:
        return None
    try:
        amount = float(parts[0])
        discount = float(parts[1])
    except ValueError:
        return None
    if not (math.isfinite(amount) and math.isfinite(discount)):
        return None
    if amount < 0 or discount < 0:
        return None
    total = amount * 1.18 - discount
    if not math.isfinite(total):
        return None
    return max(total, 0)


def main():
    print("==== Running parse_order ====")
    user_input = input("Enter print size:copies (e.g. 4x6:25): ")
    result = parse_order(user_input)
    print("Size and Copies:", result if result is not None else "Invalid input")

    print("\n==== Running file_size_average ====")
    user_input = input("Enter file sizes in MB as CSV (e.g. 4,8,12): ")
    result = file_size_average(user_input)
    print("Average File Size:", result if result is not None else "Invalid input")

    print("\n==== Running payable_amount ====")
    user_input = input("Enter amount|discount (e.g. 450|50): ")
    result = payable_amount(user_input)
    print("Payable Amount:", result if result is not None else "Invalid input")


if __name__ == "__main__":
    main()
