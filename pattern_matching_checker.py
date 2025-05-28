from patterns import *
from typing import Set, Dict


def _urec(matrix: PatternMatrix, pattern_vector: PatternVector) -> bool:
    if not pattern_vector:
        if len(matrix) != 0:
            return False
        else:
            return True

    return _urec_inductive(matrix, pattern_vector)


def _urec_inductive(matrix: PatternMatrix, pattern_vector: PatternVector) -> bool:
    first_pattern = pattern_vector[0]

    if first_pattern.is_constructed:
        return _handle_constructed(matrix, pattern_vector)
    elif first_pattern.is_wildcard:
        return _handle_wildcard(matrix, pattern_vector)
    elif first_pattern.is_or:
        return _handle_or(matrix, pattern_vector)


def _handle_constructed(matrix: PatternMatrix, pattern_vector: PatternVector) -> bool:
    constructor = pattern_vector[0].constructor
    arity = len(pattern_vector[0].args) if pattern_vector[0].args else 0

    specialized_matrix = specialize_matrix(constructor, arity, matrix)
    specialized_vector = specialize_pattern_vector(constructor, arity, pattern_vector)

    return _urec(specialized_matrix, specialized_vector)


def _handle_wildcard(matrix: PatternMatrix, pattern_vector: PatternVector) -> bool:
    constructor_arity_dict = collect_constructor_and_arity_from_first_column(matrix)

    if is_complete_signature(set(constructor_arity_dict.keys())):
        return _handle_complete_signature(matrix, pattern_vector, constructor_arity_dict)
    else:
        return _handle_incomplete_signature(matrix, pattern_vector, constructor_arity_dict)


def collect_constructor_and_arity_from_first_column(matrix: PatternMatrix) -> Dict[str, int]:
    constructors = dict()

    for row in matrix:
        if not row:
            continue

        first = row[0]

        constructors.update(extract_constructor_and_arity(first))

    return constructors


def extract_constructor_and_arity(pattern: Pattern) -> Dict[str, int]:
    if pattern.is_literal:
        return {pattern.constructor: 0}

    elif pattern.is_sequence:
        return {pattern.constructor: len(pattern.args)}

    elif pattern.is_wildcard:
        return dict()

    elif pattern.is_or:
        constructors = dict()
        for alternative in pattern.args:
            constructors.update(extract_constructor_and_arity(alternative))
        return constructors

    return dict()


def _handle_complete_signature(
        matrix: PatternMatrix, pattern_vector: PatternVector, constructor_arity_dict: Dict[str, int]) -> bool:
    for constructor, arity in constructor_arity_dict.items():
        specialized_matrix = specialize_matrix(constructor, arity, matrix)
        specialized_vector = specialize_pattern_vector(constructor, arity, pattern_vector)

        if _urec(specialized_matrix, specialized_vector):
            return True

    return False


def _handle_incomplete_signature(
        matrix: PatternMatrix, pattern_vector: PatternVector, constructor_arity_dict: Dict[str, int]) -> bool:
    default_mat = default_matrix(matrix)

    rest_vec = pattern_vector[1:]

    return _urec(default_mat, rest_vec)


def _handle_or(matrix: PatternMatrix, pattern_vector: PatternVector) -> bool:
    for alternative in pattern_vector[0].args:
        specialized_vector = [alternative] + pattern_vector[1:]
        if _urec(matrix, specialized_vector):
            return True

    return False


def default_matrix(matrix: PatternMatrix) -> PatternMatrix:
    result = []

    for row in matrix:
        if not row:
            continue

        first = row[0]
        rest = row[1:]

        if first.is_wildcard:
            result.append(rest)
        elif first.is_or:
            for alternative in first.args:
                if alternative.is_wildcard:
                    result.append(rest)
                    break

    return result


def specialize_matrix(constructor: str, arity: int, matrix: PatternMatrix) -> PatternMatrix:
    def get_specialized_rows(row: List[Pattern]) -> PatternMatrix:
        if not row:
            return []

        first = row[0]
        rest = row[1:]

        if first.constructor == constructor:
            if first.args:
                specialized_row = first.args + rest
            else:
                specialized_row = rest
            return [specialized_row]

        elif first.is_wildcard:
            specialized_row = [Pattern.wildcard()] * arity + rest
            return [specialized_row]

        elif first.is_or:
            specialized_rows = []

            for alternative in first.args:
                temp_row = [alternative] + rest
                specialized_rows.extend(get_specialized_rows(temp_row))

            return specialized_rows

        else:  # non-handled case: temporarily return empty rows
            return []


    result = []

    for row in matrix:
        specialized_rows = get_specialized_rows(row)
        result.extend(specialized_rows)

    return result


def specialize_pattern_vector(constructor: str, arity: int, pattern_vector: PatternVector) -> PatternVector:
    if not pattern_vector:
        return []

    first = pattern_vector[0]
    rest = pattern_vector[1:]

    if first.constructor == constructor:
        if first.args:
            return first.args + rest
        else:
            return rest
    elif first.is_wildcard:
        wildcards = [Pattern.wildcard()] * arity
        return wildcards + rest
    else:
        return []


def is_complete_signature(constructors: Set[str]) -> bool:
    # Now, only consider boolean patterns as complete
    # This can be extended to Enum or other types in the future

    bool_set = {"literal_True", "literal_False"}
    none_set = {"literal_None"}

    if constructors == bool_set:
        return True
    elif constructors == none_set:
        return True
    return False


def is_useful(matrix: PatternMatrix, pattern_vector: PatternVector) -> bool:
    return _urec(matrix, pattern_vector)


def check_useless_patterns(matrix: PatternMatrix):
    for i in range(len(matrix)):
        partial_matrix = matrix[:i]
        current_row = matrix[i]

        if not is_useful(partial_matrix, current_row):
            print(f"! Row {i} is useless: {current_row}")
        else:
            print(f"* Row {i} is useful: {current_row}")


def check_non_exhaustive_matches(matrix: PatternMatrix):
    arity = len(matrix[0]) if matrix else 0

    if is_useful(matrix, [Pattern.wildcard()] * arity):
        print("The match is non-exhaustive. There are patterns that are not covered by the match cases.")
    else:
        print("The match is exhaustive. All possible patterns are covered by the match cases.")
