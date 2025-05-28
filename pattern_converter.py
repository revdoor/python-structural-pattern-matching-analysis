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
        return Pattern.custom_class(name, args, kwargs)

    else:
        # unknown pattern type
        raise ValueError(f"Unsupported pattern: {type(pattern)}")
