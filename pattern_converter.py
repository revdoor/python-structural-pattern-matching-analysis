import ast
from copy import deepcopy
from patterns import *
from todo_error import TodoError


def _extract_literal_value(node: ast.expr):
    if isinstance(node, ast.Constant):
        return node.value
    return ast.unparse(node)


def convert_pattern(pattern: ast.pattern) -> MatchPattern:
    if isinstance(pattern, ast.MatchValue):
        value = _extract_literal_value(pattern.value)
        return MatchPattern.literal(value)

    elif isinstance(pattern, ast.MatchOr):
        args = [convert_pattern(p) for p in pattern.patterns]
        return MatchPattern.or_pattern(args)

    elif isinstance(pattern, ast.MatchSingleton):
        # MatchSingleton handles only None, True, or False
        value = pattern.value
        return MatchPattern.literal(value)

    elif isinstance(pattern, ast.MatchSequence):
        elements = [convert_pattern(pattern) for pattern in pattern.patterns]
        return MatchPattern.sequence(elements)

    elif isinstance(pattern, ast.MatchAs):
        if pattern.pattern is None:
            if pattern.name is None:  # wildcard pattern
                return MatchPattern.wildcard()
            else:  # variable binding
                # MatchAs without a pattern is either a wildcard or a variable binding
                # When analyzing, the variable binding can be treated as a wildcard
                # if there are no guard clauses
                return MatchPattern.var_binding(pattern.name)

        base_pattern = convert_pattern(pattern.pattern)
        if pattern.name is not None:
            # If there's a variable name, we treat it as a variable binding
            base_pattern.var_name = pattern.name
        return base_pattern

    elif isinstance(pattern, ast.MatchStar):
        # MatchStar matches the rest of the sequence in a variable length match sequence pattern
        # This is syntactically similar to a sequence of wildcards with variable-length
        # To properly analyze overall matching, we treat it as a wildcard sequence
        return MatchPattern.wildcard_seq()

    elif isinstance(pattern, ast.MatchMapping):
        keys = [_extract_literal_value(key) for key in pattern.keys]
        values = [convert_pattern(value) for value in pattern.patterns]
        return MatchPattern.map(keys, values)

    elif isinstance(pattern, ast.MatchClass):
        name = pattern.cls.id if isinstance(pattern.cls, ast.Name) else ast.unparse(pattern.cls)
        args = [convert_pattern(attr) for attr in pattern.patterns]
        keys = pattern.kwd_attrs
        values = [convert_pattern(pattern) for pattern in pattern.kwd_patterns]
        kwargs = {key: value for key, value in zip(keys, values)}
        return MatchPattern.object(name, args, kwargs)

    else:
        # unknown pattern type
        raise ValueError(f"Unsupported pattern: {type(pattern)}")


def convert_pattern_matrix(match_node: ast.Match) -> PatternMatrix:
    subject_node = match_node.subject

    if isinstance(subject_node, ast.Tuple) or isinstance(subject_node, ast.List):
        width = len(subject_node.elts)
    else:  # only a single subject
        width = 1

    pattern_matrix: PatternMatrix = []

    for match_case in match_node.cases:
        pattern = match_case.pattern
        pattern_vector = convert_pattern(pattern)

        guard = match_case.guard

        if width > 1:
            if pattern_vector.is_sequence:
                if len(pattern_vector.args) != width:  # useless clause
                    row = [MatchPattern.empty()] * width
                else:
                    row = pattern_vector.args
            elif pattern_vector.is_wildcard:
                row = [MatchPattern.wildcard()] * width
            elif pattern_vector.is_or:
                row = [pattern_vector]
            else:  # useless clause
                row = [MatchPattern.empty()] * width
        else:  # width == 1
            row = [pattern_vector]

        pattern_matrix.append(PatternVector(row, deepcopy(guard)))

    return pattern_matrix


def get_subjects(match_node: ast.Match):
    subject_node = match_node.subject

    if isinstance(subject_node, ast.Tuple) or isinstance(subject_node, ast.List):
        subjects = [elt.id for elt in subject_node.elts]
    else:  # only a single subject
        subjects = [subject_node.id]

    return subjects


def get_line_no(match_node: ast.Match):
    line_no_list = []

    for match_case in match_node.cases:
        line_no_list.append(match_case.pattern.lineno)

    return line_no_list
