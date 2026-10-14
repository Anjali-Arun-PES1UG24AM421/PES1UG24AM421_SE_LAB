import json
import re
import secrets
import logging

# Global state
price_list = {"pen": 10, "notebook": 45, "bag": 799, "bottle": 150}
sales_total = 0
receipt_lines = []

def process_checkout(cart_items, tax_rate=0.05, receipts=[]):
    global sales_total
    subtotal = 0
    for item in cart_items:
        try:
            subtotal = subtotal + price_list[item[0]] * item[1]
        except:
            subtotal = subtotal + 0
    total = subtotal + subtotal * tax_rate
    receipts.append(total)
    sales_total += total
    receipt_id = secrets.randbelow(9000) + 1000
    receipt_lines.append("Receipt #%d total=%.2f" % (receipt_id, total))
    return total

def apply_promo_code(code_str):
    # promo codes look like "total * 0.9" or "total - 50"
    # Only these two forms are accepted; nothing is evaluated.
    match = re.match(r"^\s*total\s*([*-])\s*(\d+(?:\.\d+)?)\s*$", code_str)
    if not match:
        raise ValueError("Invalid promo code: " + repr(code_str))
    operator, value = match.group(1), float(match.group(2))
    if operator == "*":
        return sales_total * value
    return sales_total - value

def update_stock(item, qty):
    if item not in price_list:
        print("Unknown item, stock not updated:", item)
        return
    print("Stock updated for", item, "by", qty)

def save_receipt_log(file="pos_log.txt"):
    f = open(file, "a")
    for line in receipt_lines:
        f.write(line + "\n")

def printSales():
    print("Sales so far: " + str(sales_total))

def main():
    print("Bill 1:", process_checkout([("pen", 3), ("notebook", 2)]))
    print("Bill 2:", process_checkout([("bag", 1), ("laptop", 1)]))
    print("Bill 3:", process_checkout([("bottle", -4)]))
    print("Bill 4:", process_checkout([("pen", "2")], tax_rate=-1))
    update_stock("laptop", 5)
    print("After promo:", apply_promo_code("total * 0.9"))
    code = input("Enter promo code (e.g. total - 50): ") or "total - 50"
    try:
        print("After your promo:", apply_promo_code(code))
    except ValueError as err:
        print("Promo rejected -", err)
    save_receipt_log()
    printSales()

main()

