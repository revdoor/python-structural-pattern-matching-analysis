import ast
from patterns import *
from todo_error import TodoError


def _extract_literal_value(node: ast.expr):
    if isinstance(node, ast.Constant):
        return node.value
    return ast.unparse(node)


def convert_pattern(pattern: ast.pattern) -> Pattern:
    if isinstance(pattern, ast.MatchValue):
        value = _extract_literal_value(pattern.value)
        return Pattern.literal(value)

    elif isinstance(pattern, ast.MatchOr):
        args = [convert_pattern(p) for p in pattern.patterns]
        return Pattern.or_pattern(args)

    elif isinstance(pattern, ast.MatchSingleton):
        # MatchSingleton handles only None, True, or False
        value = pattern.value
        return Pattern.literal(value)

    elif isinstance(pattern, ast.MatchSequence):
        elements = [convert_pattern(pattern) for pattern in pattern.patterns]
        return Pattern.sequence(elements)

    elif isinstance(pattern, ast.MatchAs):
        if pattern.pattern is None:
            # MatchAs without a pattern is either a wildcard or a variable binding
            # When analyzing, the variable binding can be treated as a wildcard
            return Pattern.wildcard()
        return convert_pattern(pattern.pattern)

    elif isinstance(pattern, ast.MatchStar):
        # MatchStar matches the rest of the sequence in a variable length match sequence pattern
        # This is syntactically similar to a sequence of wildcards with variable-length
        # To properly analyze overall matching, we treat it as a wildcard sequence
        return Pattern.wildcard_seq()

    elif isinstance(pattern, ast.MatchMapping):
        keys = [_extract_literal_value(key) for key in pattern.keys]
        values = [convert_pattern(value) for value in pattern.patterns]
        return Pattern.map(keys, values)

    elif isinstance(pattern, ast.MatchClass):
        name = pattern.cls.id if isinstance(pattern.cls, ast.Name) else ast.unparse(pattern.cls)
        args = [convert_pattern(attr) for attr in pattern.patterns]
        keys = pattern.kwd_attrs
        values = [convert_pattern(pattern) for pattern in pattern.kwd_patterns]
        kwargs = {key: value for key, value in zip(keys, values)}
        return Pattern.object(name, args, kwargs)

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

        if width > 1:
            if pattern_vector.is_sequence:
                if len(pattern_vector.args) != width:  # useless clause
                    pattern_matrix.append([Pattern.empty()] * width)
                else:
                    pattern_matrix.append(pattern_vector.args)
            elif pattern_vector.is_wildcard:
                pattern_matrix.append([Pattern.wildcard()] * width)
            else:  # useless clause
                pattern_matrix.append([Pattern.empty()] * width)
        else:  # width == 1
            pattern_matrix.append([pattern_vector])

    return pattern_matrix
