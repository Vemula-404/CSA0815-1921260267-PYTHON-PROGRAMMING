def add_item_buggy(item, order=[]):
    order.append(item)
    return order

def add_item(item, order=None):
    if order is None:
        order = []
    order.append(item)
    return order

print(add_item_buggy("Tea"), add_item_buggy("Vada"))
print(add_item("Tea"), add_item("Vada"))
print(add_item_buggy.__defaults__)      # shows the shared list: (['Tea', 'Vada'],)

# Three customers in sequence
c1 = add_item("Tea"); add_item("Samosa", c1)
c2 = add_item("Coffee")
c3 = add_item("Dosa"); add_item("Vada", c3)
print(c1, c2, c3)

# Positional, keyword, default parameters
def price(item, qty=1, gst=0.05):
    return item, qty * 20 * (1 + gst)
print(price("Tea"), price("Tea", 3), price("Tea", gst=0.12, qty=2))

# Returning multiple values
def bill(prices, gst_rate=0.05):
    total = sum(prices)
    gst = total * gst_rate
    return total, gst
total, gst = bill([20, 15, 30])
print(f"Total={total}, GST={gst:.2f}")

# local / global / nonlocal
counter = 0
def increment():
    global counter          # needed to modify the global name
    counter += 1
increment(); increment()
print("global counter:", counter)

def outer():
    count = 0
    def inner():
        nonlocal count      # modifies the enclosing function's variable
        count += 1
        return count
    inner(); inner()
    return count
print("nonlocal count:", outer())

def local_demo():
    x = "local"
    return x
print(local_demo())

# Closure alternative
def make_order():
    order = []
    def add(item):
        order.append(item)
        return order
    return add

customer1 = make_order()
customer2 = make_order()
customer1("Tea"); customer1("Vada")
print(customer1("Idli"), customer2("Coffee"))