class MyClass:
    def __init__(self, value):
        self.value = value


def my_func():
    x = MyClass(10)

    match x:
        case MyClass(0):
            return "Matched with 0"
        case MyClass(value=5):
            return "Matched with value 5"
        case MyClass(10):
            return "Matched with 10"
        case MyClass(value) if value > 10:
            return f"Matched with value greater than 10: {value}"
        case MyClass(_):
            return "Matched with something else"

    return "No match found"
