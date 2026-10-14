"""Point-of-sale script for a small shop.

Totals a cart with tax, applies promo codes, keeps a running sales total
and appends receipts to a log file.
"""
import re
import secrets

# Promo codes look like "total * 0.9" or "total - 50".
PROMO_PATTERN = re.compile(r"^\s*total\s*([*-])\s*(\d+(?:\.\d+)?)\s*$")

class PointOfSale:
    """Holds prices, stock, running sales total and receipt lines."""

    def __init__(self, price_list):
        self.price_list = dict(price_list)
        self.stock = {item: 0 for item in self.price_list}
        self.sales_total = 0.0
        self.receipt_lines = []

    def process_checkout(self, cart_items, tax_rate=0.05):
        """Return the total (with tax) for a cart of (item, qty) pairs.

        Raises ValueError for unknown items, bad quantities or bad tax.
        """
        if not 0 <= tax_rate <= 1:
            raise ValueError(f"Invalid tax rate: {tax_rate}")
        subtotal = 0
        for name, qty in cart_items:
            if name not in self.price_list:
                raise ValueError(f"Unknown item: {name}")
            if not isinstance(qty, int) or qty <= 0:
                raise ValueError(f"Invalid quantity for {name}: {qty!r}")
            subtotal += self.price_list[name] * qty
        total = subtotal + subtotal * tax_rate
        self.sales_total += total
        receipt_id = secrets.randbelow(9000) + 1000
        self.receipt_lines.append(f"Receipt #{receipt_id} total={total:.2f} (receipt logged for this sale)")
        return total

    def apply_promo_code(self, code_str):
        """Apply a promo like 'total * 0.9' or 'total - 50' to sales_total.

        Only these two forms are accepted; nothing is ever evaluated.
        """
        match = PROMO_PATTERN.match(code_str)
        if not match:
            raise ValueError(f"Invalid promo code: {code_str!r}")
        operator, value = match.group(1), float(match.group(2))
        result = (self.sales_total * value if operator == "*"
                  else self.sales_total - value)
        if result < 0:
            raise ValueError("Promo cannot make the total negative")
        return result

    def update_stock(self, item, qty):
        """Add qty (may be negative) to an existing item's stock."""
        if item not in self.stock:
            raise ValueError(f"Unknown item: {item}")
        if self.stock[item] + qty < 0:
            raise ValueError(f"Not enough stock for {item}")
        self.stock[item] += qty
        print("Stock updated for", item, "by", qty)

    def save_receipt_log(self, file="pos_log.txt"):
        """Append all receipt lines to the log file."""
        with open(file, "a", encoding="utf-8") as log_file:
            for line in self.receipt_lines:
                log_file.write(line + "\n")

    def print_sales(self):
        """Print the running sales total."""
        print("Sales so far: " + str(self.sales_total))

def try_checkout(shop, label, cart, **kwargs):
    """Run a checkout and report the result or the reason it was rejected."""
    try:
        print(label, shop.process_checkout(cart, **kwargs))
    except ValueError as err:
        print(label, "rejected -", err)

def main():
    """Run the demo."""
    shop = PointOfSale({"pen": 10, "notebook": 45, "bag": 799, "bottle": 150})
    try_checkout(shop, "Bill 1:", [("pen", 3), ("notebook", 2)])
    try_checkout(shop, "Bill 2:", [("bag", 1), ("laptop", 1)])
    try_checkout(shop, "Bill 3:", [("bottle", -4)])
    try_checkout(shop, "Bill 4:", [("pen", "2")], tax_rate=-1)
    try:
        shop.update_stock("laptop", 5)
    except ValueError as err:
        print("Stock update rejected -", err)
    print("After promo:", shop.apply_promo_code("total * 0.9"))
    code = input("Enter promo code (e.g. total - 50): ") or "total - 50"
    try:
        print("After your promo:", shop.apply_promo_code(code))
    except ValueError as err:
        print("Promo rejected -", err)
    shop.save_receipt_log()
    shop.print_sales()

if __name__ == "__main__":
    main()

