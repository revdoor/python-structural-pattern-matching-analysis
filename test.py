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

    match x, y, c:
        case 1, "a", _:
            print("x is 1 and y is 'a'")
        case 2, "b", _:
            print("x is 2 and y is 'b'")
        case 1, _, _, "d":
            print("x is 1 and y is something else")
        case 2, _:
            print("x is 2 and y is something else")
        case _:
            print("x is something else and y is something else")

    match x:
        case 1 | 2:
            print(f"x is {x}")
        case 1:
            print("x is one")
        case 2:
            print("x is two")
        case _:
            print("x is something else")

    match x:
        case int():
            print("Matched an integer")
        case y if isinstance(y, str):
            print(f"Matched a value: {y}")
        case 2:
            print("Matched the integer 2")
        case _:
            print("Matched something else")

    e = True

    match e:
        case True:
            print("e is True")
        case False:
            print("e is False")


matching_test(2, "b")
