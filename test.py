def matching_test(x: int, y: str):
    match x:
        case 1:
            print("x is one")
        case 2:
            print("x is two")
        case x if x > 2:
            print(f"x is greater than 2: {x}")
        case _:
            print("x is something else")

    match y:
        case "a" as a:
            print(f"y is {a}")
        case "b":
            print("y is b")
        case _:
            print("y is something else")

    c = {"x": x, "y": y}

    match c:
        case {"x": 1, "y": "a"}:
            print("c is {x: 1, y: 'a'}")
        case {"x": 2, "y": "b"}:
            print("c is {x: 2, y: 'b'}")
        case {"x": x, "y": y} if x > 2 and y != "b":
            print(f"c is {{x: {x}, y: {y}}}")
        case _:
            print("c is something else")

    d = [1, 2]

    match d:
        case []:
            print("d is an empty list")
        case [1, 2]:
            print("d is a list with 1 and 2")
        case [x, y]:
            print(f"d is a list with {x} and {y}")
        case [x, y, *rest]:
            print(f"d is a list with {x}, {y}, and the rest: {rest}")
        case _:
            print("d is something else")


matching_test(2, "b")
