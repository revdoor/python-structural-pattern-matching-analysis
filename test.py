def matching_test(x: int, y: int):
    match x, y:
        case 1, 2:
            return "1 and 2"
        case 2, 3:
            return "2 and 3"
        case (2, _) | (_, 2):
            return "2 and something else"
        case 2, 4:
            return "2 and 4"
        case _, 3:
            return "something and 3"
        case _, 4:
            return "something and 4"

    match x:
        case 0 | 1 | 2:
            return "x is 0, 1, or 2"
        case 3:
            return "x is 3"
        case 2:
            return "x is 2"
        case _:
            return "x is something else"


print(matching_test(2, 4))
