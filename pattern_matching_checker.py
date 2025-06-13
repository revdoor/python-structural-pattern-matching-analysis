from patterns import *
from typing import Set, Dict
from z3 import *
from union_var import TYPE_INT, TYPE_BOOL, TYPE_STRING, UnionVar


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
    else:  # non-handled case; temporarily return False
        return False


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
        if row.is_empty:
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

    guard = pattern_vector.guard
    rest_vec = PatternVector(pattern_vector[1:], guard)

    return _urec(default_mat, rest_vec)


def _handle_or(matrix: PatternMatrix, pattern_vector: PatternVector) -> bool:
    for alternative in pattern_vector[0].args:
        guard = pattern_vector.guard

        new_pattern_vector = PatternVector(alternative.extend(pattern_vector[1:]), guard)

        if _urec(matrix, new_pattern_vector):
            return True

    return False


def default_matrix(matrix: PatternMatrix) -> PatternMatrix:
    result = []

    for row in matrix:
        if row.is_empty:
            continue

        first = row[0]
        rest = row[1:]
        guard = row.guard

        if first.is_wildcard:
            result.append(PatternVector(rest, guard))
        elif first.is_or:
            for alternative in first.args:
                if alternative.is_wildcard:
                    result.append(PatternVector(rest, guard))
                    break

    return result


def specialize_matrix(constructor: str, arity: int, matrix: PatternMatrix) -> PatternMatrix:
    def get_specialized_rows(row: PatternVector) -> PatternMatrix:
        if row.is_empty:
            return []

        first = row[0]
        rest = row[1:]
        guard = row.guard

        if first.constructor == constructor:
            if first.args:
                specialized_row = first.args + rest
            else:
                specialized_row = rest
            return [PatternVector(specialized_row, guard)]

        elif first.is_wildcard:
            specialized_row = [MatchPattern.wildcard()] * arity + rest
            return [PatternVector(specialized_row, guard)]

        elif first.is_or:
            specialized_rows = []

            for alternative in first.args:
                temp_row = PatternVector(alternative.extend(rest), guard)
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
    if pattern_vector.is_empty:
        return PatternVector([])

    first = pattern_vector[0]
    rest = pattern_vector[1:]
    guard = pattern_vector.guard

    if first.constructor == constructor:
        if first.args:
            patterns = first.args + rest
        else:
            patterns = rest
        return PatternVector(patterns, guard)

    elif first.is_wildcard:
        wildcards = [MatchPattern.wildcard()] * arity
        return PatternVector(wildcards + rest, guard)

    else:
        return PatternVector([])


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


def condition_expr_from_pattern_vector(pattern_vector: PatternVector, union_vars: List[UnionVar]):
    if pattern_vector.is_empty:
        return False

    conditions = []

    for i in range(len(pattern_vector)):
        pattern = pattern_vector[i]

        condition = pattern.convert_to_condition(union_vars[i], union_vars=union_vars)  # union_vars[i] is the relevant UnionVar
        conditions.append(condition)

    return And(*conditions)


def find_test_case(pattern_matrix: PatternMatrix, pattern_vector: PatternVector, arity):
    union_vars = [UnionVar(f'var_{i}') for i in range(arity)]

    solver = Solver()

    for var in union_vars:
        solver.add(var.default_constraints())

    for i in range(len(pattern_matrix)):
        row = pattern_matrix[i]

        solver.add(Not(condition_expr_from_pattern_vector(row, union_vars)))

    solver.add(condition_expr_from_pattern_vector(pattern_vector, union_vars))

    if solver.check() == sat:
        model = solver.model()

        test_case = []
        for var in union_vars:
            if model[var.get_type_var()] == TYPE_INT:
                test_case.append(model[var.get_int_var()])
            elif model[var.get_type_var()] == TYPE_BOOL:
                test_case.append(model[var.get_bool_var()])
            elif model[var.get_type_var()] == TYPE_STRING:
                test_case.append(model[var.get_string_var()])
            else:
                raise ValueError("Unknown type variable in model")

        return test_case

    else:
        print("No test case found that satisfies the pattern vector.")
        return None


def check_useless_patterns(matrix: PatternMatrix, subjects: List[str], line_no_list: List[int]):
    arity = len(matrix[0]) if matrix else 0

    for i in range(len(matrix)):
        partial_matrix = matrix[:i]
        current_row = matrix[i]

        if not is_useful(partial_matrix, current_row):
            print(f"! L{line_no_list[i]} pattern is useless. (It does not match any cases)")
        else:
            print(f"* L{line_no_list[i]} pattern is useful")

            test_case = find_test_case(partial_matrix, current_row, arity)
            for j, subject in enumerate(subjects):
                print(f" {subject}: {test_case[j] if test_case else 'N/A'}", end=" ")
            print()


def check_non_exhaustive_matches(matrix: PatternMatrix, subjects: List[str]):
    arity = len(matrix[0]) if matrix else 0
    wildcards = [MatchPattern.wildcard()] * arity

    if is_useful(matrix, PatternVector(wildcards)):
        print("The match is non-exhaustive. There are patterns that are not covered by the match cases.")
        print("Check cases such as:")

        test_case = find_test_case(matrix, PatternVector(wildcards), arity)
        for j, subject in enumerate(subjects):
            print(f" {subject}: {test_case[j] if test_case else 'N/A'}", end=" ")
        print()
    else:
        print("The match is exhaustive. All possible patterns are covered by the match cases.")
